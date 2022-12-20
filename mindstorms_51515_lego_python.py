from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import random


# Create your objects here.
hub = MSHub()
hub.status_light.on('orange')
sensor = DistanceSensor('A')
motor = Motor('B')

timeout = 10
power = 100
turn = 150

while not (hub.left_button.is_pressed() or hub.right_button.is_pressed()):
    dt = 0.05
    distance = sensor.get_distance_cm()
    if distance is None:
        distance = 100
    print(distance)
    print(timeout)
    if less_than(distance, 10):
        timeout = 30
        hub.status_light.on('red')
        hub.light_matrix.show('99999:99999:99999:99999:99999')
    else:
        if greater_than(timeout, 0):
            timeout -= 1
            hub.status_light.on('orange')
            if less_than(timeout, 25):
                hub.light_matrix.set_pixel(timeout % 5, int((timeout) / 5), 0)
        elif timeout == 0:
            timeout = -1
            hub.status_light.on('green')
            if random.random() < 0.7:
                motor.run_for_degrees(turn, power)
                power *= -1

    wait_for_seconds(dt)

# reset
if power < 0:
    motor.run_for_degrees(turn, power)
hub.status_light.off()