# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/4/9 20:28
# @Author : Lovecraftzhou
# @Site :
import json

from paho.mqtt import client as mqtt_client
from config import mqtt_config, logger

# Connect to the MQTT
mqtt_config = mqtt_config['mqtt']
broker = mqtt_config['broker']
port = mqtt_config['port']
topic = mqtt_config['topic']
client_id = mqtt_config['client_id']
username = mqtt_config['username']
password = mqtt_config['password']
qos = mqtt_config['qos']


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.tls_set(ca_certs='./server-ca.crt')
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        message = json.loads(msg.payload.decode())
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        logger.info("Receive Data")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
