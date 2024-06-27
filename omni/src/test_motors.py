import pigpio
import time

ESC_PIN = 19  # Adjust according to your wiring

pi = pigpio.pi()
if not pi.connected:
    exit(0)

# Initialize the ESC
pi.set_servo_pulsewidth(ESC_PIN, 0)


def set_speed(pulse_width):
    """
    Set the speed of the motor by changing the pulse width.
    pulse_width: int, pulse width in microseconds (1000 to 2000)
    """
    print(pulse_width, end="\r")
    pi.set_servo_pulsewidth(ESC_PIN, pulse_width)


DV = 500

try:
    # Arm the ESC
    print("Arming ESC...")
    set_speed(1500)  # Neutral position to arm
    time.sleep(5)
    for speed in range(1500, 1500 + DV, 10):
        set_speed(speed)
        time.sleep(0.1)
        print(speed, end="\r")
    for speed in range(1500 + DV, 1500 - DV, -10):
        set_speed(speed)
        time.sleep(0.3)
        print(speed, end="\r")
    for speed in range(1500 - DV, 1500, 10):
        set_speed(speed)
        time.sleep(0.1)
        print(speed, end="\r")
    time.sleep(1)
    set_speed(1500)
    time.sleep(1)
    set_speed(0)
    time.sleep(1)
except KeyboardInterrupt:
    print("Program interrupted")

finally:
    # Cleanup
    pi.set_servo_pulsewidth(ESC_PIN, 0)
    pi.stop()
