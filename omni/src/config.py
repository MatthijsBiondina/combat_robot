# hardware restrictions
MOTOR0_ANGLE = 150  # degrees
MOTOR1_ANGLE = -90  # degrees
MOTOR2_ANGLE = 30  # degrees

MOTOR0_ANGLE_INVERTED = MOTOR2_ANGLE
MOTOR2_ANGLE_INVERTED = MOTOR0_ANGLE

MAX_RPS = 750 / 60  # rounds per second
WHEEL_RADIUS = 0.024  # m
CHASSIS_RADIUS = 0.093  # m

# motor settings
ESC_GPIO = [19, 13, 18]
MAX_ESC_PULSEWIDTH_DELTA = 2000  # ms/s

# design choices
GLOBAL_TIMEOUT = 1  # s
MAX_LINEAR_VELOCITY = 1  # m/s
MAX_ANGULAR_VELOCITY = 6  # rad/s
INVERTED = True
