"""
<plugin key="ShellyMQTT" name="Shelly MQTT" version="0.2.0">
    <description>
      Simple plugin to manage Shelly switches through MQTT
      <br/>
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="Username" width="300px"/>
        <param field="Password" label="Password" width="300px" default="" password="true"/>

        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="Verbose" value="Verbose"/>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json
import time
import re
from mqtt import MqttClient

class BasePlugin:
    mqttClient = None

    def onStart(self):
        self.debugging = Parameters["Mode6"]
        
        if self.debugging == "Verbose":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2)

        self.base_topic = "shellies" # hardwired

        self.mqttserveraddress = Parameters["Address"].strip()
        self.mqttserverport = Parameters["Port"].strip()
        self.mqttClient = MqttClient(self.mqttserveraddress, self.mqttserverport, self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)


    def checkDevices(self):
        Domoticz.Debug("checkDevices called")

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Color):  # react to commands arrived from Domoticz
        Domoticz.Debug("Command: " + Command + " (" + str(Level) + ") Color:" + Color)
        device = Devices[Unit]
        device_id = device.DeviceID.split('-')
        relnum = -1
        try:
         relnum = int(device_id[2].strip())
        except:
         relnum = -1
        if relnum in range(0,4) and len(device_id)==3: # check if is it a normal relay
         mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/relay/"+device_id[2]+"/command"
         cmd = Command.strip().lower()
         Domoticz.Debug(mqttpath+" "+cmd)
         if cmd in ["on","off"]:        # commands are simply on or off
          self.mqttClient.Publish(mqttpath, cmd)
          if cmd=="off":
           device.Update(Level,Command) # force device update if it is offline
        # otherwise check if it is a roller shutter
        elif relnum in range(0,4) and len(device_id)==4 and device_id[len(device_id)-1]=="roller":
         cmd = Command.strip().lower()
         scmd = ""                      # Translate Domoticz command to Shelly command
         if cmd == "stop":
          scmd = "stop"
         elif cmd == "off":
          scmd = "open"
         elif cmd == "on":
          scmd = "close"
         if scmd != "":
          mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/roller/"+device_id[2]+"/command"
          self.mqttClient.Publish(mqttpath, scmd)

    def onConnect(self, Connection, Status, Description):
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
        self.mqttClient.onMessage(Connection, Data)

    def onHeartbeat(self):
        Domoticz.Debug("Heartbeating...")

        # Reconnect if connection has dropped
        if self.mqttClient.mqttConn is None or (not self.mqttClient.mqttConn.Connecting() and not self.mqttClient.mqttConn.Connected() or not self.mqttClient.isConnected):
            Domoticz.Debug("Reconnecting")
            self.mqttClient.Open()
        else:
            self.mqttClient.Ping()

    def onMQTTConnected(self):
        self.mqttClient.Subscribe([self.base_topic + '/#'])

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")

    def onMQTTPublish(self, topic, message): # process incoming MQTT statuses
        Domoticz.Debug("MQTT message: " + topic + " " + str(message))
        mqttpath = topic.split('/')
        if (mqttpath[0] == self.base_topic): 
         # RELAY type, not command->process
         if (len(mqttpath)>3) and (mqttpath[2] == "relay") and (mqttpath[len(mqttpath)-1]!="command"):   
          unitname = mqttpath[1]+"-"+mqttpath[3]
          unitname = unitname.strip()
          devtype = 1
          try:
           funcid = int(mqttpath[3].strip())
           devtype=0
          except:
           devtype = 1
          if len(mqttpath)==5 and devtype==0:
           devtype = 2
          subval=""
          if devtype==1:
               subval = mqttpath[3].strip()
          elif devtype==2:
               subval = mqttpath[4].strip()
               unitname=unitname+"-"+subval
          iUnit = -1
          for Device in Devices:
           try:
            if (Devices[Device].DeviceID.strip() == unitname):
             iUnit = Device
             break
           except:
            pass
          if iUnit<0: # if device does not exists in Domoticz, than create it
             iUnit = 0
             for x in range(1,256):
              if x not in Devices:
               iUnit=x
               break
             if iUnit==0:
              iUnit=len(Devices)+1
             if devtype==0:
              Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="Switch",Used=1,DeviceID=unitname).Create()
             else:
              if subval=="energy":
               Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="kWh",Used=1,DeviceID=unitname).Create()
              elif subval=="power":
               Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="Usage",Used=1,DeviceID=unitname).Create()
          if devtype==0:
           scmd = str(message).strip().lower()
           if (str(Devices[iUnit].sValue).lower() != scmd):
            if (scmd == "on"): # set device status if needed
             Devices[iUnit].Update(1,"On") 
            else:
             Devices[iUnit].Update(0,"Off") 
          else:
           value = 0
           try:
            value = int(str(message).strip())
            if subval=="energy":
             value = (value/100) # 10*Wh??
             value = str(value)+";0"
           except:
            value=str(message).strip()
           Devices[iUnit].Update(0,str(value))
          return True
         # ROLLER type, not command->process
         elif (len(mqttpath)>3) and (mqttpath[2] == "roller") and (mqttpath[len(mqttpath)-1]!="command"):
          unitname = mqttpath[1]+"-"+mqttpath[3]+"-roller"
          unitname = unitname.strip()
          iUnit = -1
          for Device in Devices:
           try:
            if (Devices[Device].DeviceID.strip() == unitname):
             iUnit = Device
             break
           except:
            pass
          if iUnit<0: # if device does not exists in Domoticz, than create it
             iUnit = 0
             for x in range(1,256):
              if x not in Devices:
               iUnit=x
               break
             if iUnit==0:
              iUnit=len(Devices)+1
             Domoticz.Device(Name=unitname, Unit=iUnit,Type=244, Subtype=62, Switchtype=15,Used=1,DeviceID=unitname).Create() # create Venetian Blinds EU type
          Domoticz.Debug(str(Devices[iUnit].Name)+ " " + str(message))
          bcmd = str(message).strip().lower()
          if bcmd == "stop" and str(Devices[iUnit].sValue).lower() !="stop":
           Devices[iUnit].Update(17,"Stop") # stop
           return True
          elif bcmd == "open" and str(Devices[iUnit].sValue).lower() !="off":
           Devices[iUnit].Update(0,"Off") # open
           return True
          elif bcmd == "close" and str(Devices[iUnit].sValue).lower() !="on":
           Devices[iUnit].Update(1,"On")  # close
           return True

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()
    
def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
