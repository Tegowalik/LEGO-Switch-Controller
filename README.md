# Pybricks Switch Controller
Automate your LEGO train tracks by randomly change the direction of switches by detecting incoming trains. An example usage is presented here: https://youtu.be/EsnzuTQ5WIw?t=199

In principle, all the programs work in the same way: Trains are detected by an distance sensor which causes the switch to change direction (at least with some probability). The reason for the different program files consists in
- the different hardware components (powered up City Hub/ Technic Hub, Mindstorms Hub 51515, Mindstorms EV3 31313)
- the different possible switch layouts (1 sensor + 1 switch, 1 sensor + 2 switches in a row, 2 sensors with 1 switch each, ...).

Unfortunately depending on the harware type, different ways of programming is required. 

To get the motor change the direction of the switch, a design of [SteinaufStein](https://www.youtube.com/channel/UCJ-c1vQHVZZ6S6xhjjNo7Gg) is used ([video tutorial](https://youtu.be/Jwv6kI0IBoQ?t=63)). Note that for some motors (like most of the powered up motors) an additional gear ration is needed since the motors are too weak to move. 

TODO common variables that might need to be adjusted 

## Powered Up Hubs
The programs for powered up hubs are running [PyBricks](https://pybricks.com/) code. The following description uses some PyBricks specific terms, so read their [documentation](https://docs.pybricks.com/en/stable/) to understand details. Also refer to [here](https://code.pybricks.com/) in order to actually run the provided python code on your powered up hubs.

For controlling the switches, you can use any type of motor with rotation sensor being compatible with the powered up system. # TODO picture
As sensor any sensor which can determine a distance is possible. Anyway in the provided programs, only the ColorDistanceSensor is used. TODO picture
In order to use a different senosr instead, you would need to change a few lines of the program: 
- For 1 sensor + 1 switch: replace any occurence in the program of *ColorDistanceSensor* by the name of your device (like *InfraredSensor*, *ColorSensor* or *UltrasonicSensor*)
- For all other programs: Use the corresponding SwitchSensor implementation, i.e. *SwitchDistanceSensor* (used in the program), *SwitchIRSensor*, *SwitchUltrasonicSensor* or *SwitchColorSensor* 

|Description | Image | Programs |
|-|-|-|-|
|1 Sensor + 1 Switch | TODO with Ports | [CityHub](powered_up_switch_1_City_Hub.py), [TechnicHub](powered_up_switch_1_Technic_Hub.py) |
|1 Sensor + 2 Switchs | | |
|1 Sensor + 3 Switches | | |
|2 Sensors + 2 Switches | | | 

Note that the structure of the 1 sensor + 1 switch program differs completely compared to the other programs which are using a common code basis with object oriented programming. Actually the 1 sensor + 1 switch functionality can be easily achieved using the object oriented approach as well (the object oriented code basis is much more powerful, flexible and complicated). But the provided programs for 1 sensor + 1 switch are much easier to understand than the object oriented ones, so use whatever fits your needs best.

### Special Features
- **Colors**
  - RED: Switch is currently moving the direction. No train should now be passing the switch!
  - Orange: Currently a switch is detected in front of the sensor
  - Yellow: Currently no train is in front of the sensor, but was a short time ago (so either the transition of two wagons is in front of the sensor or the train passed completely the sensor)
  - Green: otherwise
  - In case of the two sensor program, the first color in the list is shown whose condition is true for at least one sensor
- **Power Off**: Use the green button of the hub to power the controller off. This might cause resetting the switches to the initial state.


## Mindstorms (Robot Inventor 51515, Spike Prime 45678)
Currently only a 1 sensor + 1 switch design is [available](51515_switch_1_1.lms). You can run it by using the official LEGO Mindstorms Software with Python Programming.

## EV3 (31313)
To run python programs on an EV3, you first need to follow these [instructions](https://pybricks.com/install/mindstorms-ev3/installation/). After that you can use the following programs:

|Description | Image | Program |
|-|-|-|
|2 Sensors + 2 XL Motors | TODO| [program](ev3_switch_1_1_XL_XL.py)|
|1 Sensor + 2 XL Motors | TODO| [program](ev3_switch_2_XL_XL.py)|
|2 Sensors + 2 XL Motors + 1 M Motor | TODO| [program](ev3_switch_2_1_XL_M_XL.py)|

Of course not all possible combinations of sensors and motors are provided. However the basic idea how to adjust the code for a certain sensor-motor-layout should be obvious. Also note that the probabilities to turn the switch are not programmed that detailed as in the previous programs.
