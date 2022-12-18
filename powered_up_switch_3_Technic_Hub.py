from pybricks.hubs import TechnicHub
from pybricks.pupdevices import Motor, Remote, ColorDistanceSensor
from pybricks.parameters import Port, Direction, Button, Color, Stop
from pybricks.tools import wait
from urandom import random

def enum(**enums):
    return type('Enum', (), enums)

SwitchPosition = enum(STRAIGTH=1, CURVED=2)
SwitchMode = enum(UP=1, DOWN=2)

# The very basic sensor for a switch. Use the concrete implementations like
# SwitchDistanceSensor to create one.
class SwitchSensor():

    def __init__(self, criticalDistance, switchMode=SwitchMode.DOWN, init_timeout=30):
        self.criticalDistance = criticalDistance
        self.switchMode = switchMode
        self.init_timeout = init_timeout
        if switchMode == SwitchMode.UP:
            self.timeout = 0
        else:
            self.reset()

    # The 'timeout' is used as following: the timeout is resetted (i. e. set to a
    # positive number) if a train is currently detected in front of the train. If no
    # train can be detected this value is decremented. The check is only successful
    # if the timout is not positive anymore (i. e. some time has been passed
    # since a train has been detected and we are not in between waggons by accident)
    # and the a train is currently in front the sensor
    def check(self):
        if self.switchMode == SwitchMode.UP:
            if self.sensor.distance() < self.criticalDistance:
                # a train is in front the sensor
                if self.switchMode == SwitchMode.UP and self.timeout <= 0: 
                    self.reset()
                    return True
            else:
                self.decrement()
        else:
            if self.sensor.distance() < self.criticalDistance:
                if self.timeout <= 0:
                    # a train is not anymore in front
                    self.reset()
                    return True
                self.reset()
            else:
                self.decrement()

        return False

    def decrement(self):
        self.timeout = max(0, self.timeout - 1)
        return 

    def reset(self):
        self.timeout = self.init_timeout

class SwitchDistanceSensor(SwitchSensor):

    def __init__(self, port : Port, criticalDistance = 30):
        super().__init__(criticalDistance)
        self.sensor = ColorDistanceSensor(port)

class SwitchIRSensor(SwitchSensor):
    
    def __init__(self, port : Port, criticalDistance = 7):
        super(criticalDistance)
        self.sensor = InfraredSensor(port)

class SwitchUltrasonicSensor(SwitchSensor):
    
    def __init__(self, port : Port, criticalDistance = 7):
        super(criticalDistance)
        self.sensor = UltrasonicSensor(port)

class SwitchColorSensor(SwitchSensor):
    
    def __init__(self, port : Port, criticalReflection):
        super(criticalReflection)
        self.criticalReflection = criticalReflection

    def check(self):
        if self.sensor.reflection() < self.criticalReflection:
            return self.decrementAndCheck()
        else:
            self.reset()
        return False


