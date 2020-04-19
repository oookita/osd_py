##!/usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8


#
# TM Series
# Gamepad Move
# GetCurrentPosition : ModbusTCP
# SetMobePosition : SocketMessage
#


import pygame
from pygame.locals import *
import time
import sys
import struct
import socket

import ModbusTCP
import TcpClient

# size of window
SCREEN_WIDTH = 350
SCREEN_HEIGHT = 250
SPEED = 1.0

class JoyStatus:
    def __init__(self):
        self.axLx = 0
        self.axLy = 0
        self.axRx = 0
        self.axRy = 0
        self.hatL = 0
        self.hatR = 0
        self.hatU = 0
        self.hatD = 0
        self.btn = [0,0,0,0,0,0,0,0,0,0]
JStat = JoyStatus()

class Position:
    def __init__(self):
        self.clear()
    def clear(self):
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.Rx = 0.0
        self.Ry = 0.0
        self.Rz = 0.0
Pos = Position()
BasePos = Position()
RelativePos = Position()

#Initialize JOYSTICK
pygame.joystick.init()
try:
    joy = pygame.joystick.Joystick(0)
    joy.init()
#    print("Number of Button : " + str(joy.get_numbuttons()))
#    print("Number of Axis : " + str(joy.get_numaxes()))
#    print("Number of Hats : " + str(joy.get_numhats()))
except pygame.error:
    print("Joystick is not found")
    sys.exit()

#
# main
#
def main():
    # create window
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('JOYSTICK')
    pygame.display.flip()
    run = 0
    speedUpDown = 0
    commInterval = 0.03      # Communication Interval (s)
    commTimer = time.time()

    while True:
        #event
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

        ShowPad(screen)

        if joy.get_button(8) == 1:
            run = 0

        if joy.get_button(9) == 1 and run == 0:

            readdata = ModbusTCP.ReadInputRegisters(7001, 12)
            setBasePos(readdata[9:])
            ModbusTCP.WriteRegisters(9000, readdata[9:])
            ModbusTCP.WriteRegisters(9012, readdata[9:])

            Pos.clear()
            commTimer = time.time()
            run = 1

        if run == 1:
            clamp = 0
            if joy.get_button(1) == 1:                              #A
                clamp = 2
            elif joy.get_button(2) == 1:                            #B
                clamp = 1

            if clamp == 0:
                setPosition()

            commElapsedtime = time.time() - commTimer
            if commElapsedtime > commInterval:
                starttime = time.time()

                #data = setCommMemory(clamp)
                #ModbusTCP.WriteRegisters(9012, data)

                SendStr = setSendStr(clamp)
                TcpClient.sendString(SendStr.encode())

                commTimer = time.time()
                elapsedtime = time.time() - starttime
                print("Elapsed Time = %sms" % (str(elapsedtime * 1000)))
                if elapsedtime > 0.1:
                    print("##### Over 100ms #####")

        # Speed
        global SPEED
        hat = joy.get_hat(0)
        if hat[1] > 0 and speedUpDown == 0:
            if SPEED < 4.95:
                SPEED += 0.1
                speedUpDown = 1
        elif hat[1] < 0 and speedUpDown == 0:
            if SPEED > 0.15:
                SPEED -= 0.1
                speedUpDown = 1
        elif hat[1] == 0:
            speedUpDown = 0

        pygame.time.wait(10)



def setBasePos(current):
    # bytes to float x6
    BasePos.X,BasePos.Y,BasePos.Z,BasePos.Rx,BasePos.Ry,BasePos.Rz = struct.unpack('>ffffff', current)


def setPosition():
    if not -0.01 < joy.get_axis(0) < 0.01:                #LeftStickX
        RelativePos.X += joy.get_axis(0) * SPEED
    if not -0.01 < joy.get_axis(1) < 0.01:                #LeftStickY
        RelativePos.Y -= joy.get_axis(1) * SPEED
    if joy.get_button(4) == 1:                              #l1
        RelativePos.Z -= SPEED
    if joy.get_button(5) == 1:                              #R1
        RelativePos.Z += SPEED

    if not -0.01 < joy.get_axis(2) < 0.01:                #RightStickX
        RelativePos.Rx += joy.get_axis(2) * (SPEED / 5.0)
    if not -0.01 < joy.get_axis(3) < 0.01:                #RightStickY
        RelativePos.Ry -= joy.get_axis(3) * (SPEED / 5.0)
    if joy.get_button(6) == 1:                              #L2
        RelativePos.Rz -= SPEED / 5.0
    if joy.get_button(7) == 1:                              #R2
        RelativePos.Rz += SPEED / 5.0

    Pos.X = BasePos.X + RelativePos.X
    Pos.Y = BasePos.Y + RelativePos.Y
    Pos.Z = BasePos.Z + RelativePos.Z
    Pos.Rx = BasePos.Rx + RelativePos.Rx
    Pos.Ry = BasePos.Ry + RelativePos.Ry
    Pos.Rz = BasePos.Rz + RelativePos.Rz
    #print(Pos.X,Pos.Y,Pos.Z,Pos.Rx,Pos.Ry,Pos.Rz)

