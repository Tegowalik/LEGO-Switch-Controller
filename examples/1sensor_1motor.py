from pybricks.pupdevices import Motor, ColorDistanceSensor, InfraredSensor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Button, Color, Stop, Side
from pybricks.tools import wait, Matrix, vector
from pybricks.iodevices import PUPDevice
from pybricks.hubs import ThisHub
from urandom import random, uniform
from umath import ceil

def enum(**enums):
    return type('Enum', (), enums)

"""
SwitchPosition.STRAIGHT means a train would pass the switch in the straight 
direction.
SwitchPosition.CURVED means a train would pass the switch in the curved 
direction (either left or right).
"""
SwitchPosition = enum(STRAIGHT=0, CURVED=1)

"""
SwitchMode.RISING_EDGE means that the switch is randomly moved if an incoming 
train is detected in front of the sensor. This mode requires that the motors can 
complete the moving before the train.
reaches switch (depends on distance of sensor and switch)
SwitchPosition.FALLING_EDGE means that the switch is randomly moved after a 
train has been passed the switch/ sensor completly.
"""
SwitchMode = enum(RISING_EDGE=0, FALLING_EDGE=1)

"""
The very basic sensor for a switch. Use the concrete implementations like 
SwitchDistanceSensor to create a specific one or use the generic SwitchSensor()
method.
Note that the init_timeout depends on the dt-value (time in ms between two 
ticks) of the SwitchController. The default dt-value of 50ms combined with 
init_timeout of 20 means that after 20 * 50ms = 1s without sensor detection a 
train is considered to be passed completely.
"""
class SwitchSensor_():

    """
    Creates a SwitchSensor.

    params:
    -switch_mode: If FALLING_EDGE, the switch moves after a train has passed,
        if RISING_EDGE, the switch moves after a train has been detected and
        (hopefully) before the train has reached the switch. Since the moving
        takes a little bit, the distance between sensor and switch must be large
        enough and the speed of the train must not be too fast. That's why,
        FALLING_EDGE is recommended in general.
    -init_timeout: The initial timeout, which is the number of ticks the sensor
        needs to be unblocked, until a train is really considered to be passed.
        This is necessary since the sensor may become unblocked during a train
        passes (e.g. because of wagons). The time between two ticks is the 'dt'
        of the SwitchController (default dt=50ms, i.e. 20 ticks per second).
    -post_sensor_init_timeout: if this sensor is used as post-sensor, then this
        timeout refers to the number of ticks the sensor stays additionally
        blocked (after it becomes unblocked according to the usual timeouting).
        If post_sensor_init_timeout=100, dt=50ms, and init_timeout=20, then
        after a train passed the sensor, the track is considered to be blocked
        for another (20+100)*50ms = 6 seconds.
    -post_sensor_delay: number of ticks to delay the post_sensor_blocking 
        signal. If the delay is 100, dt=50ms, and a train passes this sensor, 
        the sensor will be blocked first after 50ms*100=5s (as post-sensor).
        This is especially useful if a train passing this post-sensor still 
        needs to drive some seconds until it reaches a potential point of 
        conflict with an output of another switch setup (where the post-sensor 
        is used).
    """
    def __init__(self, critical_distance, 
                switch_mode=SwitchMode.FALLING_EDGE, 
                init_timeout=20, 
                post_sensor_init_timeout=20, 
                post_sensor_delay=0):
        self.critical_distance = critical_distance
        self.init_timeout = init_timeout
        self.post_sensor_init_timeout = post_sensor_init_timeout + 1 # +1 because of internal purposess
        self.post_sensor_timeout = -1
        self.set_switch_mode(switch_mode) # initializes timeouts
        self.state = False
        n = ceil(post_sensor_delay / 8.0)
        self.delay = bytearray(n)
        self.delay_end = post_sensor_delay % 8
        self.post_sensor_delay = post_sensor_delay > 0
        self.blocked = False

    def __str__(self):
        return "%s(%s)" % (str(type(self))[8:-2], self.port)

    def tick(self):
        self._distance()
        self.state = self._tick()
        self.is_blocked()

    """
    Performs a 'tick' of the sensor. 
    
    The 'timeout' is used as following: the timeout is resetted (i. e. set to a
    positive number) if a train is currently detected in front of the train. If no
    train can be detected this value is decremented. The check is only successful
    if the timout is not positive anymore (i. e. some time has been passed
    since a train has been detected and we are not in between waggons by accident)
    and the a train is currently in front the sensor.
    """
    def _tick(self):
        if self.switch_mode == SwitchMode.RISING_EDGE:
            if self.distance < self.critical_distance:
                # a train is in front the sensor
                if self.timeout <= 0: 
                    self.reset()
                    return True
                self.reset()
            else:
                self.decrement()
        else:
            if self.distance > self.critical_distance:
                if self.timeout >= 0:
                    self.decrement()
            else:
                self.reset()

            if self.timeout == 0:
                # a train is not anymore in front
                self.timeout = -1
                return True

        return False

    def check(self):
        return self.state

    def is_currently_blocked(self):
        return self.timeout > 0

    def is_blocked(self):
        currently_blocked = self.is_currently_blocked()
        if currently_blocked:
            self.post_sensor_timeout = self.post_sensor_init_timeout
        elif self.post_sensor_timeout > 0:
            self.post_sensor_timeout -= 1
        
        blocked = self.post_sensor_timeout > 0 

        # delay the blocked signal (if post_sensor_delay > 0)
        if self.post_sensor_delay:
            self.blocked = self._delay_binary_state(int(blocked))
        else:
            self.blocked = blocked
        return self.blocked

    def _delay_binary_state(self, new_bit):
        out = self._get_nth_bit(self.delay[0], self.delay_end)

        # shift the bits in the byte array to the left by one bit
        for i in range(len(self.delay) - 1):
            b1 = self.delay[i]
            b2 = self.delay[i+1]
            bb2 = self._get_first_bit(b2)
            b1 = (b1 << 1) | ((1 << bb2) - 1)
            self.delay[i] = b1

        # shift the last byte to left + insert new bit
        self.delay[-1] = (self.delay[-1] << 1) | ((1 << new_bit) - 1)
        return out

    def _get_first_bit(self, byte):
        return self._get_nth_bit(byte, 0)

    def _get_nth_bit(self, byte, n):
        first_bit = (byte >> (7 - n)) & 1
        return first_bit

    def _distance(self):
        self.distance = self.sensor.distance()

    def decrement(self):
        self.timeout = max(0, self.timeout - 1)
        return 

    def reset(self):
        self.timeout = self.init_timeout

    def reset2wait(self):
        if self.switch_mode == SwitchMode.RISING_EDGE:
            self.timeout = self.init_timeout
        else:
            self.timeout = -1

    def set_init_timeout(self, init_timeout):
        self.init_timeout = init_timeout

    def set_switch_mode(self, switch_mode : SwitchMode):
        self.switch_mode = switch_mode
        if self.switch_mode == SwitchMode.RISING_EDGE:
            self.timeout = 0
        else:
            self.timeout = -1

    def sensors(self):
        return {self}

