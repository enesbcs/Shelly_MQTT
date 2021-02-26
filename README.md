# To support the development you can:
- Buy a [coffee](https://ko-fi.com/I3I514LLW)
- Contribute to any of my [Wishlist items](https://www.wishlist.com/wishlists_/alexander-nagy/dwGnV/)
- Be a patron at [Patreon](https://www.patreon.com/enesbcs)
- Add Python code by [Pull Request](https://github.com/enesbcs/rpieasy/pulls)

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

**I can only support devices that i have. Thank you for your understanding.**

*Power consumption can be enabled in the plugin settings page manually, it's an optional feature without any further support

**I would like to thank [Allterco Robotics](https://allterco.com/en/Shelly) for providing me with samples of Shelly Plug/Shelly2/Shelly4/Shelly RGBW2/Shelly Dimmer2/Shelly Bulb Duo/Shelly i3/Shelly Motion to support the development of this plugin.**
