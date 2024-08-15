import base64
from picamera2 import Picamera2
from yolo_manager import YoloDetectorWrapper
from utils import SimpleFPS, draw_fps, draw_annotation
import argparse
import time
from flask import Flask
import grovepi
import math
import time
from paho.mqtt import client as mqtt_client
from config import mqtt_config, logger
import json
from flask_mqtt import Mqtt

# Connect the Grove Temperature & Humidity Sensor Pro to digital port D4
# This example uses the blue colored sensor.
# SIG,NC,VCC,GND
sensor = 4  # The Sensor goes on digital port 4.

# temp_humidity_sensor_type
# Grove Base Kit comes with the blue sensor.
blue = 0  # The Blue colored sensor.
white = 1  # The White colored sensor.

is_temperature_limit = True
is_humidity_limit = True

# Connect to the MQTT
mqtt_config = mqtt_config['mqtt2']
broker = mqtt_config['broker']
port = mqtt_config['port']
topic = mqtt_config['topic']
client_id = mqtt_config['client_id']
username = mqtt_config['username']
password = mqtt_config['password']
qos = mqtt_config['qos']

parser = argparse.ArgumentParser()
parser.add_argument("--model", default="./model/best.pt")
parser.add_argument('--camera_test', action=argparse.BooleanOptionalAction)
parser.add_argument('--debug', action=argparse.BooleanOptionalAction)

args = parser.parse_args()

# 创建应用实例
app = Flask(__name__)
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


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc: int) -> None:
    logger.info(f'Connected with result code {rc}')
    topic1 = app.config['MQTT_TOPIC']
    mqtt.subscribe(topic1)  # Replace with your MQTT topic


@mqtt.on_message()
def handle_message(client, userdata, message) -> None:
    logger.info(f'Received message: {message.payload.decode()} on topic {message.topic}')


@app.route('/detect_disease', methods=['GET'])
def predict():
    # capture from webcam
    logger.info("Start predict")
    yolo_detector = YoloDetectorWrapper(args.model)
    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"},
                                                      raw={"size": (640, 480)})
    picam2.configure(camera_config)
    picam2.start()

    fps_util = SimpleFPS()

    frame = picam2.capture_array()
    results = yolo_detector.predict(frame)
    times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    data = {
    }
    if len(results[0]) > 0:
        logger.info("Detected Disease")
        base64_bytes = base64.b64encode(frame)
        base64_message = base64_bytes.decode()
        result = results[0].tojson()
        data["status"] = 200
        data["results"] = result
        data["Datetime"] = times
        data["img"] = base64_message
        logger.info("Predicted Diesease: ", data)
        message = json.dumps(data)
        mqtt.publish(app.config['MQTT_TOPIC'], message)
        time.sleep(2)
        return json.dumps(data)
        # fps, is_updated = fps_util.get_fps()
        # if is_updated:
        #     print(fps)
    else:
        data["status"] = 400
        data["response"] = "No Disease"
        return json.dumps(data)


def predict_start():
    app.run(debug=True)

