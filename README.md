| PayPal |
|-------|
|  [![donate](https://img.shields.io/badge/donate-PayPal-blue.svg)](https://www.paypal.me/rpieasy) |
If you like this project, or you wants to support the development, you can do that the links above. Or simply send me a Shelly device, that is not already supported, but you wish. :)

# ShellyMQTT - Domoticz Python Plugin
Python plugin for Shelly relay devices using MQTT protocol

MQTT parts based on heavily on the [zigbee2mqtt] project (https://github.com/stas-demydiuk/domoticz-zigbee2mqtt-plugin) 
big thanks for it!

## Prerequisites

Tested and works with Domoticz v4.x.

If you do not have a working Python >3.4 installation, please install it first! ( https://www.domoticz.com/wiki/Using_Python_plugins )

Setup and run MQTT broker and an MQTT capable Shelly device. (http://shelly-api-docs.shelly.cloud/#mqtt-support-beta)

## Installation

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/enesbcs/Shelly_MQTT.git
```
2. Restart domoticz
3. Go to "Hardware" page and add new item with type "ShellyMQTT"
4. Set your MQTT server address and port to plugin settings

Once plugin receive any MQTT message from Shelly it will try to create appropriate device.

## Plugin update

Warning: if you use this method, Domoticz may duplicate devices after it! Download only plugin.py if you have a lot of shellies and do not want to risk it!

1. Stop domoticz
2. Go to plugin folder and pull new version
```
cd domoticz/plugins/Shelly_MQTT
git pull
```
3. Start domoticz

## Supported devices

Tested and working with:
 - Shelly 1 Open Source (relay)
 - Shelly Plug (relay and power consumption reporting)
 - Shelly2 Switch (relay and roller shutter mode, positioning)
 - Shelly4 Pro (relay and power consumption reporting)
 - Shelly H&T
