# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/4/9 21:51
# @Author : Lovecraftzhou
# @Site :


import grovepi
import math
import time
from paho.mqtt import client as mqtt_client
from config import mqtt_config, logger
import json
import grovepi

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
mqtt_config = mqtt_config['mqtt']
broker = mqtt_config['broker']
port = mqtt_config['port']
topic = mqtt_config['topic']
client_id = mqtt_config['client_id']
username = mqtt_config['username']
password = mqtt_config['password']
qos = mqtt_config['qos']


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
        else:
            logger.info("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.tls_set(ca_certs='./config/server-ca.crt')
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish_sensor_data(client):
    try:
        while True:
            try:
                # This example uses the blue colored sensor.
                # The first parameter is the port, the second parameter is the type of sensor.
                [temp, humidity] = grovepi.dht(sensor, blue)
                times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                if math.isnan(temp) == False and math.isnan(humidity) == False:
                    data = {
                        "Temperature": round(temp, 1),
                        "Humidity": round(humidity, 1),
                        "Datetime": times
                    }
                    logger.info("Datatime:%s | temp = %.02f C humidity =%.02f%%" % (str(times), temp, humidity))
                    message = json.dumps(data)
                    client.publish(topic, message, qos=qos)
                    time.sleep(2)
            except IOError:
                print("Failed to retrieve data from humidity sensor")
    except KeyboardInterrupt:
        print("Terminating...")
        client.disconnect()


def run():
    client = connect_mqtt()
    publish_sensor_data(client)
    client.loop_start()


if __name__ == '__main__':
    run()
