# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/4/28 14:41
# @Author : Lovecraftzhou
# @Site :
import base64
import time

# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/4/9 20:28
# @Author : Lovecraftzhou
# @Site :
import cv2
import json
import os
from PIL import Image, ImageDraw
import numpy as np
import redis
from paho.mqtt import client as mqtt_client
from config import mqtt_config, logger, con_config
from flask_mqtt import Mqtt
from flask import Flask
# Connect to the MQTT
mqtt_config = mqtt_config['mqtt2']
broker = mqtt_config['broker']
port = mqtt_config['port']
topic = mqtt_config['topic']
client_id = mqtt_config['client_id']
username = mqtt_config['username']
password = mqtt_config['password']
qos = mqtt_config['qos']
app = Flask(__name__)
# redis
redis_data = con_config['Redis']
r_host = redis_data['host']
r_port = redis_data['port']
r_db = redis_data['db']
try:
    r = redis.Redis(host=r_host, port=r_port, db=r_db)
    logger.success("Redis connection Successful!")
except ConnectionError as e:
    logger.error(f"Redis connection error: {e}")

# Get the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_path, "image")

# MQTT Configuration
app.config['MQTT_BROKER_URL'] = broker  # MQTT Broker URL
app.config['MQTT_BROKER_PORT'] = port  # MQTT Broker Port
app.config['MQTT_USERNAME'] = username  # MQTT Username
app.config['MQTT_PASSWORD'] = password  # MQTT Password
app.config['MQTT_TOPIC'] = topic  # MQTT Topic
app.config['MQTT_KEEPALIVE'] = 60  # MQTT KeepAlive Interval
app.config['MQTT_RECONNECT_DELAY'] = 3  # MQTT Reconnect Interval
app.config['MQTT_CLIENT_ID'] = client_id
app.config['MQTT_TLS_ENABLED'] = True
# Load DigiCert Global Root G2, which is used by EMQX Public Broker: broker.emqx.io
app.config['MQTT_TLS_CA_CERTS'] = "./config/server-ca.crt"
mqtt = Mqtt()


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.tls_set(ca_certs='config/server-ca.crt')
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        message = json.loads(msg.payload.decode())
        image_base64(message)
        print(message)
        # redis_write(message)
        logger.info("Receive Data")

    client.subscribe(topic)
    client.on_message = on_message


def redis_write(json_dict):
    try:
        # with open(json_dict, 'r') as f1:
        #     new_data = json.loads(f1.read())
        new_data = json_dict
        for col_name in new_data:
            r.hset(new_data['Datetime'], col_name, new_data[col_name])
        hash_list = r.keys('*')
        # for key in hash_list:
        #     hash_value = r.hgetall(key)
        #     print(str(hash_value[b'Datetime'], 'utf-8'))
        print("Redis Writing Successfully")

    except Exception as error:
        logger.error(f"write_redis Error while writing to redis {error}")


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


def image_base64(data):
    result = data["results"]
    print(result)
    image_b64 = data["img"]  # 获取dict中'img'标签的数据
    image_decode = base64.b64decode(image_b64)  # 进行base64解码工作 base64->数组
    # nparr = np.fromstring(image_decode, np.uint8)  # fromstring实现了字符串到Ascii码的转换
    # img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # 将 nparr 数据转换(解码)成图像格式
    # cv2.imwrite('test.jpg', img_np)

    # 将二进制数据转换成numpy数组
    np_data = np.frombuffer(image_decode, np.uint8)

    # 读取图片并进行解码
    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

    for res in result:
        name = res["name"]
        conf = res["confidence"]
        box = res["box"]
        xmin = box["x1"]
        ymin = box["y1"]
        xmax = box["x2"]
        ymax = box["y2"]
        start_point = (int(xmin), int(ymin))
        end_point = (int(xmax), int(ymax))
        color = (0, 255, 0)  # 绿色框
        thickness = 2
        cv2.rectangle(img, start_point, end_point, color, thickness)

        # 获取类别名称（确保你有类别的名称列表，如classes=['person', 'bicycle', ...]）
        label = f'{name}: {conf:.2f}'

        # 在框的顶部添加类别名称和置信度
        cv2.putText(img, label, (int(xmin), int(ymin - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 0)

    times = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    img_name = "{0}.jpeg".format(times)
    # save_path = os.path.join(image_path, img_name)
    print(img_name)
    cv2.imwrite(f'image/{img_name}', img)
    str = convert_image_to_base64(img)



def convert_image_to_base64(img):
    # 将图像编码为JPEG格式的字节流
    _, buffer = cv2.imencode('.jpg', img)

    # 将字节流编码为Base64字符串
    img_base64 = base64.b64encode(buffer)

    # 将Base64字节对象解码为UTF-8字符串
    img_base64_string = img_base64.decode('utf-8')

    # 添加数据类型前缀以在HTML中使用
    return img_base64_string


def Test():
    with open("data/result.json", "r") as f:
        data = json.load(f)
    # print(data)
    result = data["results"]
    print(result)
    image_b64 = data["img"]  # 获取dict中'img'标签的数据
    image_decode = base64.b64decode(image_b64)  # 进行base64解码工作 base64->数组
    # nparr = np.fromstring(image_decode, np.uint8)  # fromstring实现了字符串到Ascii码的转换
    # img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # 将 nparr 数据转换(解码)成图像格式
    # cv2.imwrite('test.jpg', img_np)

    # 将二进制数据转换成numpy数组
    np_data = np.frombuffer(image_decode, np.uint8)

    # 读取图片并进行解码
    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

    for r in result:
        name = r["name"]
        conf = r["confidence"]
        box = r["box"]
        xmin = box["x1"]
        ymin = box["y1"]
        xmax = box["x2"]
        ymax = box["y2"]
        start_point = (int(xmin), int(ymin))
        end_point = (int(xmax), int(ymax))
        color = (0, 255, 0)  # 绿色框
        thickness = 2
        cv2.rectangle(img, start_point, end_point, color, thickness)

        # 获取类别名称（确保你有类别的名称列表，如classes=['person', 'bicycle', ...]）
        label = f'{name}: {conf:.2f}'

        # 在框的顶部添加类别名称和置信度
        cv2.putText(img, label, (int(xmin), int(ymin - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 0)

        # cv2.imwrite('test.jpeg', img)

    times = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    img_name = "{0}.jpeg".format(times)
    # save_path = os.path.join(image_path, img_name)
    print(img_name)
    cv2.imwrite(f'image/{img_name}', img)
    str = convert_image_to_base64(img)
    print(str)
    # cv2.namedWindow('Image', cv2.WINDOW_FREERATIO)
    # cv2.imshow('Image', img)
    # cv2.waitKey(0)  # 等待按键按下
    # cv2.destroyAllWindows()  # 销毁所有窗口


if __name__ == '__main__':
    # run()
    Test()
