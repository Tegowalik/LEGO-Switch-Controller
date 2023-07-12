from switch import * #SwitchDistanceSensor, SwitchController, SwitchMotor, SmartSensor, SwitchPosition


# configure your switch layout here
pre_sensor = SwitchDistanceSensor(Port.A)
post_sensor = SwitchDistanceSensor(Port.B)
post_sensors = {(SwitchPosition.STRAIGHT,): post_sensor}
smart_sensor = SmartSensor(pre_sensor, post_sensors=post_sensors)

motor = SwitchMotor(Port.D, probability_curved_to_straight=0.8, probability_straight_to_curved=0.8)

controller = SwitchController()
controller.register_sensor(smart_sensor, motor)

# start the switch controller
controller.run()
