from pybricks.pupdevices import Motor, ColorDistanceSensor, InfraredSensor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Button, Color, Stop, Side
from pybricks.tools import wait
from pybricks.hubs import ThisHub
from urandom import random, uniform

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

    # todo use __new__ to auto configure sensor type based on current sensor

    def __init__(self, criticalDistance, switchMode=SwitchMode.FALLING_EDGE, init_timeout=40):
        self.criticalDistance = criticalDistance
        self.init_timeout = init_timeout
        self.set_switch_mode(switchMode)
        self.state = False


    def tick(self):
        self.state = self._tick()

    def _tick(self):
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

    # The 'timeout' is used as following: the timeout is resetted (i. e. set to a
    # positive number) if a train is currently detected in front of the train. If no
    # train can be detected this value is decremented. The check is only successful
    # if the timout is not positive anymore (i. e. some time has been passed
    # since a train has been detected and we are not in between waggons by accident)
    # and the a train is currently in front the sensor
    def check(self):
        return self.state

    def is_blocked(self):
        return self.timeout > 0

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

    def sensors():
        return {self}

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

# a remote sensor i.e. a sensor that is connected to another hub
class RemoteSensor(SwitchSensor):
    # todo implement (placeholder so far)
    pass

class SmartSensor:

    def __init__(self, *args, **kwargs):
        self.pre_sensors = list(args) + kwargs.get('pre_sensors', [])
        self.post_sensors = kwargs.get('post_sensors', {})
        self.update_timeout()
        self.update_init_timeout()
        

    def add_pre_sensor(self, sensor):
        self.pre_sensors.append(sensor)
        self.update_timeout()
        self.update_init_timeout()
        self.state = (False, [])

    def add_post_sensor(self, sensor, path): # todo add more options like delay 
        self.post_sensors[path] = sensor

    def update_timeout(self):
        self.timeout = max([s.timeout for s in self.pre_sensors])
    
    def update_init_timeout(self):
        self.init_timeout = max([s.init_timeout for s in self.pre_sensors])

    def tick():
        self.state = self._tick()

    def _tick(self):
        post_conditions = [cond for cond, sensor in self.post_sensors.items() if sensor.is_blocked()]
        print(post_conditions)
        # first check if any presensor fires
        any_fired = any([s.check() for s in self.pre_sensors])
        print(any_fired)
        if any_fired:
            for s in self.pre_sensors:
                s.reset()

        return any_fired, post_conditions

    def check(self):
        return self.state
        

    def sensors(self):
        return self.pre_sensors + list(self.post_sensors.values())

    def reset(self):
        for sensor in self.sensors():
            sensor.reset()

    def set_init_timeout(self, init_timeout):
        for sensor in self.sensors():
            sensor.set_init_timeout(init_timeout)

    def set_switch_mode(self, switchMode : SwitchMode):
        for sensor in self.sensors():
            sensor.set_switch_mode(switchMode)

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
            switch_position=SwitchPosition.STRAIGHT, 
            direction=Direction.CLOCKWISE,
            probability_straight_to_curved=0.5,
            probability_curved_to_straight=0.5,
            turn_degrees=None, # ~60 if no gears are needed
            power=750):
        self.probabilities = {SwitchPosition.STRAIGHT: probability_straight_to_curved,
                                SwitchPosition.CURVED: probability_curved_to_straight}
        self.switch_position = switch_position
        self.initial_position = switch_position
        self.motor = Motor(port, direction)
        self.motor.reset_angle(0)
        self.motor.stop()
        self.successors = {}
        self.power = power
        self.stop_mode = Stop.COAST
        self.display = None
        self.next_path = None

        if turn_degrees is None:
            self.calibrate()
        else:
            other_switch_position = self.other_switch_position()
            self.angle = {switch_position: 0, other_switch_position: turn_degrees}

    def other_switch_position(self):
        return SwitchPosition.STRAIGHT if self.switch_position == SwitchPosition.CURVED else SwitchPosition.CURVED

    def calibrate(self):
        self.motor.reset_angle(0)
        angle1 = self.motor.run_until_stalled(self.power / 5)
        angle2 = self.motor.run_until_stalled(-self.power / 5)

        # move angles a little bit towards each other
        diff = angle1 - angle2
        if diff > 100:
            angle1 = int(angle1 - diff / 5)
            angle2 = int(angle2 + diff / 5)

        other_switch_position = self.other_switch_position()
        if angle1 < -angle2:
            self.motor.run_target(self.power, angle1)
            self.angle = {self.switch_position: angle1, other_switch_position: angle2}
        else:
            self.motor.run_target(self.power, angle2)
            self.angle = {self.switch_position: angle2, other_switch_position: angle1}
        self.motor.stop()

    def register_successor(self, successor : SwitchMotor, switch_position : SwitchPosition):
        self.successors[switch_position] = successor

    def switch_angle(self):
        return self.angle1 if self.angle == self.angle2 else self.angle2

    def move(self):
        if self.display is not None:
            self.display.cross()
        if self.switch_position == SwitchPosition.STRAIGHT:
            self.switch_position = SwitchPosition.CURVED
        elif self.switch_position == SwitchPosition.CURVED:
            self.switch_position = SwitchPosition.STRAIGHT
        angle = self.angle[self.switch_position]
        self.motor.run_target(self.power, angle, then=self.stop_mode, wait=True)      

    def move_random(self):
        if random() < self.probabilities[self.switch_position]:
            self.move()
        self.move_successor_random()

    # paths are those allowed paths
    def move_smart(self, check, paths):
        if self.next_path in paths:
            # go back to the last path that has been blocked before, but is free again
            self.move_path(self.nextPath)
            self.next_path = None
        else:
            current_path = self.current_path()
            needs2move = currentPath in paths
            if (check and random() < self.probabilities[self.switch_position]) or needs2move:
                # we need to move (at least if a new path is available)
                paths = [p for p in paths if p is not current_path]
                if len(paths) == 0:
                    # no 'good' path is available, so stay for now, and probably 
                    pass
                else:
                    # todo choose random path based on probabilities!!!
                    path_weights = [self._get_path_probability(p) for p in paths]
                    path = self._get_random_path(paths, path_weights)
                    
                    self.move_path(path)
                    if needs2move:
                        # make sure to move back to the now blocked path once this path is free again
                        self.next_path = current_path
                    else:
                        self.next_path = None 

    def move_path(self, path):
        if path[0] != self.switch_position:
            self.move()
        if self.switch_position in self.successors:
            self.successors[self.switch_position].move_path(path[1:])

    def current_path(self):
        return [self.switch_position] + self.successors.get(self.switch_position, [])

    def move_successor_random(self):
        if self.switch_position in self.successors.keys():
            self.successors[self.switch_position].move_random()

    def reset(self):
        if self.switch_position != self.initial_position:
            self.move()
        for motor in self.successors.values():
            motor.reset()

    def set_display(self, display: LightMatrix):
        self.display = display
        for successor in self.successors.values():
            successor.set_display(display)

    def _get_path_probability(self, path, mul=True):
        d = path[0]
        if d == self.probabilities[self.switch_position]:
            prob = 1 - self.probabilities[self.switch_position]
        else:
            prob = self.probabilities[self.switch_position]
        
        if d in self.successors:
            probs = [prob] + self.successors[d]._get_path_probability(path[1:], mul=False)
        else:
            probs = [prob]

        if mul:
            result = 1
            for p in probs:
                result *= p
            return result

        return probs

    # returns a random path whith weighted probabilities
    # this has a similar behaviour as the ususal python random.choices(paths, weights=weights, k=1)[0]
    def _get_random_path(self, paths, weights=None):
        if weights is None:
            return random.choice(paths)
        
        total_weight = sum(weights)
        choices = []
        
        rand = uniform(0, total_weight)
        cumulative_weight = 0
        
        for i, item in enumerate(paths):
            cumulative_weight += weights[i]
            if rand <= cumulative_weight:
                return item

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
        self.hub.display.icon(matrix)
    
    def update_two(self, timeouts, init_timeouts):
        data = []
        for index in range(2):
            proportion = timeouts[index] / init_timeouts[index]
            m = [[self._convert(j * 2 + i + 1, 10, proportion) for i in range(2)] for j in range(5)]
            data.append(m)
        matrix = [[data[0][i][0], data[0][i][1], 0, data[1][i][0], data[1][i][1]] for i in range(5)]
        self.hub.display.icon(matrix)

    def update_three(self, timeouts, init_timeouts):
        data = []
        for index in range(3):
            proportion = timeouts[index] / init_timeouts[index]
            m = [self._convert(j + 1, 5, proportion) for j in range(5)]
            data.append(m)
        matrix = [[data[0][i], 0, data[1][i], 0, data[2][i]] for i in range(5)]
        self.hub.display.icon(matrix)

    def cross(self):
        matrix = [[100, 0, 0, 0, 100], [0, 100, 0, 100, 0], [0, 0, 100, 0, 0], [0, 100, 0, 100, 0], [100, 0, 0, 0, 100]]
        self.hub.display.icon(matrix)


