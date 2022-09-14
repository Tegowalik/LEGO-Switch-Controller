#!/usr/bin/env pybricks-micropython

from random import seed
from random import randint as rdm
from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

# initilize
speed = 10
IRHeight = 32
colorValue = 2
XLTurn = -50
MTurn = -45
maxCount = 40
colorCount = maxCount
IRCount = maxCount
change = False
XL1IsClosed = False
XL2IsClosed = False
MIsClosed = False
#random.seed(0)
brick.light(Color.GREEN)

cs = ColorSensor(Port.S1) 
ir = InfraredSensor(Port.S4)
#btn = TouchSensor(Port.S2)
XL1 = Motor(Port.A)
XL2 = Motor(Port.B)
M = Motor(Port.D)

def direction(isClosed):
    if isClosed:
        return -1
    else:
        return 1

def moveXL1():
    global XL1IsClosed, change
    XL1.run_angle(1000, direction(XL1IsClosed)*XLTurn)
    XL1IsClosed = not XL1IsClosed
    brick.light(Color.ORANGE)

def moveXL2():
    global XL2IsClosed, change
    XL2.run_angle(1000, direction(XL2IsClosed)*XLTurn, Stop.COAST, False)
    XL2IsClosed = not XL2IsClosed
    brick.light(Color.ORANGE)

def moveM():
    global MIsClosed, change
    M.run_angle(1000, direction(MIsClosed)*MTurn)
    MIsClosed = not MIsClosed
    brick.light(Color.ORANGE)
    
def reset():
    print("reset")
    brick.light(Color.ORANGE)
    if XL1IsClosed:
        moveXL1()
    if XL2IsClosed:
        moveXL2()
    if MIsClosed:
        moveM()
    brick.light(Color.GREEN)
    wait(100)

seed(1)
# loop
while True:
    ran = rdm(1,10)
    if Button.CENTER in brick.buttons():
        break
    if brick.battery.voltage() < 5000:
        print("crtitical low battary")
        brick.sound.beep()
        break
    for i in range (1,10):
        IRDist = ir.distance()
        colorReflection = cs.reflection()

        if IRCount == 0 and colorCount == 0:
            brick.light(Color.GREEN)

        # Move
        if IRCount == 0:
            if IRHeight > IRDist:
                IRCount = maxCount
                if MIsClosed and ran < 6:
                    moveM()
                elif not MIsClosed and ran < 9:
                    moveM()
                if MIsClosed:
                    moveXL1()
        else:
            IRCount = IRCount - 1
    
        if colorCount == 0:
            if colorValue < colorReflection:
                colorCount = maxCount
                if ran < 8:
                    moveXL2()
        else:
            colorCount = colorCount - 1

        # Cooldown
        if IRHeight > IRDist:
            IRCount = maxCount
        
        if colorValue < colorReflection:
            colorCount = maxCount
        wait(speed)

    brick.display.clear()
    brick.display.text(IRDist, (60,50))
    brick.display.text(colorReflection)
    brick.display.text(IRCount)
    brick.display.text(colorCount)
    
reset()