"""
<plugin key="ShellyMQTT" name="Shelly MQTT" version="0.3.2">
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
try:
 from mqtt import MqttClient
except Exception as e:
 Domoticz.Debug("MQTT client import error: "+str(e))

class BasePlugin:
    mqttClient = None

    def onStart(self):
      try:
        Domoticz.Heartbeat(10)
        self.debugging = Parameters["Mode6"]
        if self.debugging == "Verbose":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2)
        self.base_topic = "shellies" # hardwired
        self.mqttserveraddress = Parameters["Address"].strip()
        self.mqttserverport = Parameters["Port"].strip()
        self.mqttClient = MqttClient(self.mqttserveraddress, self.mqttserverport, "", self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)
      except Exception as e:
        Domoticz.Debug("MQTT client start error: "+str(e))


    def checkDevices(self):
        Domoticz.Debug("checkDevices called")

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Color):  # react to commands arrived from Domoticz
        if self.mqttClient is None:
         return False
        Domoticz.Debug("Command: " + Command + " (" + str(Level) + ") Color:" + Color)
        try:
         device = Devices[Unit]
         device_id = device.DeviceID.split('-')
        except Exception as e:
         Domoticz.Debug(str(e))
         return False
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
          try:
           self.mqttClient.Publish(mqttpath, cmd)
           if cmd=="off":
            device.Update(nValue=int(Level),sValue=str(Command)) # force device update if it is offline
          except Exception as e:
           Domoticz.Debug(str(e))
        # otherwise check if it is a roller shutter
        elif relnum in range(0,4) and len(device_id)==4 and device_id[len(device_id)-1]=="roller":
         cmd = Command.strip().lower()
         scmd = ""                      # Translate Domoticz command to Shelly command
         if cmd == "stop":
          scmd = "stop"
         elif cmd == "on":
          scmd = "open"
         elif cmd == "off":
          scmd = "close"
         if scmd != "":
          mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/roller/"+device_id[2]+"/command"
          try:
           self.mqttClient.Publish(mqttpath, scmd)
          except Exception as e:
           Domoticz.Debug(str(e))
        # experimental support for v1.4 Percentage poisitioning
        elif relnum in range(0,4) and len(device_id)==4 and device_id[len(device_id)-1]=="pos":
          cmnd = str(Command).strip().lower()
          pos = str(Level).strip().lower()
          if ((cmnd=="set level") or (cmnd=="off" and pos!="50" and pos!="100")): # percentage requested 
           mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/roller/"+device_id[2]+"/command/pos"
           Domoticz.Debug(mqttpath+" "+str(Command)+" "+str(Level))
           try:
            self.mqttClient.Publish(mqttpath, pos)
           except Exception as e:
            Domoticz.Debug(str(e))
          else: # command arrived
           scmd = ""                      # Translate Domoticz command to Shelly command
           if cmnd == "on":
            scmd = "open"
           elif cmnd == "off":
            scmd = "close"
           if scmd != "":
            mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/roller/"+device_id[2]+"/command"
            try:
             self.mqttClient.Publish(mqttpath, scmd)
            except Exception as e:
             Domoticz.Debug(str(e))

    def onConnect(self, Connection, Status, Description):
       if self.mqttClient is not None:
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
       if self.mqttClient is not None:
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
       if self.mqttClient is not None:
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
       if self.mqttClient is not None:
        self.mqttClient.Subscribe([self.base_topic + '/#'])

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")

    def onMQTTPublish(self, topic, message): # process incoming MQTT statuses
        if "/announce" in topic: # announce did not contain any information for us
         return False
        try:
         topic = str(topic)
         message = str(message)
        except:
         Domoticz.Debug("MQTT message is not a valid string!") #if message is not a real string, drop it
         return False
        Domoticz.Debug("MQTT message: " + topic + " " + str(message))
        mqttpath = topic.split('/')
        if (mqttpath[0] == self.base_topic): 
         # RELAY type, not command->process
         if (len(mqttpath)>3) and (mqttpath[2] == "relay") and ("/command" not in topic):
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
          if subval=="power" or subval=="energy":
            unitname=mqttpath[1]+"-energy"
          iUnit = -1
          for Device in Devices:
           try:
            if (Devices[Device].DeviceID.strip() == unitname):
             iUnit = Device
             break
           except:
            pass
          if iUnit<0: # if device does not exists in Domoticz, than create it
            try:
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
              if subval=="energy" or subval=="power":
               Domoticz.Device(Name=unitname, Unit=iUnit,Type=243,Subtype=29,Used=1,DeviceID=unitname).Create()
            except Exception as e:
             Domoticz.Debug(str(e))
             return False
          if devtype==0:
           try:
            scmd = str(message).strip().lower()
            if (str(Devices[iUnit].sValue).lower() != scmd):
             if (scmd == "on"): # set device status if needed
              Devices[iUnit].Update(nValue=1,sValue="On")
             else:
              Devices[iUnit].Update(nValue=0,sValue="Off")
           except Exception as e:
            Domoticz.Debug(str(e))
            return False
          else:
           try:
            curval = Devices[iUnit].sValue
            prevdata = curval.split(";")
           except:
            prevdata = []
           if len(prevdata)<2:
            prevdata.append(0)
            prevdata.append(0)
           try:
            mval = float(str(message).strip())
           except:
            mval = str(message).strip()
           sval = ""
           if subval=="power":
            sval = str(mval)+";"+str(prevdata[1])
           elif subval=="energy":
            try:
             mval2 = (mval/100) # 10*Wh?
            except:
             mval2 = str(mval)
            sval = str(prevdata[0])+";"+str(mval2)
           try:
            Devices[iUnit].Update(nValue=0,sValue=str(sval))
           except Exception as e:
            Domoticz.Debug(str(e))
          return True
         # ROLLER type, not command->process
         elif (len(mqttpath)>3) and (mqttpath[2] == "roller") and ("/command" not in topic):
          if mqttpath[len(mqttpath)-1]=="pos":
           unitname = mqttpath[1]+"-"+mqttpath[3]+"-pos"
          else:
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
            try:
             iUnit = 0
             for x in range(1,256):
              if x not in Devices:
               iUnit=x
               break
             if iUnit==0:
              iUnit=len(Devices)+1
             if "-pos" in unitname:
              Domoticz.Device(Name=unitname, Unit=iUnit,Type=244, Subtype=62, Switchtype=13,Used=1,DeviceID=unitname).Create() # create Blinds Percentage
             else:
              Domoticz.Device(Name=unitname, Unit=iUnit,Type=244, Subtype=62, Switchtype=15,Used=1,DeviceID=unitname).Create() # create Venetian Blinds EU type
            except Exception as e:
             Domoticz.Debug(str(e))
             return False
          if "-pos" in unitname:
           try:
            pval = str(message).strip()
            nval = 0
            if int(pval)>0 and int(pval)<100:
             nval = 2
            if int(pval)>99:
             nval = 1
            Devices[iUnit].Update(nValue=int(nval),sValue=str(pval))
           except:
            Domoticz.Debug("MQTT message error " + str(topic) + ":"+ str(message))
          else:
           try:
            bcmd = str(message).strip().lower()
            if bcmd == "stop" and str(Devices[iUnit].sValue).lower() !="stop":
             Devices[iUnit].Update(nValue=17,sValue="Stop") # stop
             return True
            elif bcmd == "open" and str(Devices[iUnit].sValue).lower() !="off":
             Devices[iUnit].Update(nValue=0,sValue="Off") # open
             return True
            elif bcmd == "close" and str(Devices[iUnit].sValue).lower() !="on":
             Devices[iUnit].Update(nValue=1,sValue="On")  # close
             return True
           except Exception as e:
            Domoticz.Debug(str(e))
            return False
         # INPUT type, not command->process
         elif (len(mqttpath)>3) and (mqttpath[2] == "input") and (mqttpath[len(mqttpath)-1]!="command"):
          unitname = mqttpath[1]+"-"+mqttpath[3]+"-input"
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
            try:
             iUnit = 0
             for x in range(1,256):
              if x not in Devices:
               iUnit=x
               break
             if iUnit==0:
              iUnit=len(Devices)+1
             Domoticz.Device(Name=unitname+" BUTTON", Unit=iUnit,TypeName="Switch",Used=0,DeviceID=unitname).Create()
            except Exception as e:
             Domoticz.Debug(str(e))
             return False
          try:
           if str(message).lower=="on" or str(message)=="1":
            scmd = "on"
           else:
            scmd = "off"
           if (str(Devices[iUnit].sValue).lower() != scmd):
            if (scmd == "on"): # set device status if needed
             Devices[iUnit].Update(nValue=1,sValue="On")
            else:
             Devices[iUnit].Update(nValue=0,sValue="Off")
          except Exception as e:
           Domoticz.Debug(str(e))
           return False
          return True
         # SENSOR type, not command->process
         elif (len(mqttpath)>3) and (mqttpath[2] == "sensor") and (mqttpath[3] in ['temperature','humidity','battery']) and (("shellysense" in mqttpath[1]) or ("shellyht" in mqttpath[1])):
          unitname = mqttpath[1]+"-sensor"
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
            try:
             iUnit = 0
             for x in range(1,256):
              if x not in Devices:
               iUnit=x
               break
             if iUnit==0:
              iUnit=len(Devices)+1
             Domoticz.Device(Name=unitname, Unit=iUnit, TypeName="Temp+Hum",Used=1,DeviceID=unitname).Create() # create Temp+Hum Type=82
            except Exception as e:
             Domoticz.Debug(str(e))
             return False
          stype = mqttpath[3].strip().lower()
          try:
           curval = Devices[iUnit].sValue
          except:
           curval = 0
          try:
           mval = float(message)
          except:
           mval = str(message).strip()
          if stype=="battery":
           try:
            Devices[iUnit].Update(nValue=0,sValue=str(curval),BatteryLevel=int(mval))
           except Exception as e:
            Domoticz.Debug(str(e))
          elif stype=="temperature":
           try:
            env = curval.split(";")
           except:
            env = [0,0]
           if len(env)<3:
            env.append(0)
            env.append(0)
            env.append(0)
           sval = str(mval)+";"+str(env[1])+";"+str(env[2])
           try:
            Devices[iUnit].Update(nValue=0,sValue=str(sval))
           except Exception as e:
            Domoticz.Debug(str(e))
          elif stype=="humidity":
           hstat = 0
           try:
            env = curval.split(";")
           except:
            env = [0,0]
           if len(env)<1:
            env.append(0)
           if int(mval)>= 50 and int(mval)<=70:
            hstat = 1
           elif int(mval)<40:
            hstat = 2
           elif int(mval)>70:
            hstat = 3
           sval = str(env[0]) + ";"+ str(mval)+";"+str(hstat)
           try:
            Devices[iUnit].Update(nValue=0,sValue=str(sval))
           except Exception as e:
            Domoticz.Debug(str(e))

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
