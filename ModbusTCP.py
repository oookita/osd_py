##!/usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import sys
from socket import *
from contextlib import closing

HOST = "192.168.1.201"
PORT = 502
netaddr = (HOST,PORT)
BUFFER_SIZE = 1024

def setNetAddress(NetAddress):
    HOST = NetAddress[0]
    PORT = NetAddress[1]


def setReadCmd(type,adr,size):
    ReadCmd = bytearray(12)

    ReadCmd[0] = 0x00
    ReadCmd[1] = 0x00
    ReadCmd[2] = 0x00
    ReadCmd[3] = 0x00
    ReadCmd[4] = 0x00
    ReadCmd[5] = 0x06           #size
    ReadCmd[6] = 0x01           #UnitID (Fixed)
    ReadCmd[7] = type           #CommandCode
    ReadCmd[8] = adr // 256     #ReadAddress
    ReadCmd[9] = adr % 256
    ReadCmd[10] = size // 256   #ReadSize
    ReadCmd[11] = size % 256

    return ReadCmd


def setSingleWriteCmd(adr,val):
    WriteCmd = bytearray(12)

    WriteCmd[0] = 0x00
    WriteCmd[1] = 0x00
    WriteCmd[2] = 0x00
    WriteCmd[3] = 0x00
    WriteCmd[4] = 0x00
    WriteCmd[5] = 0x06      #size
    WriteCmd[6] = 0x01      #UintID (Fixed)
    WriteCmd[7] = 0x06      #CommandCode (06)
    WriteCmd[8] = adr // 256      #WriteAddress
    WriteCmd[9] = adr % 256
    WriteCmd[10] = val[0]     #WriteData
    WriteCmd[11] = val[1]

    return WriteCmd


def PresetMultipleRegistersCmd(adr,val):
    byteSize = len(data)
    WriteCmd = bytearray(11 + bytesze)

    WriteCmd[0] = 0x00
    WriteCmd[1] = 0x00
    WriteCmd[2] = 0x00
    WriteCmd[3] = 0x00
    WriteCmd[4] = 0x00
    WriteCmd[5] = 5 + byteSize      #command size
    WriteCmd[6] = 0x01              #UintID (Fixed)
    WriteCmd[7] = 0x10              #CommandCode (10)
    WriteCmd[8] = adr // 256        #WriteAddress
    WriteCmd[9] = adr % 256
    writeCmd[10] = byteSize         #data size
    for idx in range(0,byteSize):   #WriteData
        writeCmd[11 + idx] = val[idx]

    return WriteCmd




def ReadHoldingRegisters(adr,size):
    return ReadRegisters(0x03,adr,size)

def ReadInputRegisters(adr,size):
    return ReadRegisters(0x04,adr,size)

#
# Read Registers (command 03 or 04)
#
def ReadRegisters(type,adr,size):
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(2.0)
    with closing(s):
        s.connect(netaddr)
        readcmd = setReadCmd(type, adr, size)
        s.send(readcmd)
        res = s.recv(BUFFER_SIZE)
    return res

#
# Preset SIngle Register (06) Expanded  (orginal)
# Use when the connection destination dose not suppot 16(0x10)command (Present Multiple Registers)
#
def WriteRegisters(adr,data):
    wordsize = len(data) // 2

    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(2.0)
    with closing(s):
        #try:
        s.connect(netaddr)
        for cnt in range(0, wordsize):
            index = cnt * 2
            val = data[index : index+2]
            address = adr + cnt
            #print("index=",index,"address=",address,"value=",val)
            writecmd = setSingleWriteCmd(address, val)
            #print('writeCmd=',writecmd)
            s.send(writecmd)
            res = s.recv(BUFFER_SIZE)
            #print("res=",res)
        #except socket.timeout:


#
# Preset Multiple Registers (0x10)
#
def PresetMultipleRegisters(adr,data):
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(2.0)
    with closing(s):
        s.connect(netaddr)
        cmd = PresetMultipleRegistersCmd(adr,data)
        s.send(cmd)
        res = s.recv(BUFFER_SIZE)
