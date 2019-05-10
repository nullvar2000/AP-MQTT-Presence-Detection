#!/usr/bin/python

import subprocess
import re
import paho.mqtt.client as mqtt

DEVICE_ID = "wifi-ap"

MQTT_BROKER = "broker"
MQTT_PORT = 1883
MQTT_USERNAME = "user"
MQTT_PASSWORD = "password"
MQTT_BASE_TOPIC = "home/devices/<MAC>/presence"
MQTT_AVAIL_TOPIC = "home/" + DEVICE_ID + "/availability"
MQTT_HOME_PAYLOAD = "home"
MQTT_AWAY_PAYLOAD = "not_home"

def on_connect(client, userdata, flags, rc):
    mqttc.publish(MQTT_AVAIL_TOPIC, "online")

def on_disconnect(client, userdata, rc):
    mqttc.publish(MQTT_AVAIL_TOPIC, "offline")

mqttc = mqtt.Client(DEVICE_ID)

if MQTT_USERNAME and MQTT_PASSWORD:
    mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

mqttc.will_set(MQTT_AVAIL_TOPIC, "offline")
mqttc.reconnect_delay_set(5, 120)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect

mqttc.connect(MQTT_BROKER, MQTT_PORT)
mqttc.loop_start()

cmd = ['iw', 'event']

events = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
event = ""

for character in iter(lambda: events.stdout.read(1), ''):

    if character != '\n':
        event += character
    else:
        match = re.match(r'.+: (.+) station (.+)', event, re.I|re.S)

        if match:
            action = MQTT_HOME_PAYLOAD if match.group(1) == "new" else MQTT_AWAY_PAYLOAD
            mac = match.group(2)

            mqttc.publish(MQTT_BASE_TOPIC.replace("<MAC>", mac), action)

        event = ""

