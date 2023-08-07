[![Code size](https://img.shields.io/github/languages/code-size/enesbcs/shelly_mqtt)]() [![Last commit](https://img.shields.io/github/last-commit/enesbcs/shelly_mqtt)]()

# This plugin is free and open source, you can use forever and any purpose you like. But further improvement is stopped.
# The new script which adds Shelly devices to Domoticz MQTT Autodiscovery hardware is published at https://github.com/enesbcs/shellyteacher4domo and that is currently under development.

# ShellyMQTT - Domoticz Python Plugin
Python plugin for Shelly relay devices using MQTT protocol

MQTT parts based on heavily on the [zigbee2mqtt] project (https://github.com/stas-demydiuk/domoticz-zigbee2mqtt-plugin) 
big thanks for it!

## Prerequisites

Tested and works with Domoticz v4.x.

If you do not have a working Python >=3.5 installation, please install it first! ( https://www.domoticz.com/wiki/Using_Python_plugins )
(if Shelly_MQTT does not appear in HW list after installation, read again the above article!)

Setup and run MQTT broker and an MQTT capable Shelly device. (http://shelly-api-docs.shelly.cloud/#mqtt-support-beta)
If you do not have an MQTT server yet, install Mosquitto for example:
http://mosquitto.org/blog/2013/01/mosquitto-debian-repository/

!!! Please, DO NOT CHECK "Use custom MQTT prefix" on your device settings page if you want to use this plugin as this will render device detection unusable !!!

!!! For Shelly Plus HT, please prefix the MQTT topic with `shellies/` on your device settings page to make it send on the same topic as other devices !!!

## Installation

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/enesbcs/Shelly_MQTT.git
```
2. Restart domoticz
3. Go to "Hardware" page and add new item with type "ShellyMQTT"
4. Set your MQTT server address and port to plugin settings
5. Remember to allow new devices discovery in Domoticz settings

Once plugin receive any MQTT message from Shelly it will try to create appropriate device.

## Plugin install&update with plugin manager

I suggest to use a plugin manager for easy updates through Domoticz GUI:
https://github.com/stas-demydiuk/domoticz-plugins-manager

## Plugin manual update

Warning: if you use this method, Domoticz may duplicate devices after it!

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
 - Shelly 1PM (relay)*
 - Shelly Plug (relay)*
 - Shelly Plug S (relay)*
 - Shelly2 and 2.5 Switch (relay and roller shutter mode, positioning)
 - Shelly4 Pro (relay)*
 - Shelly H&T
 - Shelly RGBW2
 - Shelly Flood
 - Shelly Door and Window sensor
 - Shelly 2LED
 - Shelly Dimmer/Shelly Dimmer2
 - Shelly Bulb RGBW
 - Shelly EM/3EM
 - Shelly Button1
 - Shelly Door Window 2
 - Shelly i3
 - Shelly Bulb Duo
 - Shelly UNI
 - Shelly 1L (relay)
 - Shelly Gas
 - Shelly Motion
 - Shelly Plus H&T (by setting MQTT prefix to `shellies`)

*Power consumption can be enabled in the plugin settings page manually, it's an optional feature without any further support

**I would like to thank [Allterco Robotics](https://allterco.com/en/Shelly) for providing me with samples of Shelly Plug/Shelly2/Shelly4/Shelly RGBW2/Shelly Dimmer2/Shelly Bulb Duo/Shelly i3/Shelly Motion to support the development of this plugin.**
