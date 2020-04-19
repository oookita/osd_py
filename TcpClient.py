##!/usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import sys
from socket import *
from contextlib import closing


HOST = "192.168.1.201"
#HOST = "192.168.250.48"
PORT = 5890
netaddr = (HOST,PORT)
BUFFER_SIZE = 1024

def setNetAddress(NetAddress):
    HOST = NetAddress[0]
    PORT = NetAddress[1]



def sendString(data):
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(2.0)
    with closing(s):
        s.connect(netaddr)
        rcvStr = s.recv(BUFFER_SIZE).decode()
        s.send(data)

def rcvString():
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(10.0)
    with closing(s):
        s.connect(netaddr)
        rcvData = s.recv(BUFFER_SIZE)

    return rcvData