class SwitchMotor:
    def __init__(self, 
            port : Port, 
            switchPosition = SwitchPosition.STRAIGTH, 
            direction = Direction.CLOCKWISE,
            probability_straigth_to_curved = 0.5,
            probability_curved_to_straigth = 0.5):
        self.probabilities = {SwitchPosition.STRAIGTH: probability_straigth_to_curved,
                                SwitchPosition.CURVED: probability_curved_to_straigth}
        self.switchPosition = switchPosition
        self.initialPosition = switchPosition
        self.motor = Motor(port, direction)
        self.successors = {}
        self.power = 500
        self.stop_mode = Stop.BRAKE

        self.calibrate()

    def calibrate(self):
        angle1 = self.motor.run_until_stalled(self.power / 5)
        angle2 = self.motor.run_until_stalled(-self.power / 5)

        # move angles a little bit towards each other to prevent motor squeaking
        diff = angle1 - angle2
        angle1 = int(angle1 - diff/3.0)
        angle2 = int(angle2 + diff/3.0)

        other_switch_position = SwitchPosition.STRAIGTH if self.switchPosition == SwitchPosition.CURVED else SwitchPosition.CURVED
        if angle1 < -angle2:
            self.motor.run_target(self.power, angle1)
            self.angle = {self.switchPosition: angle1, other_switch_position: angle2}
        else:
            self.motor.run_target(self.power, angle2)
            self.angle = {self.switchPosition: angle2, other_switch_position: angle1}

    def registerSuccessor(self, successor : SwitchMotor, switchPosition : SwitchPosition):
        self.successors[switchPosition] = successor

    def switch_angle(self):
        return self.angle1 if self.angle == self.angle2 else self.angle2

    def move(self):
        if self.switchPosition == SwitchPosition.STRAIGTH:
            self.switchPosition = SwitchPosition.CURVED
        elif self.switchPosition == SwitchPosition.CURVED:
            self.switchPosition = SwitchPosition.STRAIGTH
        angle = self.angle[self.switchPosition]
        self.motor.run_target(self.power, angle, then=self.stop_mode, wait=True)      
        self.power *= -1

    def moveRandom(self):
        if random() < self.probabilities[self.switchPosition]:
            self.move()
        self.moveSuccessorRandom()

    def moveSuccessorRandom(self):
        if self.switchPosition in self.successors.keys():
            self.successors[self.switchPosition].moveRandom()

    def reset(self):
        if self.switchPosition != self.initialPosition:
            self.move()
        for motor in self.successors.values():
            motor.reset()

class SwitchController():

    def __init__(self, hub = None, dt=50):
        self.sensors = {}
        self.dt = dt
        self.hub = hub
        self.initializeHub()
        
    def registerSensor(self, sensor : SwitchSensor, motor = None):
        self.sensors[sensor] = motor

    # Registers a new motor (which controls a switch) within a sensor-motor-group
    # The precessor can either be a sensor (i. e. the motor is right behind the 
    # sensor) or another motor (i. e. the motor is behind another switch)
    def registerMotor(self, precessor : SwitchSensor, motor : SwitchMotor):
        self.sensors[precessor] = motor

    def __str__():
        pass

    def run(self, timeout = None):
        while Button.CENTER not in self.hub.button.pressed():
            self.tick()
            wait(self.dt)
        self.color(Color.YELLOW)
        self.reset()
        self.hub.system.shutdown()

    def tick(self):

        for sensor in self.sensors:
            if sensor.check():
                self.color(Color.RED)
                self.sensors[sensor].moveRandom()

        max_timeout = max([sensor.timeout for sensor in self.sensors])
        init_timeout = max([sensor.init_timeout for sensor in self.sensors])
        if max_timeout <= 0:
            self.color(Color.GREEN)
        elif max_timeout >= init_timeout - 1:
            self.color(Color.RED)
        else:
            self.color(Color.ORANGE)

    def reset(self):
        for sensor in self.sensors:
            self.sensors[sensor].reset()

    def color(self, color : Color):
        if self.hub is not None:
            self.hub.light.on(color)

    def initializeHub(self):
        if self.hub is not None:
            self.hub.system.set_stop_button(None)
        self.color(Color.GREEN)


# create a layout sensor before motor1, the straight direction of motor 1 leads to motor2 and the curved one to motor3
sensor = SwitchDistanceSensor(Port.A, criticalDistance=50)
motor1 = SwitchMotor(Port.B, probability_straigth_to_curved=0.5, probability_curved_to_straigth=0.7)

motor2 = SwitchMotor(Port.C, probability_straigth_to_curved=0.8, probability_curved_to_straigth=0.9)
motor1.registerSuccessor(motor2, SwitchPosition.STRAIGTH)

motor3 = SwitchMotor(Port.D)
motor1.registerSuccessor(motor3,SwitchPosition.CURVED)

hub = TechnicHub()
controller = SwitchController(hub)
controller.registerSensor(sensor, motor1)
controller.run()