import os
import pygame
import time

# Initialize Pygame
pygame.init()

# Initialize the joystick component
pygame.joystick.init()

# Check for joystick count
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No joystick detected")
    exit()

# Use the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

try:
    while True:
        for event in pygame.event.get():  # User did something
            os.system("clear")
            if event.type == pygame.JOYAXISMOTION:  # Joystick movement
                # Capture input from all joysticks
                left_stick_x = joystick.get_axis(0)
                left_stick_y = joystick.get_axis(1)
                left_trigger = joystick.get_axis(2)
                right_stick_x = joystick.get_axis(4)
                right_stick_y = joystick.get_axis(3)
                right_trigger = joystick.get_axis(5)

                print(
                    f"Left Stick X-axis: {left_stick_x:.2f} Y-axis: {left_stick_y:.2f}"
                )
                print(
                    f"Right Stick X-axis: {right_stick_x:.2f} Y-axis: {right_stick_y:.2f}"
                )
                print(f"Left Trigger: {left_trigger:.2f}")
                print(f"Right Trigger: {right_trigger:.2f}")

            elif event.type == pygame.JOYBUTTONDOWN:  # Button pressed
                print(f"Button {event.button} pressed")
            elif event.type == pygame.JOYBUTTONUP:  # Button released
                print(f"Button {event.button} released")

        # Delay briefly to limit output (reduces CPU usage)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    # Properly shut down Pygame
    pygame.joystick.quit()
    pygame.quit()
