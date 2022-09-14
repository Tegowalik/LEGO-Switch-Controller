# Pybricks Switch Controller
Automate your LEGO train tracks by randomly change the direction of switches by detecting incoming trains. An example usage is presented here: https://www.youtube.com/watch?v=EsnzuTQ5WIw&t=317s 

In principle, all the programs work in the same way: Trains are detected by an distance sensor which causes the switch to change direction (at least with some probability). The reason for the different program files consists in
- the different hardware components (powered up City Hub/ Technic Hub, Mindstorms Hub 51515, Mindstorms EV3 31313)
- the different possible switch layouts (1 sensor + 1 switch, 1 sensor + 2 switches in a row, 2 sensors with 1 switch each, ...).

Unfortunately depending on the harware type, different ways of programming is required. 

To get the motor change the direction of the switch, a design of [SteinaufStein](https://www.youtube.com/channel/UCJ-c1vQHVZZ6S6xhjjNo7Gg) is used ([video tutorial](https://youtu.be/Jwv6kI0IBoQ?t=63)). Note that for some motors (like most of the powered up motors) an additional gear ration is needed since the motors are too weak to move. 

TODO common variables that might need to be adjusted 

## Powered Up Hubs
The programs for powered up hubs are running using [PyBricks](https://pybricks.com/). The following description uses some PyBricks specific terms, so read their [documentation](https://docs.pybricks.com/en/stable/) to understand details. Also refer to [here](https://code.pybricks.com/) in order to actually run the provided python code on your powered up hubs.

For controlling the switches, you can use any type of motor with rotation sensor being compatible with the powered up system. # TODO picture
As sensor any sensor which can determine a distance is possible. Anyway in the provided programs, only the ColorDistanceSensor is used. TODO picture
In order to use a different senosr instead, you would need to change a few lines of the program: Basically replace any occurence in the program of *ColorDistanceSensor* by the name of your device (like *InfraredSensor*, *ColorSensor* or *UltrasonicSensor*).



|Description | Image | Technic Hub | City Hub |
|-|-|-|-|
|1 Sensor + 1 Switch | TODO with Ports | TOOD | TODO |
|1 Sensor + 2 Switchs | | | |
|1 Sensor + 3 Switches | | | |
|2 Sensors + 2 Switches | | | | 

### Special Features
- **Colors**
  - RED: Switch is currently moving the direction. No train should now be passing the switch!
  - Orange: Currently a switch is detected in front of the sensor
  - Yellow: Currently no train is in front of the sensor, but was a short time ago (so either the transition of two wagons is in front of the sensor or the train passed completely the sensor)
  - Green: otherwise
  - In case of the two sensor program, the first color in the list is shown whose condition is true for at least one sensor
- **Battery Power**: To indicate the state of charge of the battery, the shown color switches the brightness each second. 1st second the full brightness is visible, 2nd second the brightness is only the remaining state of charge, so one can detect the contrast. To control this behavior, change the variables min_voltage and max_voltage. In particular, max_voltage should be 6\*1.2V = 7.2V, but is set to a lower value, s.t. the blinking will start only after some hours (like when only 50% of the capacity is left). Note that estimating the *true* state of charge is not trivial at all and the given predictor is very naive and works only as simple indicator that the battery might be empty soon. For hubs running the switch controller code are working fine for more than 10 hours without battery problems.
- **Power Off**: Use the green button of the hub to power the controller off. This might cause resetting the switches to the initial state.


## EV3 (31313)



