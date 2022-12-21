from pybricks.hubs import CityHub
from pybricks.pupdevices import Motor, ColorDistanceSensor, InfraredSensor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Button, Color, Stop
from pybricks.tools import wait
from urandom import random

def enum(**enums):
    return type('Enum', (), enums)

# SwitchPosition.STRAIGHT means a train would pass the switch in the straight direction
# SwitchPosition.CURVED means a train would pass the switch in the curved direction (either left or right)
SwitchPosition = enum(STRAIGHT=1, CURVED=2)

# SwitchMode.RISING_EDGE means that the switch is randomly moved if an incoming train is detected in front of the sensor.
# This mode requires that the motors can complete the moving before the train reaches switch (depends on distance of sensor and switch)
# SwitchPosition.FALLING_EDGE means that the switch is randomly moved after a train has been passed the switch/ sensor completly
SwitchMode = enum(RISING_EDGE=1, FALLING_EDGE=2)

# The very basic sensor for a switch. Use the concrete implementations like
# SwitchDistanceSensor to create one.
# Note that the init_timeout depends on the dt-value (time in ms between two ticks) of the SwitchController.
# The default dt-value of 50ms combined with init_timeout of 40 means that after 40 * 50ms = 2s without sensor detection a train is considered to be passed completely.
class SwitchSensor():

    def __init__(self, criticalDistance, switchMode=SwitchMode.FALLING_EDGE, init_timeout=40):
        self.criticalDistance = criticalDistance
        self.init_timeout = init_timeout
        self.set_switch_mode(switchMode)


    # The 'timeout' is used as following: the timeout is resetted (i. e. set to a
    # positive number) if a train is currently detected in front of the train. If no
    # train can be detected this value is decremented. The check is only successful
    # if the timout is not positive anymore (i. e. some time has been passed
    # since a train has been detected and we are not in between waggons by accident)
    # and the a train is currently in front the sensor
    def check(self):
        d = self.distance()
        if self.switchMode == SwitchMode.RISING_EDGE:
            if d < self.criticalDistance:
                # a train is in front the sensor
                if self.timeout <= 0: 
                    self.reset()
                    return True
                self.reset()
            else:
                self.decrement()
        else:
            if d > self.criticalDistance:
                if self.timeout >= 0:
                    self.decrement()
            else:
                self.reset()

            if self.timeout == 0:
                # a train is not anymore in front
                self.timeout = -1
                return True

        return False

    def distance(self):
        return self.sensor.distance()

    def decrement(self):
        self.timeout = max(0, self.timeout - 1)
        return 

    def reset(self):
        self.timeout = self.init_timeout

    def set_init_timeout(self, init_timeout):
        self.init_timeout = init_timeout

    def set_switch_mode(self, switchMode : SwitchMode):
        self.switchMode = switchMode
        if switchMode == SwitchMode.RISING_EDGE:
            self.timeout = 0
        else:
            self.timeout = -1

# a color distance sensor (LEGO item 88007)
class SwitchDistanceSensor(SwitchSensor):
    # critical distance in %
    def __init__(self, port : Port, criticalDistance=30):
        super().__init__(criticalDistance)
        self.sensor = ColorDistanceSensor(port)

# the motion/ IR sensor known from LEGO WeDo 2.0 or the Grand Piano (LEGO item 20844)
class SwitchIRSensor(SwitchSensor):
    # critical distance in %
    def __init__(self, port : Port, criticalDistance=60):
        super().__init__(criticalDistance)
        self.sensor = InfraredSensor(port)

# the ultrasonic sensor known from LEGO Mindstorms 51515 (LEGO part 37316c01)
class SwitchUltrasonicSensor(SwitchSensor):
    
    # critical distance in mm
    def __init__(self, port : Port, criticalDistance=120):
        super().__init__(criticalDistance)
        self.sensor = UltrasonicSensor(port)

# the color sensor known from LEGO Mindstorms 51515 (LEGO part 37308c01)
class SwitchColorSensor(SwitchSensor):
    # critical distance in %
    def __init__(self, port : Port, criticalDistance=95):
        super().__init__(criticalDistance)
        self.sensor = ColorSensor(port)

    def distance(self):
        return 100 - self.sensor.reflection()

