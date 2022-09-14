#!/usr/bin/env pybricks-micropython


from random import randint as rdm
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor
from pybricks.parameters import Port, Button, Stop, Color
from pybricks.tools import wait

# initilize
speed = 100
IRHeight = 32
XLTurn = -50
maxCount = 25
IRCount = maxCount
change = False
XL1IsClosed = False
XL2IsClosed = False

ev3 = EV3Brick()
ev3.light.on(Color.ORANGE)
wait(10000)


ir = InfraredSensor(Port.S1)
XL1 = Motor(Port.A)
XL2 = Motor(Port.B)

def direction(isClosed):
    if isClosed:
        return -1
    else:
        return 1

def moveXL1():
    global XL1IsClosed, change
    XL1.run_angle(1000, direction(XL1IsClosed)*XLTurn)
    XL1IsClosed = not XL1IsClosed
    ev3.light.on(Color.ORANGE)

def moveXL2():
    global XL2IsClosed, change
    XL2.run_angle(1000, direction(XL2IsClosed)*XLTurn, Stop.COAST, False)
    XL2IsClosed = not XL2IsClosed
    ev3.light.on(Color.ORANGE)
    
def reset():
    ev3.light.on(Color.ORANGE)
    if XL1IsClosed:
        moveXL1()
    if XL2IsClosed:
        moveXL2()
    ev3.light.on(Color.GREEN)
    wait(100)

# loop
while True:
    ran = rdm(1,10)
    if Button.CENTER in ev3.buttons.pressed():
        break
    if ev3.battery.voltage() < 5000:
        print("crtitical low battary")
        ev3.sound.beep()
        break

    IRDist = ir.distance()
    if IRCount == 0:
        ev3.light.on(Color.GREEN)
        if IRHeight > IRDist:
            IRCount = maxCount
            if ran < 8:
                moveXL1()
            if XL1IsClosed and ran >= 2:
                moveXL2()
    else:
        IRCount = max(IRCount - 1, 0)

    # Cooldown
    if IRHeight > IRDist:
        IRCount = maxCount
    
    wait(speed)

    ev3.screen.clear()
    ev3.screen.print(IRDist)
    ev3.screen.print(IRCount)
    
reset() 