def setCommMemory(clamp):
    PosAll = (Pos.X, Pos.Y, Pos.Z, Pos.Rx, Pos.Ry, Pos.Rz, clamp)      # tuple
    data = struct.pack('>ffffffH', *PosAll)                      # (float x6 + short) to bytes
    #print("output=",data)
    return data

def setSendStr(clamp):
    str = format(Pos.X, '10.3f')
    str += format(Pos.Y, '10.3f')
    str += format(Pos.Z, '10.3f')
    str += format(Pos.Rx, '10.3f')
    str += format(Pos.Ry, '10.3f')
    str += format(Pos.Rz, '10.3f')
    str += format(clamp, '>2')

    return str

def ShowPad(screen):
    font = pygame.font.Font(None, 18)

    # Value of Joystick
    JStat.axLx = int((joy.get_axis(0)+1) * 20 + 100)     #LeftStickX -1...+1
    JStat.axLy = int((joy.get_axis(1)+1) * 20 + 150)     #LeftStickY
    JStat.axRx = int((joy.get_axis(2)+1) * 20 + 200)     #RightStickX
    JStat.axRy = int((joy.get_axis(3)+1) * 20 + 150)     #RightStickY

    # HatSwitch
    hat_input = joy.get_hat(0)

    if hat_input[0] < 0:
        JStat.hatL = 0
        JStat.hatR = 1
    elif hat_input[0] > 0:
        JStat.hatL = 1
        JStat.hatR = 0
    else:
        JStat.hatL = 1
        JStat.hatR = 1

    if hat_input[1] < 0:
        JStat.hatD = 0
        JStat.hatU = 1
    elif hat_input[1] > 0:
        JStat.hatD = 1
        JStat.hatU = 0
    else:
        JStat.hatD = 1
        JStat.hatU = 1

    for i in range(10):
        if joy.get_button(i) == 1:
            JStat.btn[i] = 0
        else:
            JStat.btn[i] = 1


    # refresh window
    screen.fill((0,40,0))

    pygame.draw.circle(screen, (255,255,255), (120,170), 40, 1)
    pygame.draw.circle(screen, (255,255,255), (220,170), 40, 1)
    pygame.draw.circle(screen, (0,255,0), (JStat.axLx, JStat.axLy), 5)
    pygame.draw.circle(screen, (0,255,0), (JStat.axRx, JStat.axRy), 5)

    pygame.draw.rect(screen, (255,255,255), Rect(30,100,15,15), JStat.hatL)
    pygame.draw.rect(screen, (255,255,255), Rect(70,100,15,15), JStat.hatR)
    pygame.draw.rect(screen, (255,255,255), Rect(50,80,15,15), JStat.hatU)
    pygame.draw.rect(screen, (255,255,255), Rect(50,120,15,15), JStat.hatD)

    pygame.draw.rect(screen, (255,255,255), Rect(250,100,15,15), JStat.btn[0])    #X
    pygame.draw.rect(screen, (255,255,255), Rect(270,120,15,15), JStat.btn[1])    #A
    pygame.draw.rect(screen, (255,255,255), Rect(290,100,15,15), JStat.btn[2])    #B
    pygame.draw.rect(screen, (255,255,255), Rect(270,80,15,15), JStat.btn[3])    #Y

    pygame.draw.rect(screen, (255,255,255), Rect(30,50,50,15), JStat.btn[4])    #L1
    pygame.draw.rect(screen, (255,255,255), Rect(250,50,50,15), JStat.btn[5])   #L2
    pygame.draw.rect(screen, (255,255,255), Rect(30,30,50,15), JStat.btn[6])    #R1
    pygame.draw.rect(screen, (255,255,255), Rect(250,30,50,15), JStat.btn[7])   #R2

    pygame.draw.rect(screen, (255,255,255), Rect(120,80,20,15), JStat.btn[8])    #Back
    pygame.draw.rect(screen, (255,255,255), Rect(200,80,20,15), JStat.btn[9])    #Start

    #Show value
    text = font.render("X: {:.3f}".format(Pos.X), True, (255,255,255))
    screen.blit(text, [10,180])
    text = font.render("Y: {:.3f}".format(Pos.Y), True, (255,255,255))
    screen.blit(text, [10,200])
    text = font.render("Z: {:.3f}".format(Pos.Z), True, (255,255,255))
    screen.blit(text, [10,220])
    text = font.render("Rx: {:.3f}".format(Pos.Rx), True, (255,255,255))
    screen.blit(text, [270,180])
    text = font.render("Ry: {:.3f}".format(Pos.Ry), True, (255,255,255))
    screen.blit(text, [270,200])
    text = font.render("Rz: {:.3f}".format(Pos.Rz), True, (255,255,255))
    screen.blit(text, [270,220])

    text = font.render("Speed: {:1.1f}".format(SPEED), True, (255,255,255))
    screen.blit(text, [140,230])

    pygame.display.update()


if __name__ == '__main__':
    main()
