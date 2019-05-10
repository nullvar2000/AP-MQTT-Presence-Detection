# AP-MQTT-Presence-Detection

This was written to in openWRT, but should work in any Linux based WIFI access point.

# Requirements

This script requires python and the paho-mqtt library. The paho-mqtt library can be easily installed with pip.

# openWRT installation

Install requirements:

opkg update
opkg install python-light
opkg install python-pip
pip install paho-mqtt

Copy python script:

opkg install libustream-mbedtls
mkdir -p /usr/local/bin
wget https://github.com/nullvar2000/AP-MQTT-Presence-Detection/blob/master/presence.py -P /usr/local/bin/

To run the python script as a service:

opkg install coreutils-nohup

Add the following line to /etc/rc.local before the "exit 0" line:

nohup /usr/local/bin/presence.py &

# Thanks

Thanks to Chen A. at https://stackoverflow.com/questions/46245250/subprocess-with-watch-command for the subprocess example.