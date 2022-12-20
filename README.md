# Pybricks Switch Controller
Automate your LEGO train tracks by randomly change the direction of switches by detecting incoming trains. An example usage is presented here: https://youtu.be/EsnzuTQ5WIw?t=199

In principle, all the programs work in the same way: Trains are detected by an distance sensor which causes the switch to change direction (at least with some probability). The reason for the different program files consists in
- the different hardware components (powered up City Hub/ Technic Hub, MINDSTORMS Robot Inventor 51515, MINDSTORMS EV3 31313, Spike Prime)
- the different possible switch layouts (1 sensor + 1 switch, 1 sensor + 2 switches in a row, 2 sensors with 1 switch each, ...)

Most of the provided programs are running [PyBricks](https://pybricks.com/) code. However, for LEGO MINDSTORMs EV3 (31313) [EV3 MicroPython](https://pybricks.com/ev3-micropython/) is used. The LEGO MINDSTORMS Robot Inventor (51515) can be used either with PyBricks or with the official [LEGO MINDSTORMS Software with Python Programming](https://lego.github.io/MINDSTORMS-Robot-Inventor-hub-API/).

To get the motor rotation change the direction of the switch, a design of [SteinaufStein](https://www.youtube.com/channel/UCJ-c1vQHVZZ6S6xhjjNo7Gg) is used ([video tutorial](https://youtu.be/Jwv6kI0IBoQ?t=63)). Note that for some motors (like most of the powered up motors) an additional gear ration is needed since the motors are too weak to move. 
<img src="img/switch_gear_ratio.jpg" width="300">

## Powered Up Hubs
All the programs for powered up hubs are running [PyBricks](https://pybricks.com/) code. The following description uses some PyBricks specific terms, so read their [documentation](https://docs.pybricks.com/en/stable/) to understand details. Also refer to [here](https://code.pybricks.com/) in order to actually run the provided python code on your powered up hubs.

For controlling the switches, you can use any type of motor with rotation sensor being compatible with the powered up system. The following picture from the (PyBricks Documentation](https://docs.pybricks.com/en/latest/pupdevices/index.html) shows the compatible motors.
<img src="img/motors.jpg" width="600">
These motors occur in motorized LEGO Technic Sets (like Liebherr R 9800 Excavator (42100), App-Controlled Cat® D11 Bulldozer (42131)) and in LEGO MINDSTORMS/ SPIKE sets (like Robot Inventor (51515), SPIKE Prime Set (45678)). 

As sensor any sensor which can determine a distance is possible. The pictures are again taken from the (PyBricks Documentation](https://docs.pybricks.com/en/latest/pupdevices/index.html).

| **Sensor** | **Color & Distance Sensor** | **Infrared/ Motion Sensor** | **Ultrasonic Sensor** | **Color Sensor** |
|-|-|-|-|-|
| **Python Class name** | `SwitchDistanceSensor` | `SwitchIRSensor` | `SwitchUltrasonicSensor` | `SwitchColorSensor` | 
| **LEGO item/ part number** | item 88007 | item 20844 | part 37316c01 | part 37308c01 |
| **LEGO sets with this sensor** | BOOST Creative Toolbox (17101), Droid Commander (75253), [sold as single item at LEGO store](https://www.lego.com/en-us/product/color-distance-sensor-88007) |  Grand Piano (21323), WeDo 2.0 Core Set (45300) | Robot Inventor (51515), SPIKE Prime Set (45678) | Robot Inventor (51515), SPIKE Essential Set (45345), SPIKE Prime Expansion Set (45681), SPIKE Prime Set (45678) |
| **Picture** | <img src="img/ColorDistanceSensor.png" width="200"> | <img src="img/InfraredSensor.png" width="200"> | <img src="img/UltrasonicSensor.png" width="200"> | <img src="img/ColorSensor.png" width="200"> |

Since all sensors except the Color & Distance Sensor is used only in MINDSTORMS/ SPIKE sets (which are EOL 2022), this sensor seems to be the most suitable - also because it is sold individually by LEGO and is relatively cheap.

Once you have organized the hub, motor(s) and sensor(s), you are ready to run the program. Therefore you need a hub dependant *code basis* and a switch layout dependant *configuration part*

### Powered Up Code Basis
| City Hub | [CityHub.py](CityHub.py) |
|-|-|
| Technic Hub | [TechnicHub.py](TechnicHub.py) |

### Powered Up Configuration Part
Depending on your actual switch layout, you need to add a few lines to the program right below the line `# configure your switch layout here`.

The following examples should cover the most important switch-sensor-motor-combinations. You might need to make little changes (like changing the used sensor type, port or parameter values). The provided *Easy Code* is a minimal working code example for the given setup. The *Advanced Code* shows which parameters can be used to modify the behaviour.

<table>
<tr>
  <td>Description </td> <td>Picture </td> <td>Easy Code </td> <td>Advanced Code</td>
</tr>
<tr>
  <td>1 Sensor + 1 Switch </td> <td>TODO</td>
<td>

```python
sensor = SwitchDistanceSensor(Port.A)
  
motor = SwitchMotor(Port.B)
  
controller.registerSensor(sensor, motor)
```

  </td><td>

```python
# create a SwitchDistanceSensor with higher critical distance (60) 
# instead of the default value 40 
# -> sensor will trigger if object is in front with distance 
# less than 40 (no unit; value means proportion of reflected light)
# -> sensor can be placed further away from the tracks
  
sensor = SwitchDistanceSensor(Port.A, criticalDistance=60)
# probability_straigth_to_curved > probability_curved_to_straigth 
# means that the switch will be more often in the curved state 
# than in the straight one
motor = SwitchMotor(Port.B, 
                    probability_curved_to_straigth=0.5, 
                    probability_straigth_to_curved=0.8,
                    switchPosition=SwitchPosition.STRAIGHT)
  
controller.registerSensor(sensor, motor)
```

  </td>
</tr>
<tr>
<td> 1 Sensor + 2 Motors </td>
  <td>TODO</td>
<td>

```python
sensor = SwitchDistanceSensor(Port.A)
  
motor1 = SwitchMotor(Port.B)
motor2 = SwitchMotor(Port.C)
motor1.registerSuccessor(motor2, SwitchPosition.CURVED)
  
controller.registerSensor(sensor, motor)
```

  </td><td>

```python  
sensor = SwitchDistanceSensor(Port.A, criticalDistance=60)

motor1 = SwitchMotor(Port.B, switchposition=SwitchPosition.CURVED)
motor2 = SwitchMotor(Port.C, 
                    probability_curved_to_straigth=0.5, 
                    probability_straigth_to_curved=0.8)
motor1.registerSuccessor(motor2, SwitchPosition.CURVED)
  
controller.registerSensor(sensor, motor)
```

  </td>
</tr>
  <tr>
<td> 1 Sensor + 3 Motors </td>
  <td>TODO</td>
<td>

```python
sensor = SwitchDistanceSensor(Port.A)
  
motor1 = SwitchMotor(Port.B)
motor2 = SwitchMotor(Port.C)
motor3 = SwitchMotor(Port.D)
motor1.registerSuccessor(motor2, SwitchPosition.CURVED)
motor1.registerSuccessor(motor3, SwitchPosition.STRAIGHT)
  
controller.registerSensor(sensor, motor)
```

  </td><td>

```python  
sensor = SwitchDistanceSensor(Port.A, criticalDistance=30)
# Set the initial timeout value to 20 (default=40).
# Note that the init_timeout depends on the dt-value 
# (time in ms between two ticks) of the SwitchController.
# The default dt-value of 50ms combined with init_timeout of 20 
# means that after 20 * 50ms = 1s without sensor detection 
# a train is considered to be passed completely.
sensor.set_init_timeout(20)

motor1 = SwitchMotor(Port.B, switchposition=SwitchPosition.CURVED)
motor2 = SwitchMotor(Port.C, 
                    probability_straigth_to_curved=0.8)
motor3 = SwitchMotor(Port.D, 
                     probability_straigth_to_curved=1.0, 
                     probability_curved_to_straigth=1.0,
                     switchPosition=SwitchPosition.CURVED)
motor1.registerSuccessor(motor2, SwitchPosition.CURVED)
motor1.registerSuccessor(motor3, SwitchPosition.STRAIGHT)
  
controller.registerSensor(sensor, motor)
```

  </td>
</tr>
    <tr>
<td> 1 Sensor + 3 Motors </td>
  <td>TODO</td>
<td>

```python
sensor1 = SwitchIRSensor(Port.A)
sensor2 = SwitchUltrasonicSensor(Port.C)
  
motor1 = SwitchMotor(Port.B)
motor2 = SwitchMotor(Port.D)
  
controller.registerSensor(sensor1, motor1)
controller.registerSensor(sensor2, motor2)
```

  </td><td>

```python  
sensor1 = SwitchIR(Port.A, criticalDistance=30)
sensor2 = SwitchUltrasonicSensor(Port.A, criticalDistance=400)
sensor2.set_init_timeout(600)

motor1 = SwitchMotor(Port.B, 
                     switchposition=SwitchPosition.CURVED,
                     probability_straigth_to_curved=1.0, 
                     probability_curved_to_straigth=1.0,)
motor2 = SwitchMotor(Port.C, 
                    switchPosition=SwitchPosition.STRAIGHT,
                    probability_straigth_to_curved=0.8)
  
controller.registerSensor(sensor1, motor2)
controller.registerSensor(sensor2, motor2)
```

  </td>
</tr>
</table>

Note that for the [City Hub](https://www.lego.com/en-us/product/hub-88009) (the hub used for the City trains), only the first example can be used since only two ports are available. In particular, another special program is available for this case which is easier to understand (esspecially if you are not familiar with object oriented programming): [CityHub_easy.py](CityHub_easy.py).

Personally, I recommend to first running the program without including the current program to the firmware. So you can easily experiment different settings and see what fits your purposes best (errors can be seen in the terminal). Once the program is ready flash the hub with including the current program to the firmware (Currently this option is available under "Settings" -> "Firmware" -> "Include current program"). This causes that flashed program is executed whenever the hub is started in the future - unless you reflash it again. You can easily reflash the original LEGO firmware by connecting the hub to the powered up app. The disadvantage of the flashing the program to the firmware is that you can no longer see the terminal output, so make sure that the program runs without errors before doing this.

### Special Features
- **Colors**
  - RED: Switch is currently moving the direction. No train should now be passing the switch!
  - Orange: Currently a switch is detected in front of the sensor
  - Yellow: Currently no train is in front of the sensor, but was a short time ago (so either the transition of two wagons is in front of the sensor or the train passed completely the sensor)
  - Green: otherwise (sensor is waiting for an incoming train)
  - In case of the multiple sensor programs, the first color in the list is shown whose condition is true for at least one sensor
- **Power Off**: Use the green button of the hub to power the controller off. This might cause resetting the switches to the initial state.
- **Probabilities** TODO
- **Motor Auto Calibration** TODO (also add code)
- **Critical Distances** TODO


## MINDSTORMS (Robot Inventor 51515, SPIKE Prime 45678)
The [PyBricks](https://pybricks.com/) code for these hubs works similar to the ones using the Powered Up Hubs. You just need to use the special code basis: [MINDSTORMS_51515.py](MINDSTORMS_51515.py). (I haven't tested it for the SPIKE Prime, but according to the PyBricks documentation, the code should work as well).
Using this code basis, all [Powered Up Configuration Examples](#Powered_Up_Configuration_Part) can also be used for the MINDSTORMS Hubs. But because of the additional available ports, even more (complex) configurations become possible:


<table>
<tr>
  <td>Description </td> <td>Picture </td> <td>Easy Code </td> <td>Advanced Code</td>
</tr>
<tr>
  <td>2 Sensor + 3 Switch </td> <td>TODO</td>
<td>

```python
sensor = SwitchDistanceSensor(Port.A)
  
motor = SwitchMotor(Port.B)
  
controller.registerSensor(sensor, motor)
```

  </td><td>

```python
# create a SwitchDistanceSensor with higher critical distance (60) 
# instead of the default value 40 
# -> sensor will trigger if object is in front with distance 
# less than 40 (no unit; value means proportion of reflected light)
# -> sensor can be placed further away from the tracks
  
sensor = SwitchDistanceSensor(Port.A, criticalDistance=60)
# probability_straigth_to_curved > probability_curved_to_straigth 
# means that the switch will be more often in the curved state 
# than in the straight one
motor = SwitchMotor(Port.B, 
                    probability_curved_to_straigth=0.5, 
                    probability_straigth_to_curved=0.8,
                    switchPosition=SwitchPosition.STRAIGHT)
  
controller.registerSensor(sensor, motor)
```

  </td>
</tr>
 TODO 2 sensor, 4 motor
  TODO 3 sensor, 3 motor
</table>


In case you don't want to flash your MINDSTORMS with PyBricks firmware, you can still use a version for the official LEGO Mindstorms Software with Python Programming: [MINDSTORMS_51515.lms](MINDSTORMS_51515.lms)/ [MINDSTORMS_51515_LEGO_python.py](MINDSTORMS_51515_LEGO_python.py). However, because of the very limited functionality of the programming language, only a 1 Switch + 1 Motor layout is provided (with less modification possibilities compared to the PyBricks version). 

### Special Features
Additionally to the Powered Up Hub Speical Features the light matrix is used to indicate the progress of the sensor timeout. Depending on the number of sensors the color matrix shows progress bar(s) indicating the timeout progress.

TODO add gifs

## MINDSTORMS EV3 (31313)
To run python programs on an EV3, you first need to follow these [instructions](https://pybricks.com/install/mindstorms-ev3/installation/). After that you can use the following programs:

|Description | Image | Program |
|-|-|-|
|2 Sensors + 2 XL Motors | TODO| [program](ev3_switch_1_1_XL_XL.py)|
|1 Sensor + 2 XL Motors | TODO| [program](ev3_switch_2_XL_XL.py)|
|2 Sensors + 2 XL Motors + 1 M Motor | TODO| [program](ev3_switch_2_1_XL_M_XL.py)|

Of course not all possible combinations of sensors and motors are provided. In addition the programs aren't that flexible as the PyBricks ones. However the basic idea how to adjust the code for a certain sensor-motor-layout should be obvious.

## Known Issues
- The variable/ method naming in the python files mixes CamelCasing and snake_casing. As a programmer, I really regret that I haven't been consistently using a case system. However I don't have neither the time nor the motivation to make the naming consistent.
- As soon as communication between hubs is possible, this makes a lot of new features possible (large chained layouts are possible -> no limitation due to limited available ports). Furthermore, it would be awesome if PyBricks Hubs could connect to a app which supervises *all* hubs.

If you find any unexpected behaviour or have a feature request, please create an issue or a pull request.
