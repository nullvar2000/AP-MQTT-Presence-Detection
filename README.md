# AP-MQTT-Presence-Detection

This was written to in openWRT, but should work in any Linux based WIFI access point.

# Requirements

This script requires python and the paho-mqtt library. The paho-mqtt library can be easily installed with pip.

# openWRT installation

Install requirements:

opkg update<br />
opkg install python-light<br />
opkg install python-pip<br />
pip install paho-mqtt

Copy python script:

opkg install libustream-mbedtls<br />
mkdir -p /usr/local/bin<br />
wget https://github.com/nullvar2000/AP-MQTT-Presence-Detection/blob/master/presence.py -P /usr/local/bin/

To run the python script as a service:

opkg install coreutils-nohup

Add the following line to /etc/rc.local before the "exit 0" line:

nohup /usr/local/bin/presence.py &

# Home Assistant Setup

I set this up in Home Assistant, but it should be able to work with any MQTT compatible systems. To use this script with Home Assistant, add the following to your configuration.yaml file. Simply replace the mac addresses with the correct ones from the devices to be tracked and add/remove devices as needed.

binary_sensor:<br />
  - platform: mqtt<br />
    name: "Wifi AP Presence Detection"<br />
    state_topic: 'home/presense_detection/wifi-ap/availability'<br />
    payload_on: 'online'<br />
    payload_off: 'offline'<br />
    device_class: connectivity<br />
    
device_tracker:<br />
  - platform: mqtt<br />
    devices:<br />
      Harry: 'home/devices/01:23:45:67:89:ab/presence'<br />
      Sally: 'home/devices/01:23:45:67:89:ac/presence'

# Thanks

Thanks to Chen A. at https://stackoverflow.com/questions/46245250/subprocess-with-watch-command for the subprocess example.
