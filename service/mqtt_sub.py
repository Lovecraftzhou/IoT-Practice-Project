# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/4/9 20:28
# @Author : Lovecraftzhou
# @Site :

import json
import os

import redis
from paho.mqtt import client as mqtt_client
from config import mqtt_config, logger, con_config

# Connect to the MQTT
mqtt_config = mqtt_config['mqtt']
broker = mqtt_config['broker']
port = mqtt_config['port']
topic = mqtt_config['topic']
client_id = mqtt_config['client_id']
username = mqtt_config['username']
password = mqtt_config['password']
qos = mqtt_config['qos']

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
        redis_write(message)
        temperature = message.get('temperature')
        humidity = message.get('humidity')

        # 打印解析后的数据
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
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


if __name__ == '__main__':
    run()
