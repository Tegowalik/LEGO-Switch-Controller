from pybricks.hubs import CityHub
from pybricks.pupdevices import Motor, ColorDistanceSensor
from pybricks.parameters import Port, Direction, Button, Color, Stop
from pybricks.tools import wait
from urandom import random

hub = CityHub()
hub.system.set_stop_button(None)
hub.light.on(Color.ORANGE)
sensor = ColorDistanceSensor(Port.A)
motor = Motor(Port.B)
motor.reset_angle(0)

# the initial timeout in seconds. If no train/ wagon is detected for 
# initial_timeout_s seconds, it is assumed that the whole train has been passed 
# and the switch can randomly change direction. 
initial_timeout_s = 1.0 
dt = 50.0 # the time delta in milli seconds
timeout = int(initial_timeout_s * 1000 / dt)
critical_distance = 40
power = 500
turn = 50
stop_mode = Stop.BRAKE

# probability to switch from the initial position to the other one after a train has passed the sensor
p_init_to_not_init = 0.5
# probability to switch from the non-initial position to the initial one after a train has passed the sensor
p_not_init_to_init = 0.8  
# note since p_not_init_to_init > p_init_to_not_init the initial position is more likely

# calibrate the motor
angle1 = motor.run_until_stalled(power / 4)
angle2 = motor.run_until_stalled(-power / 4)

# move angles a little bit towards each other to prevent motor squeezing
diff = angle1 - angle2
angle1 = int(angle1 - diff/4.0)
angle2 = int(angle2 + diff/4.0)

init_angle = angle1 if angle1 < -angle2 else angle2
motor.run_target(power, init_angle, then=stop_mode)
angle = init_angle

def switch_angle():
    return angle1 if angle == angle2 else angle2


while Button.CENTER not in hub.button.pressed():
    d = sensor.distance()
    if d < critical_distance:
        timeout = int(initial_timeout_s * 1000 / dt)
        hub.light.on(Color.RED)
    else:
        if timeout > 0:
            timeout -= 1
            hub.light.on(Color.ORANGE)
        elif timeout == 0:
            timeout = -1
            hub.light.on(Color.GREEN)
            probability = p_init_to_not_init if angle == init_angle else p_not_init_to_init
            if random() < probability:
                angle = switch_angle()
                motor.run_target(power, angle, then=stop_mode, wait=False)
    wait(dt)

hub.light.on(Color.RED)
# move switch to initial position
if angle != init_angle:
    motor.run_target(power, init_angle, then=stop_mode)
hub.light.on(Color.GREEN)
wait(dt)
hub.system.shutdown()