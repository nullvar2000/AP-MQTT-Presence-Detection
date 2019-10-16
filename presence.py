#!/usr/bin/python

import subprocess
import time
from threading import Thread
import re
import paho.mqtt.client as mqtt 

REPORT_INTERVAL_MINUTES = 5

DEVICE_ID = "router"

MQTT_BROKER = "broker"
MQTT_PORT = 1883
MQTT_USERNAME = "username"
MQTT_PASSWORD = "password"
MQTT_BASE_TOPIC = "home/" + DEVICE_ID + "/devices/<MAC>/presence"
MQTT_AVAIL_TOPIC = "home/" + DEVICE_ID + "/availability"
MQTT_HOME_PAYLOAD = "home"
MQTT_AWAY_PAYLOAD = "not_home"

def on_connect(client, userdata, flags, rc):
        print "Connected to MQTT server"
        global isConnected
        isConnected = True
        mqttc.publish(MQTT_AVAIL_TOPIC, "online", 0, True)

def on_disconnect(client, userdata, rc):
        print "Lost connection to MQTT server"
        global isConnected
        isConnected = False
        mqttc.publish(MQTT_AVAIL_TOPIC, "offline",   0, True)

mqttc = mqtt.Client(DEVICE_ID)
isConnected = False

if MQTT_USERNAME and MQTT_PASSWORD:
        mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

mqttc.will_set(MQTT_AVAIL_TOPIC, "offline")
mqttc.reconnect_delay_set(5, 120)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect

mqttc.connect(MQTT_BROKER, MQTT_PORT)
mqttc.loop_start()

class ReportEvents(Thread):
        def __init__(self):
                Thread.__init__(self)

        def run(self):
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

                                        if isConnected:
                                            mqttc.publish(MQTT_BASE_TOPIC.replace("<MAC>", mac), action)
                                        print('Event: ' + MQTT_BASE_TOPIC.replace("<MAC>", mac) + " " + action)

                                event = ""

class ReportConnections(Thread):
        def __init__(self):
                Thread.__init__(self)

        def run(self):
                cmd = ["iw", "dev"]
                ifaceData = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                ifaces = []
                
                for line in ifaceData.stdout.readlines():
                        match = re.match(r'\s+Interface\s+(.+)?\s+', line, re.I|re.S)

                        if match:
                            ifaces.append(match.group(1))

                while(1):
                        for iface in ifaces:
                                cmd = ["iw", "dev", iface, "station", "dump"]
                                connectionData = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                                for line in connectionData.stdout.readlines():
                                        match = re.match(r'^Station (.+) \(', line, re.I|re.S)

                                        if match:
                                                mac = match.group(1)
                                                if isConnected:
                                                    mqttc.publish(MQTT_BASE_TOPIC.replace("<MAC>", mac), MQTT_HOME_PAYLOAD)
                                                print('Report: ' + MQTT_BASE_TOPIC.replace("<MAC>", mac) + " " + MQTT_HOME_PAYLOAD)
                                                
                                retval = connectionData.wait()

                        time.sleep(REPORT_INTERVAL_MINUTES * 60)

reportEvents = ReportEvents()
reportConnections = ReportConnections()

reportEvents.start()
reportConnections.start()