"""
A color distance sensor (LEGO item 88007)
"""
class SwitchDistanceSensor(SwitchSensor_):
    # critical distance in %
    def __init__(self, port : Port, critical_distance=30, *args, **kwargs):
        super().__init__(critical_distance, *args, **kwargs)
        self.sensor = ColorDistanceSensor(port)
        self.port = port

"""
The motion/ IR sensor known from LEGO WeDo 2.0 or the Grand Piano (LEGO item 20844)
"""
class SwitchIRSensor(SwitchSensor_):
    # critical distance in %
    def __init__(self, port : Port, critical_distance=60, *args, **kwargs):
        super().__init__(critical_distance, *args, **kwargs)
        self.sensor = InfraredSensor(port)
        self.port = port

"""
The ultrasonic sensor known from LEGO Mindstorms 51515 (LEGO part 37316c01)
"""
class SwitchUltrasonicSensor(SwitchSensor_):
    
    # critical distance in mm
    def __init__(self, port : Port, criticalDistance=120, *args, **kwargs):
        super().__init__(critical_distance, *args, **kwargs)
        self.sensor = UltrasonicSensor(port)
        self.port = port

"""
The color sensor known from LEGO Mindstorms 51515 (LEGO part 37308c01)
"""
class SwitchColorSensor(SwitchSensor_):
    # critical distance in %
    def __init__(self, port : Port, critical_distance=95, *args, **kwargs):
        super().__init__(critical_distance, *args, **kwargs)
        self.sensor = ColorSensor(port)
        self.port = port

    def distance(self):
        return 100 - self.sensor.reflection()

