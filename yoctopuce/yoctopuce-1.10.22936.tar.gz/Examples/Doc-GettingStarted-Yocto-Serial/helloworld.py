#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
# add ../../Sources to the PYTHONPATH
sys.path.append(os.path.join("..","..","Sources"))
import os,sys
sys.path.append(os.path.join("..", "..", "Sources"))
from yoctopuce.yocto_api import *
from yoctopuce.yocto_serialport import *

# Setup the API to use local USB devices. You can
# use an IP address instead of 'usb' if the device
# is connected to a network.

errmsg = YRefParam()
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("init error" + errmsg.value)

if len(sys.argv) > 1:
    serialPort = YSerialPort.FindSerialPort(sys.argv[1] + ".serialPort")
    if not serialPort.isOnline():
        sys.exit('Module not connected')
else:
    serialPort = YSerialPort.FirstSerialPort()
    if serialPort is None:
        sys.exit('No module connected (check cable)')

    serialPort.set_serialMode("9600,8N1")
    serialPort.set_protocol("Line")
    serialPort.reset()
    
    print("****************************")
    print("* make sure voltage levels *") 
    print("* are properly configured  *")
    print("****************************")

while True:
    print("Type line to send, or Ctrl-C to exit:")
    line = input(": ")  # use raw_input in python 2.x
    if line == "":
        break
    serialPort.writeLine(line)
    YAPI.Sleep(500)
    line = serialPort.readLine()
    if (line != ""):
        print("Received: " + line)
YAPI.FreeAPI()
