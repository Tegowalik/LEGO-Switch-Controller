

switch_file = open('../switch.py', 'r+').readlines()

suffixes = {
    '1sensor_1motor': [
        "controller = SwitchController()",
        "",
        "sensor = SwitchSensor(Port.A, critical_distance=70)",
        "motor = SwitchMotor(Port.B, probability_curved_to_straight=0.8, probability_straight_to_curved=0.8)",
        "controller.register_sensor(sensor, motor)",
        "",
        "# start the switch controller",
        "controller.run()"
    ],
    'mindstorms_51515_1_1': [
        "hub = ThisHub()",
        "hub.display.orientation(Side.BOTTOM)",
        "controller = SwitchController(hub)",
        "",
        "# configure your switch layout here",
        "sensor1 = SwitchUltrasonicSensor(Port.F)",
        "sensor2 = SwitchIRSensor(Port.E)",
        "",
        "motor1 = SwitchMotor(Port.D, probability_curved_to_straight=0.8, probability_straight_to_curved=0.8)",
        "motor2 = SwitchMotor(Port.C, probability_curved_to_straight=0.4, probability_straight_to_curved=0.6)",
        "",
        "controller.register_sensor(sensor1, motor1)",
        "controller.register_sensor(sensor2, motor2)",
        "",
        "# start the switch controller",
        "controller.run()"
    ],
    'mindstorms_51515_1_1_1': [
        "hub = PrimeHub()",
        "hub.display.orientation(Side.BOTTOM)",
        "controller = SwitchController(hub)"
        "",
        "# configure your switch layout here",
        "sensor1 = SwitchSensor(Port.A)",
        "sensor1.set_init_timeout(60)",
        "sensor2 = SwitchSensor(Port.D)",
        "sensor2.set_init_timeout(20)",
        "sensor3 = SwitchSensor(Port.E)",
        "motor1 = SwitchMotor(Port.C, probability_curved_to_straight=0.8, probability_straight_to_curved=0.8)",
        "motor2 = SwitchMotor(Port.F, probability_curved_to_straight=0.8, probability_straight_to_curved=0.8)",
        "motor3 = SwitchMotor(Port.B, probability_curved_to_straight=0.8, probability_straight_to_curved=0.8)",
        "",
        "controller.register_sensor(sensor2, motor2)",
        "controller.register_sensor(sensor3, motor3)",
        "controller.register_sensor(sensor1, motor1)",
        "",
        "# start the switch controller",
        "controller.run()"
    ],
    '1sensor_3motors(1.1.1)': [
        "# creates a chained 3 motor layout with one sensor",
        "controller = SwitchController()",
        "",
        "sensor = SwitchSensor(Port.A, critical_distance=70)",
        "motor1 = SwitchMotor(Port.B, probability_curved_to_straight=0.25, probability_straight_to_curved=1)",
        "motor2 = SwitchMotor(Port.C, probability_curved_to_straight=0.33, probability_straight_to_curved=0.67)",
        "motor3 = SwitchMotor(Port.D, probability_curved_to_straight=0.7, probability_straight_to_curved=0.7)",
        "",
        "motor1.register_successor(motor2, SwitchPosition.CURVED)",
        "motor2.register_successor(motor3, SwitchPosition.CURVED)",
        "",
        "controller.register_sensor(sensor, motor1)",
        "",
        "# start the switch controller",
        "controller.run()"
    ],
    '1sensor_3motors(1.2)': [
        "# creates a tree like 3 motor layout with one sensor",
        "controller = SwitchController()",
        "",
        "sensor = SwitchSensor(Port.A, critical_distance=70)",
        "motor1 = SwitchMotor(Port.B, probability_curved_to_straight=0.25, probability_straight_to_curved=1)",
        "motor2 = SwitchMotor(Port.C, probability_curved_to_straight=0.33, probability_straight_to_curved=0.67)",
        "motor3 = SwitchMotor(Port.D, probability_curved_to_straight=0.7, probability_straight_to_curved=0.7)",
        "",
        "motor1.register_successor(motor2, SwitchPosition.CURVED)",
        "motor1.register_successor(motor3, SwitchPosition.CURVED)",
        "",
        "controller.register_sensor(sensor, motor1)",
        "",
        "# start the switch controller",
        "controller.run()"
    ],
    '2sensor_1motor': [
        "controller = SwitchController()",
        "",
        "pre_sensor = SwitchSensor(Port.A)",
        "post_sensor = SwitchSensor(Port.B, post_sensor_init_timeout=50, post_sensor_delay=100)",
        "post_sensors = {(SwitchPosition.STRAIGHT,): post_sensor}",
        "smart_sensor = SmartSensor(pre_sensor, post_sensors=post_sensors)",
        "",
        "motor = SwitchMotor(Port.C)"
        "",
        "controller.register_sensor(smart_sensor, motor)",
        "controller.run()"
    ]
}

for name, suffix in suffixes.items():
    with open(name + '.py', 'w+') as out:
        out.writelines(switch_file)
        for line in ['\n\n'] + suffix:
            out.write(line + '\n')