# A representation of a motor for a switch. 
# The corresponding (hardware) motor must have a rotation sensor, like most of the Technic motors and all of the Mindstorm motors have.
# Params:
#   port: The port the motor is connected to, like Port.A
#   switchPosition: the initial position of the straight
#   direction: the default direction of the motor. This is espacially important if turn_degrees is given
#   probability_straight_to_curved: the probability that the switch moves after the sensor triggers and the switch is in the straight position
#   probability_curved_to_straight: the probability that the switch moves after the sensor triggers and the switch is in the curved position
#   turn_degrees: If not None, this value is used as relative position for the other switch position than given. If None, then an auto calibration is done.
class SwitchMotor:
    def __init__(self, 
            port : Port, 
            switchPosition=SwitchPosition.STRAIGHT,
            direction=Direction.CLOCKWISE,
            probability_straight_to_curved=0.5,
            probability_curved_to_straight=0.5,
            turn_degrees=None, # ~60 if no gears are needed
            power=750):
        self.probabilities = {SwitchPosition.STRAIGHT: probability_straight_to_curved,
                                SwitchPosition.CURVED: probability_curved_to_straight}
        self.switchPosition = switchPosition
        self.initialPosition = switchPosition
        self.motor = Motor(port, direction)
        self.motor.reset_angle(0)
        self.motor.stop()
        self.successors = {}
        self.power = power
        self.stop_mode = Stop.COAST

        if turn_degrees is None:
            self.calibrate()
        else:
            other_switch_position = SwitchPosition.STRAIGHT if self.switchPosition == SwitchPosition.CURVED else SwitchPosition.CURVED
            self.angle = {switchPosition: 0, other_switch_position: turn_degrees}

    def calibrate(self):
        self.motor.reset_angle(0)
        angle1 = self.motor.run_until_stalled(self.power / 5)
        angle2 = self.motor.run_until_stalled(-self.power / 5)

        other_switch_position = SwitchPosition.STRAIGHT if self.switchPosition == SwitchPosition.CURVED else SwitchPosition.CURVED
        if angle1 < -angle2:
            self.motor.run_target(self.power, angle1)
            self.angle = {self.switchPosition: angle1, other_switch_position: angle2}
        else:
            self.motor.run_target(self.power, angle2)
            self.angle = {self.switchPosition: angle2, other_switch_position: angle1}
        self.motor.stop()

    def registerSuccessor(self, successor : SwitchMotor, switchPosition : SwitchPosition):
        self.successors[switchPosition] = successor

    def switch_angle(self):
        return self.angle1 if self.angle == self.angle2 else self.angle2

    def move(self):
        if self.switchPosition == SwitchPosition.STRAIGHT:
            self.switchPosition = SwitchPosition.CURVED
        elif self.switchPosition == SwitchPosition.CURVED:
            self.switchPosition = SwitchPosition.STRAIGHT
        angle = self.angle[self.switchPosition]
        self.motor.run_target(self.power, angle, then=self.stop_mode, wait=True)      

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

    def __init__(self, hub=None, dt=50):
        self.sensors = {} # map from sensors to motors
        self.sensorList = [] # preserves order for correct update of the LightMatrix
        self.dt = dt
        self.hub = hub
        self.initializeHub()
        
    def registerSensor(self, sensor : SwitchSensor, motor):
        self.sensors[sensor] = motor
        self.sensorList.append(sensor)

    def run(self):
        while Button.CENTER not in self.hub.button.pressed():
            self.tick()
            wait(self.dt)
        self.color(Color.BLUE)
        self.reset()
        self.hub.system.shutdown()

    def tick(self):

        for sensor in self.sensors:
            if sensor.check():
                self.color(Color.RED)
                self.sensors[sensor].moveRandom()
        
        timeouts = [sensor.timeout for sensor in self.sensorList]
        max_timeout = max(timeouts)
        init_timeouts = [sensor.init_timeout for sensor in self.sensorList]
        init_timeout = max(init_timeouts)
        
        # update status light
        if max_timeout <= 0:
            self.color(Color.GREEN)
        elif any([timeout == init for timeout, init in zip(timeouts, init_timeouts)]): # todo improve
            self.color(Color.ORANGE)
        else:
            self.color(Color.YELLOW)

        
        

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

hub = CityHub()
controller = SwitchController(hub)

# configure your switch layout here
sensor = SwitchDistanceSensor(Port.A, criticalDistance=70)
motor = SwitchMotor(Port.B, probability_curved_to_straight=0.8, probability_straight_to_curved=0.8)
controller.registerSensor(sensor, motor)

# start the switch controller
controller.run()

