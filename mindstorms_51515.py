from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorDistanceSensor, InfraredSensor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Button, Color, Stop
from pybricks.tools import wait
from urandom import random

def enum(**enums):
    return type('Enum', (), enums)

# SwitchPosition.STRAIGHT means a train would pass the switch in the straight direction
# SwitchPosition.CURVED means a train would pass the switch in the curved direction (either left or right)
SwitchPosition = enum(STRAIGTH=1, CURVED=2)

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
        self.set_switch_mode(switch_mode)


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
        self.timeout = init_timeout

    def set_switch_mode(switch_mode : SwitchMode):
        self.switchMode = switchMode
        if switchMode == SwitchMode.RISING_EDGE:
            self.timeout = 0
        else:
            self.reset()

# a color distance sensor (LEGO item 88007)
class SwitchDistanceSensor(SwitchSensor):
    # critical distance in %
    def __init__(self, port : Port, criticalDistance=30):
        super().__init__(criticalDistance)
        self.sensor = ColorDistanceSensor(port)

# the motion/ IR sensor known from LEGO WeDo 2.0 or the Grand Piano (LEGO item 20844)
class SwitchIRSensor(SwitchSensor):
    # critical distance in %
    def __init__(self, port : Port, criticalDistance=20):
        super().__init__(criticalDistance)
        self.sensor = InfraredSensor(port)

# the ultrasonic sensor known from LEGO Mindstorms 51515 (LEGO part 37316c01)
class SwitchUltrasonicSensor(SwitchSensor):
    
    # critical distance in mm
    def __init__(self, port : Port, criticalDistance=200):
        super().__init__(criticalDistance)
        self.sensor = UltrasonicSensor(port)

# the color sensor known from LEGO Mindstorms 51515 (LEGO part 37308c01)
class SwitchColorSensor(SwitchSensor):
    # critical distance in %
    def __init__(self, port : Port, criticalDistance=85):
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
            switchPosition=SwitchPosition.STRAIGTH, 
            direction=Direction.CLOCKWISE,
            probability_straigth_to_curved=0.5,
            probability_curved_to_straigth=0.5,
            turn_degrees=None):
        self.probabilities = {SwitchPosition.STRAIGTH: probability_straigth_to_curved,
                                SwitchPosition.CURVED: probability_curved_to_straigth}
        self.switchPosition = switchPosition
        self.initialPosition = switchPosition
        self.motor = Motor(port, direction)
        self.successors = {}
        self.power = 500
        self.stop_mode = Stop.COAST
        self.display = None

        if turn_degrees is None:
            self.calibrate()
        else:
            other_switch_position = SwitchPosition.STRAIGTH if self.switchPosition == SwitchPosition.CURVED else SwitchPosition.CURVED
            self.angle = {switchPosition: 0, other_switch_position: turn_degrees}

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
        self.display.cross()
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

    def setDisplay(self, display: LightMatrix):
        self.display = display

class LightMatrix():

    def __init__(self, hub):
        self.hub = hub


    def update(self, timeouts, init_timeouts):
        amount = len(timeouts)
        if amount == 1:
            self.update_one(timeouts, init_timeouts)
        elif amount == 2:
            self.update_two(timeouts, init_timeouts)
        elif amount == 3:
            self.update_three(timeouts, init_timeouts)
        else:
            print("Unknown amount")
            print(amount)

    def _convert(self, pixel_number, total_pixel, proportion):
        if pixel_number / total_pixel <= proportion:
            return 100
        elif (pixel_number - 1) / total_pixel <= proportion:
            return  int(100 * (total_pixel * proportion - (pixel_number - 1)))
        else:
            return 0

    def update_one(self, timeouts, init_timeouts):
        proportion = timeouts[0] / init_timeouts[0]
        matrix = [[self._convert(j * 5 + i + 1, 25, proportion) for i in range(5)] for j in range(5)]
        hub.display.icon(matrix)
    
    def update_two(self, timeouts, init_timeouts):
        data = []
        for index in range(2):
            proportion = timeouts[index] / init_timeouts[index]
            m = [[self._convert(j * 2 + i + 1, 10, proportion) for i in range(2)] for j in range(5)]
            data.append(m)
        matrix = [[data[0][i][0], data[0][i][1], 0, data[1][i][0], data[1][i][1]] for i in range(5)]
        hub.display.icon(matrix)

    def update_three(self, timeouts, init_timeouts):
        data = []
        for index in range(3):
            proportion = timeouts[index] / init_timeouts[index]
            m = [self._convert(j + 1, 5, proportion) for j in range(5)]
            data.append(m)
        matrix = [[data[0][i], 0, data[1][i], 0, data[2][i]] for i in range(5)]
        hub.display.icon(matrix)

    def cross(self):
        matrix = [[100, 0, 0, 0, 100], [0, 100, 0, 100, 0], [0, 0, 100, 0, 0], [0, 100, 0, 100, 0], [100, 0, 0, 0, 100]]
        hub.display.icon(matrix)


class SwitchController():

    def __init__(self, hub=None, dt=50):
        self.sensors = {}
        self.dt = dt
        self.hub = hub
        self.initializeHub()
        self.display = LightMatrix(hub)
        
    def registerSensor(self, sensor : SwitchSensor, motor):
        self.sensors[sensor] = motor
        motor.setDisplay(self.display)

    # Registers a new motor (which controls a switch) within a sensor-motor-group
    # The precessor can either be a sensor (i. e. the motor is right behind the 
    # sensor) or another motor (i. e. the motor is behind another switch)
    def registerMotor(self, precessor : SwitchSensor, motor : SwitchMotor):
        self.sensors[precessor] = motor
        motor.setDisplay(self.display)


    def run(self):
        while Button.CENTER not in self.hub.buttons.pressed():
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
        
        timeouts = [sensor.timeout for sensor in self.sensors]
        max_timeout = max(timeouts)
        init_timeouts = [sensor.init_timeout for sensor in self.sensors]
        init_timeout = max(init_timeouts)
        
        # update status light
        if max_timeout <= 0:
            self.color(Color.GREEN)
        elif any([timeout == init for timeout, init in zip(timeouts, init_timeouts)]): # todo improve
            self.color(Color.ORANGE)
        else:
            self.color(Color.YELLOW)

        # update status light matrix
        if self.hub != None:
            self.display.update(timeouts, init_timeouts)

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

hub = PrimeHub()
hub.display.orientation(Side.BOTTOM)
controller = SwitchController(hub)

# configure your switch layout here
motor1 = SwitchMotor(Port.B, probability_curved_to_straigth=0.5, probability_straigth_to_curved=0.8)
motor2 = SwitchMotor(Port.B, probability_curved_to_straigth=0.5, probability_straigth_to_curved=0.8)
motor1.registerSuccessor(motor1, SwitchPosition.STRAIGTH)

controller.registerSensor(sensor, motor)

# start the switch controller
controller.run()