class SwitchController():

    def __init__(self, hub=None, dt=50):
        self.sensors = {} # map from sensors to motors
        self.sensor_list = [] # preserves order for correct update of the LightMatrix
        self.dt = dt
        if not hub:
            hub = ThisHub()
        self.hub = hub
        self.initialize_hub()
        if hasattr(self.hub, 'display'):
            self.display = LightMatrix(hub)
        else:
            self.display = None
        
    def register_sensor(self, sensor : SwitchSensor, motor):
        self.sensors[sensor] = motor
        self.sensorList.append(sensor)
        motor.set_display(self.display)

    def buttons(self):
        if hasattr(self.hub, 'buttons'):
            return self.hub.buttons.pressed()
        elif hasattr(self.hub, 'button'):
            return self.hub.button.pressed()
        else:
            raise ValueError()

    def run(self):
        while Button.CENTER not in self.buttons():
            self.tick()
            wait(self.dt)
        self.color(Color.BLUE)
        self.reset()
        self.hub.system.shutdown()

    def tick(self):
        for sensor in self.all_sensors():
            sensor.tick()

        for sensor in self.sensors:
            check = sensor.check()
            if check is True:
                self.color(Color.RED)
                self.sensors[sensor].move_random()
            elif isinstance(check, tuple):
                self.color(Color.RED)
                self.sensors[sensor].move_smart(*check)
        
        timeouts = [sensor.timeout for sensor in self.sensor_list]
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

        # update status light matrix
        if self.display:
            self.display.update(timeouts, init_timeouts)

    def all_sensors():
        sensors = set()
        for s in self.sensors:
            sensors.update(s.sensors)
        print(sensors)
        return sensors

    def reset(self):
        for sensor in self.all_sensors():
            self.sensors[sensor].reset()

    def color(self, color : Color):
        if self.hub:
            self.hub.light.on(color)

    def initialize_hub(self):
        if self.hub:
            self.hub.system.set_stop_button(None)
        self.color(Color.GREEN)

__all__ = [
    # PyBricks classes (that needs to be exported)
    'Port',
    # Switch classes
    'SwitchPosition', 'SwitchMode', 'SwitchSensor', 'SwitchDistanceSensor',
    'SwitchIRSensor', 'SwitchUltrasonicSensor', 'SwitchColorSensor',
    'RemoteSensor', 'SmartSensor', 'SwitchMotor', 'SwitchController'
]