# a remote sensor i.e. a sensor that is connected to another hub
class SwitchRemoteSensor(SwitchSensor_):
    # todo implement (placeholder so far) (Issue2)
    pass

"""
Creates a SwitchSensor which fits the connected sensor type.
"""
def SwitchSensor(port: Port, *args, **kwargs):
    device = PUPDevice(port)
    info = device.info()
    device_id = info['id']

    # https://github.com/pybricks/technical-info/blob/master/assigned-numbers.md
    if device_id == 37:
        return SwitchDistanceSensor(port, *args, **kwargs)
    elif device_id == 61:
        return SwitchColorSensor(port, *args, **kwargs)
    elif device_id == 62:
        return SwitchUltrasonicSensor(port, *args, **kwargs)
    elif device_id == 35:
        return SwitchIRSensor(port, critical_distance, *args, **kwargs)
    else:
        raise ValueError("Unknown device on port %s" % port)

"""
A wrapper class for multiple sensors. 

To type of sensors are distinguished: pre- and post-sensors.

A pre-sensor can be any SwitchSensor and checks if the current switch is
blocked or not. Compared to the SwitchSensor, multiple pre-sensors can be
provided. This might be useful to prevent situations in which a train drives in
front of the (single) sensor, just after the switch moving started. This might
derail the train. This motivates to place the sensor as far away from the motor/
switch as possible. On the other hand, this can lead to derailments if a train
stops on the switch. That's why using multiple sensors might make your track
saver and leads to less crashes.

A post-sensor can also be any SwitchSensor which checks if an output of the
switch leads to a currently blocked track. Those sensors can still be used 
normally in another switch as well. You can even define the delay of such 
switches (using the post_sensor_delay option of the SwitchSensor) and a timeout
(using the post_sensor_init_timeout option of the SwitchSensor). The timeout
extends the blocking state of a post-sensor by the number of timeout cycles
(depends on dt of the controller, dt=100ms and post_sensor_init_timeout=20 means
the sensor stays 100ms*20=2s longer blocked - additionally to the init_timeout).   
"""
class SmartSensor:

    def __init__(self, *args, **kwargs):
        self.pre_sensors = list(args) + kwargs.get('pre_sensors', [])
        self.post_sensors = kwargs.get('post_sensors', {})
        self._sanitize_post_sensors()  
        self.update_timeout()
        self.update_init_timeout()
        self.state = (False, (False, []))  
        self.blocked = []  

    def __str__(self):
        pre_sensors = ", ".join([str(s) for s in self.pre_sensors])
        return "SmartSensor\n-Pre-Sensors: %s" % (pre_sensors)

    def _sanitize_post_sensors(self):
        for path1 in self.post_sensors:
            for path2 in self.post_sensors:
                if path1 != path2:
                    # check if path1 is subpath of path2 -> this is an error
                    if self._is_sub_path(path1, path2):
                        raise ValueError("The configuration of the post_sensors is invalid! Path <%s> and Path <%s> is a subpath/ superpath pair!" % (path2, path1))
   
    def _is_sub_path(self, path1, path2):
        for p1, p2 in zip(path1, path2):
            if p1 != p2:
                return False
        return len(path1) != len(path2)


    def add_pre_sensor(self, sensor):
        self.pre_sensors.append(sensor)
        self.update_timeout()
        self.update_init_timeout()

    def add_post_sensor(self, sensor, path):
        self.post_sensors[path] = sensor

    def update_timeout(self):
        self.timeout = max([s.timeout for s in self.pre_sensors])
    
    def update_init_timeout(self):
        self.init_timeout = max([s.init_timeout for s in self.pre_sensors])

    def tick(self):
        self.state = self._tick()
        self.update_timeout()

    """
    The core function of the SmartSensor.

    It checks for blocked paths and if any pre_sensor is activated (i.e. the 
    corresponding motor should move in this tick randomly) or is blocked (i.e.
    a train is in front of the sensor).
    """
    def _tick(self):
        post_conditions = [cond for cond, sensor in self.post_sensors.items() if sensor.blocked]
        # first check if any presensor fires
        any_activated = any(s.check() for s in self.pre_sensors)
        any_blocked = any(s.is_currently_blocked() for s in self.pre_sensors)
        if any_activated:
            for s in self.pre_sensors:
                s.reset2wait()

        self.post_sensors_blocked = [s.blocked for s in self.post_sensors.values()]

        return not any_blocked, (any_activated, post_conditions)

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

