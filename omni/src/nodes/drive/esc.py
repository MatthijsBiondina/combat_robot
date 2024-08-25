import argparse
import time

import numpy as np
import pigpio

from src import config
from src.config import GLOBAL_TIMEOUT, MAX_ESC_PULSEWIDTH_DELTA
from src.cyclone.cycloneddsnode import CycloneDDSNode
from src.cyclone.reader import Reader
from src.idl.base_types.float_pod import FloatPOD
from src.utils.logger import get_logger
from src.utils.tools import pyout

logger = get_logger()


class ElectornicSpeedController(CycloneDDSNode):
    """
    Manages the ESC for a specific motor by controlling the pulse width based on commands received
    via DDS. It ensures smooth transitions in pulse width to prevent triggering the ESC's failsafe.
    """

    PULSEWIDTH_STATIONARY = 1500  # Neutral pulse width when the motor is stationary.

    def __init__(self, motor_nr: int):
        """
        Initializes the ESC controller for the specified motor.

        Args:
            motor_nr (int): The motor number to control.
        """
        super().__init__()
        self.__motor_nr = motor_nr
        self.__gpio_nr = config.ESC_GPIO[motor_nr]
        self.__arm_esc()

        # Create a DDS reader for receiving pulse width commands.
        self.__input = Reader(
            topic_name=f"ESC{self.__motor_nr}_pulsewidth", data_type=FloatPOD
        )
        self.__current_pulsewidth = self.PULSEWIDTH_STATIONARY
        self.__target_pulsewidth = self.PULSEWIDTH_STATIONARY
        self.__timestamp_last_input_recieved = time.time()

        self.__run()

    def __run(self):
        """
        The main control loop that continuously checks for new pulse width commands and
        updates the ESC.
        """
        timestamp_last_control_loop = time.time()
        while True:
            try:
                # Get the latest pulse width command from the DDS topic.
                pod = self.__input()[-1]
                self.__timestamp_last_input_recieved = pod.timestamp
                self.__target_pulsewidth = self.__clip_pulsewidth(pod.float_)
            except IndexError:
                pass  # Handle cases where no command is received.

            # Implement an emergency stop if no command is received within the timeout period.
            if self.__timestamp_last_input_recieved + GLOBAL_TIMEOUT < time.time():
                self.__target_pulsewidth = self.PULSEWIDTH_STATIONARY

            # Gradually update the pulse width to avoid triggering the ESC failsafe.
            self.__update_pulsewidth(time.time() - timestamp_last_control_loop)
            self.__set_pulsewidth(self.__current_pulsewidth)
            timestamp_last_control_loop = time.time()
            self.sleep()

    def __arm_esc(self):
        """
        Arms the ESC by sending a neutral pulse width signal and verifying the connection to pigpio.
        """
        self.pi = pigpio.pi()
        if not self.pi.connected:
            logger.exception(
                f"Motor {self.__motor_nr} (GPIO {self.__gpio_nr}): pigpio not connected"
            )
            raise RuntimeError("pigpio not connected")
        self.__set_pulsewidth(1500)
        time.sleep(2)
        logger.info(f"Motor {self.__motor_nr} ({self.__gpio_nr}) armed.")

    def __clip_pulsewidth(self, pw: float):
        """
        Clips the pulse width to ensure it remains within the valid range (1001-1999 microseconds).

        Args:
            pw (float): The requested pulse width.

        Returns:
            float: The clipped pulse width within the valid range.
        """
        if not (1000 <= pw <= 2000):
            logger.warn(
                f"Motor {self.__motor_nr} ({self.__gpio_nr}): Requested pulsewidth "
                f"({pw}) not in range (1000, 2000)"
            )
            pw = np.clip(pw, 1001, 1999)
        return pw

    def __set_pulsewidth(self, pw: float):
        """
        Sets the pulse width for the ESC after clipping it to the valid range.

        Args:
            pw (float): The pulse width to set.
        """
        pw = self.__clip_pulsewidth(pw)
        self.pi.set_servo_pulsewidth(self.__gpio_nr, pw)

    def __update_pulsewidth(self, delta_time: float):
        """
        Gradually adjusts the current pulse width towards the target to avoid
        triggering the ESC failsafe.

        Args:
            delta_time (float): The time elapsed since the last control loop iteration.
        """
        if self.__current_pulsewidth < self.__target_pulsewidth:
            self.__current_pulsewidth = min(
                self.__target_pulsewidth,
                self.__current_pulsewidth + MAX_ESC_PULSEWIDTH_DELTA * delta_time,
            )
        elif self.__current_pulsewidth > self.__target_pulsewidth:
            self.__current_pulsewidth = max(
                self.__target_pulsewidth,
                self.__current_pulsewidth - MAX_ESC_PULSEWIDTH_DELTA * delta_time,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Electronic Speed Controller.")
    parser.add_argument(
        "motor_nr", type=int, nargs="?", default=0, help="The motor number."
    )
    args = parser.parse_args()
    esc = ElectornicSpeedController(args.motor_nr)