""" 
A representation of a motor for a switch.

The corresponding (hardware) motor must have a rotation sensor, like most of 
the Technic motors and all of the Mindstorm motors have.

Params:
-port: The port the motor is connected to, like Port.A
-switchPosition: the initial position of the switch
-probability_straight_to_curved: the probability that the switch moves after the
    sensor triggers and the switch is in the straight position. By default, the
    switch moves after every 2nd train
-probability_curved_to_straight: the probability that the switch moves after the 
    sensor triggers and the switch is in the curved position. By default, the
    switch moves after every 2nd train
- power: The power to use for the motors. Unless you have a good reason to 
    change it, leave the default (as it might influence the auto calibration)
- stop_mode: The stop mode of the motors. COAST means, that you can easily
    change the switch position yourself (since the motor is spinnning freely).
    If this is not wanted, change it to HOLD (Also see other options in PyBricks
    documentation)
-turn_degrees: If not None, this value is used as relative position for the 
    other switch position than given. If None, then an auto calibration is done.
    The auto calibration is recommended in general.
-direction: the default direction of the motor. This is only important if 
    turn_degrees is given
"""
class SwitchMotor:
    def __init__(self, 
            port : Port, 
            switch_position=SwitchPosition.STRAIGHT, 
            direction=Direction.CLOCKWISE,
            probability_straight_to_curved=0.5,
            probability_curved_to_straight=0.5,
            turn_degrees=None, # ~60 if no gears are needed
            power=750,
            stop_mode=Stop.COAST,
            display=None):
        self.probabilities = {SwitchPosition.STRAIGHT: probability_straight_to_curved,
                                SwitchPosition.CURVED: probability_curved_to_straight}
        self.switch_position = switch_position
        self.initial_position = switch_position
        self.motor = Motor(port, direction)
        self.port = port
        self.motor.reset_angle(0)
        self.motor.stop()
        self.successors = {}
        self.power = power
        self.stop_mode = stop_mode
        self.display = display
        self.next_path = None
        self._update()

        if turn_degrees is None:
            self.calibrate()
        else:
            other_switch_position = self.other_switch_position()
            self.angle = {switch_position: 0, other_switch_position: turn_degrees}

    def __str__(self):
        return self._string()

    def print(self, depth=0, post_sensors={}):
        print(self._string(depth=depth, post_sensors=post_sensors))

    def _string(self, depth=0, direction=None, post_sensors={}):
        def string_direction(direction):
            return "Direction." + ('STRAIGHT' if direction == SwitchPosition.STRAIGHT else 'CURVED')
        if direction:
            direction = 'STRAIGHT' if direction == SwitchPosition.STRAIGHT else 'CURVED'
            name = "%s: SwitchMotor(%s)" % (string_direction(direction), self.port)
        else:
            name = "SwitchMotor(%s)" % (self.port)

        if self in post_sensors:
            for direction, sensor in post_sensors[self]:
                name += "\n" + (depth + 1) * " " + "-" + string_direction(direction) + ": Post-Sensor: " + str(sensor)
        
        result = depth * " " + "-" + name 
        for position, motor in self.successors.items():
            post = {k: v[1:] for k, v in post_sensors.items() if v[0] == position}
            result += '\n' + motor._string(depth+1, position, post)
        return result

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

    """
    Registers a successor (i.e. another motor) for the given switch position,
    i.e. register_successor(motor2, SwitchPosition.STRAIGHT) means, that after
    this motor in straight direction is another switch with motor2 connected to
    it.
    """
    def register_successor(self, successor : SwitchMotor, switch_position : SwitchPosition):
        self.successors[switch_position] = successor
        self._update()

    def move(self):
        if self.display is not None:
            self.display.cross()
        if self.switch_position == SwitchPosition.STRAIGHT:
            self.switch_position = SwitchPosition.CURVED
        elif self.switch_position == SwitchPosition.CURVED:
            self.switch_position = SwitchPosition.STRAIGHT
        angle = self.angle[self.switch_position]
        self.motor.run_target(self.power, angle, then=self.stop_mode, wait=True)      

    """
    Moves randomly this switch position (and its successor positions).
    """
    def move_random(self):
        if random() < self.probabilities[self.switch_position]:
            self.move()
        self.move_successor_random()

    """
    Performes a smart moving of this motors switch direction and its successors.

    'Smart' means that a path is selected that is not blocked according to the
    given parameters. 
    If a the switch needed to move because of a blocked sensor, it tries to move
    back to this position if this sensor becomes unblocked again later.
    Besides of this smart behavior, this method still randomizes i.e. if
    multiple paths are available, a random path is moved to (satisfying the
    configured probability distribution).
    """
    def move_smart(self, check: bool, blocked_paths: list):
        current_path = self.current_path()
        path_candidates = [p for p in self.all_paths if p not in blocked_paths + [current_path]]

        if self.next_path in path_candidates:
            # go back to the last path that has been blocked before, but is free again
            self.move_path(self.next_path)
            self.next_path = None
        else:
            needs2move = current_path in blocked_paths
            if (check and random() < self.probabilities[self.switch_position]) or needs2move:
                # we need to move (at least if a new path is available)         
                if len(path_candidates) == 0:
                    # no 'good' path is available, so stay for now, and probably 
                    pass
                else:
                    # choose random path based on probabilities!!!
                    path_weights = self._get_path_probabilities(path_candidates)
                    path = self._get_random_path(path_candidates, path_weights)
                    
                    self.move_path(path)

                    if needs2move:
                        # make sure to move back to the currently blocked path once this path is free again
                        self.next_path = current_path
                    else:
                        self.next_path = None

    def _update(self):
        self.all_paths = [tuple(p) for p in self._all_paths()]

    """
    Iterates over all switch paths in this layout. 

    If this switch has no successors at all, the only paths are
    [(STRAIGHT,), (CURVED,)].

    If only the STRAIGHT position has a successor which has no successors, the
    paths are [(STRAIGHT, STRAIGHT), (STRAIGHT, CURVED), (CURVED,)], etc...
    """
    def _all_paths(self):
        for position in [SwitchPosition.STRAIGHT, SwitchPosition.CURVED]:
            if position not in self.successors:
                yield [position]

        for position, motor in self.successors.items():
            for path in motor._all_paths():
                yield [position] + path

    def move_path(self, path):
        if path[0] != self.switch_position:
            self.move()
        if self.switch_position in self.successors:
            self.successors[self.switch_position].move_path(path[1:])

    def current_path(self, as_tuple=True):
        path = [self.switch_position]
        if self.switch_position in self.successors:
            path += self.successors[self.switch_position].current_path(as_tuple=False)

        if as_tuple:
            return tuple(path)
        else:
            return path

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

    """
    Calcualates the probability for a switch path. 

    This probability depends on probability_straight_to_curved and
    probability_curved_to_straight. 
    For example, if the switch has currently position CURVED and the given path
    requires the switch position STRAIGHT, the probability_curved_to_straight
    is used. If the path requires switch position CURVED, the switch needs to
    stay in this position (with probability 1 - probability_curved_to_straight).
    This concept is apllied recursively to successors and the corresponding 
    subpaths.
    """
    def _get_path_probabilities(self, paths):
        probs = self._determine_path_probabilities(paths)
        return probs

    def _determine_path_probabilities(self, states, num_steps=5):
        if len(states) == 1:
            return [1]

        state_vector = Matrix([[1.0/len(states)] * len(states)])

        rows = []
        for path1 in states:
            column = []
            for path2 in states:
                column.append(self._get_transition_probability(path1, path2))
            rows.append(column)
        transition_matrix = Matrix(rows)

        for _ in range(num_steps):
            state_vector = state_vector * transition_matrix

        return state_vector

    def _get_transition_probability(self, path1, path2):
        switches_to_move_probs = []
        motor = self
        for i, (p1, p2) in enumerate(zip(path1, path2)):
            if p1 != p2:
                prob1 = motor.probabilities[p1] # probability from p1 -> p2
                switches_to_move_probs.append(prob1)
                break
            else:
                if p1 in self.successors:
                    motor = self.successors[p1]
                else:
                    # end of loop
                    break
        else:
            return 1 # identical paths

        for j in range(i, len(path2)-1):
            motor = motor.successors[path2[j]]
            if motor.switch_position != path2[j+1]:
                prob = motor.probabilities[motor.switch_position]
                switches_to_move_probs.append(prob)

        if len(switches_to_move_probs) == 0:
            return 1
        else:
            prod = 1
            for p in switches_to_move_probs:
                prod *= p
            return prod



    """
    Returns a random path out of the given path with optional weighted 
    probabilities. This has a similar behaviour as the ususal python 
    implementation of random.choices(paths, weights=weights, k=1)[0].
    """
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

    def update(self, timeouts, init_timeouts, blocked=None):
        amount = len(timeouts)
        if amount == 1:
            self.update_one(timeouts, init_timeouts, blocked)
        elif amount == 2:
            self.update_two(timeouts, init_timeouts, None) # blocked not supported yet for > 1 SmartSensor
        elif amount == 3:
            self.update_three(timeouts, init_timeouts, None) # blocked not supported yet for > 1 SmartSensor
        else:
            raise ValueError("Unknown amount <%s>" % amount)

    def _convert(self, pixel_number, total_pixel, proportion):
        if pixel_number / total_pixel <= proportion:
            return 100
        elif (pixel_number - 1) / total_pixel <= proportion:
            return  int(100 * (total_pixel * proportion - (pixel_number - 1)))
        else:
            return 0

    def _blocked_row(self, blocked):
        b = [100 * int(b) for b in blocked][:5]
        l = len(b)
        if l < 5:
            b = b + [0] * (5 - l)
        return b


    def update_one(self, timeouts, init_timeouts, blocked):
        proportion = timeouts[0] / init_timeouts[0]
        width = 5
        height = 5
        matrix = []
        if blocked:
            blocked = blocked[0]
            l = len(blocked)
            if l > 0:
                height = 4
                blocked_row = [100 * int(b) for b in blocked][:5]
                if l < 5:
                    blocked_row = blocked_row + [0] * (5 - l)

                matrix = [blocked_row]

        matrix += [[self._convert(j * width + i + 1, height * width, proportion) for i in range(width)] for j in range(height)]
        self.hub.display.icon(matrix)
    
    def update_two(self, timeouts, init_timeouts, blocked):
        data = []
        matrix = []
        width = 5
        height = 5
        if blocked:
            if any(len(b) > 0 for b in blocked):
                blocked_row = []
                height = height - 1

                for i, b in enumerate(blocked):
                    l = len(b)
                    
                    if l > 0:
                        b = [100 * int(bb) for bb in b][:2]
                        l = len(b)
                        if l < 2:
                            blocked_row += b + [0] * (2 - l)
                        else:
                            blocked_row = b

                        if i == 0:
                            blocked_row += [0]
                    else:
                        blocked_row += [0, 0]

                
                matrix = [blocked_row]

        for index in range(2):
            proportion = timeouts[index] / init_timeouts[index]
            m = [[self._convert(j * 2 + i + 1, 10, proportion) for i in range(2)] for j in range(height)]
            data.append(m)
        matrix += [[data[0][i][0], data[0][i][1], 0, data[1][i][0], data[1][i][1]] for i in range(height)]
        self.hub.display.icon(matrix)

    def update_three(self, timeouts, init_timeouts, blocked):
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
            self.display = LightMatrix(self.hub)
        else:
            self.display = None
        self._update()
        
    def register_sensor(self, sensor : SwitchSensor, motor):
        self.sensors[sensor] = motor
        self.sensor_list.append(sensor)
        motor.set_display(self.display)
        self._update()

    def buttons(self):
        if hasattr(self.hub, 'buttons'):
            return self.hub.buttons.pressed()
        elif hasattr(self.hub, 'button'):
            return self.hub.button.pressed()
        else:
            raise ValueError()

    def run(self):
        self.print()
        while Button.CENTER not in self.buttons():
            self.tick()
            wait(self.dt)
        self.color(Color.BLUE)
        self.reset()
        self.hub.system.shutdown()

    def print(self):
        print("Start SwitchController")
        for sensor, motor in self.sensors.items():
            print("Sensor: %s" % sensor)
            post_sensors = {}
            if isinstance(sensor, SmartSensor):
                for path, post in sensor.post_sensors.items():
                    m = motor
                    for p in path[:-1]:
                        m = m.successors[p]
                    
                    pair = (path, post)
                    if m in post_sensors:
                        post_sensors[m].append(pair)
                    else:
                        post_sensors[m] = [pair]

            motor.print(depth=1, post_sensors=post_sensors)

    def tick(self):
        for sensor in self.all_sensors:
            sensor.tick()

        blocked = None
        for sensor in self.sensors:
            check = sensor.check()
            if check is True:
                self.color(Color.RED)
                self.sensors[sensor].move_random()
            elif isinstance(check, tuple) and check[0]:
                self.color(Color.RED)
                self.sensors[sensor].move_smart(*check[1])
                blocked = [sensor.post_sensors_blocked if hasattr(sensor, 'post_sensors_blocked') else [] for sensor in self.sensor_list]
        
        timeouts = [sensor.timeout for sensor in self.sensor_list]
        max_timeout = max(timeouts)
        init_timeouts = [sensor.init_timeout for sensor in self.sensor_list]
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
            self.display.update(timeouts, init_timeouts, blocked)

    def _update(self):
        self.all_sensors = list(self._all_sensors())

    def _all_sensors(self):
        sensors = []
        for s in self.sensors:
            for ss in s.sensors():
                if ss not in sensors:
                    yield ss
                    sensors.append(ss)
                if s not in sensors:
                    yield s
                    sensors.append(s)

    def reset(self):
        for motor in self.sensors.values():
            motor.reset()

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
    'RemoteSensor', 'SwitchSensor', 'SmartSensor', 'SwitchMotor', 'SwitchController'
]


controller = SwitchController()

sensor = SwitchSensor(Port.A, critical_distance=70)
motor = SwitchMotor(Port.B, probability_curved_to_straight=0.8, probability_straight_to_curved=0.8)
controller.register_sensor(sensor, motor)

# start the switch controller
controller.run()
