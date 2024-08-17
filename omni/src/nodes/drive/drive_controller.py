import time
from typing import Optional, Tuple, Union, List, AnyStr

import numpy as np
from cyclonedds.qos import Qos

from src.config import (
    MAX_LINEAR_VELOCITY,
    MAX_ANGULAR_VELOCITY,
    MOTOR1_ANGLE,
    MOTOR0_ANGLE,
    MOTOR2_ANGLE,
    WHEEL_RADIUS,
    CHASSIS_RADIUS,
    MAX_RPS,
)
from src.cyclone.defaults import QOS
from src.cyclone.writer import Writer
from src.idl.drive_control_pod import DriveControlPOD
from src.idl.xbox360_pod import Xbox360POD
from src.nodes.controller.xbox360.xbox360_reader import Xbox360Reader
from src.utils.default_types import CYCLONE_MESSAGE_TYPE
from src.utils.logger import get_logger

logger = get_logger()


class DriveController(Writer):
    """
    The DriveController class is responsible for controlling the motor speeds of an omni-wheel
    kiwi-drive robot based on input from an Xbox 360 controller. It reads the desired velocities
    (linear and angular) from the controller, computes the corresponding motor speeds, normalizes
    them to ensure they stay within acceptable limits, and then publishes these speeds to the motors.

    """

    def __init__(
            self,
            topic_name: AnyStr = "drive_controller",
            data_type: CYCLONE_MESSAGE_TYPE = DriveControlPOD,
            qos: Qos = QOS,
            rate_hz: int = 50,
    ):
        """
        Initializes the DriveController object.

        Parameters:
        -----------
        topic_name : AnyStr
            The DDS topic name for the motor control messages.
        data_type : CYCLONE_MESSAGE_TYPE
            The data type for the DDS messages (DriveControlPOD).
        qos : Qos
            The Quality of Service (QoS) settings for the DDS communication.
        rate_hz : int
            The frequency at which to publish motor control messages.
        """
        super().__init__(topic_name, data_type, qos, rate_hz)
        self.controller = Xbox360Reader()
        self.controller_state: Optional[Xbox360POD] = None

        self.R_motor0_body = self.__init_rotation_matrix(MOTOR0_ANGLE)
        self.R_motor1_body = self.__init_rotation_matrix(MOTOR1_ANGLE)
        self.R_motor2_body = self.__init_rotation_matrix(MOTOR2_ANGLE)

        self.__run()

    def __run(self):
        """
        Main loop for the DriveController. Continuously reads the state of the Xbox 360 controller,
        computes the desired motor speeds based on the controller input, and publishes these speeds
        to the motors. If an emergency stop (e-stop) is detected, it sets all motor speeds to zero.
        """
        while True:
            try:
                new_controller_state = self.controller.state
                self.controller_state = (
                    new_controller_state if new_controller_state is not None else None
                )

                if self.controller.e_stop or self.controller_state is None:
                    esc0, esc1, esc2 = 0.0, 0.0, 0.0
                else:
                    dx, dy, d_omega = self.__get_desired_velocities_from_controller()
                    (
                        rps0_unnormalized,
                        rps1_unnormalized,
                        rps2_unnormalized,
                    ) = self.__compute_motor_speeds_rps(dx, dy, d_omega)

                    (
                        rps0_normalized,
                        rps1_normalized,
                        rps2_normalized,
                    ) = self.__normalize_motor_speeds(
                        rps0_unnormalized, rps1_unnormalized, rps2_unnormalized
                    )

                    esc0 = rps0_normalized / MAX_RPS
                    esc1 = rps1_normalized / MAX_RPS
                    esc2 = rps2_normalized / MAX_RPS

                motor_control_message = DriveControlPOD(
                    timestamp=time.time(),
                    esc0=esc0,
                    esc1=esc1,
                    esc2=esc2,
                )
                self.publish(motor_control_message)

            except Exception as e:
                logger.exception(f"Er is een onverwachte fout opgetreden: {e}")

    def __get_desired_velocities_from_controller(self) -> Tuple[float, float, float]:
        """
        Extracts the desired linear and angular velocities from the Xbox 360 controller input.

        Returns:
        --------
        Tuple[float, float, float]
            The desired velocities in the x-direction, y-direction, and angular velocity (rotation).
        """
        # pushing L stick forward (-1) -> move forward (+ LINEAR VELOCITY)
        d_x = -self.controller_state.axis_left_stick_y * MAX_LINEAR_VELOCITY
        d_y = -self.controller_state.axis_left_stick_x * MAX_LINEAR_VELOCITY

        # pushing R stick right(1) ->  rotate clockwise (-ANGULAR VELOCITY)
        d_omega = -self.controller_state.axis_right_stick_x * MAX_ANGULAR_VELOCITY

        return d_x, d_y, d_omega

    def __compute_motor_speeds_rps(
            self, dx: float, dy: float, d_omega: float
    ) -> Tuple[float, float, float]:
        """
        Computes the unnormalized motor speeds in rounds per second (RPS) for each motor
        based on the desired linear and angular velocities.

        Parameters:
        -----------
        dx : float
            The desired linear velocity in the x-direction (m/s).
        dy : float
            The desired linear velocity in the y-direction (m/s).
        d_omega : float
            The desired angular velocity (rad/s).

        Returns:
        --------
        Tuple[float, float, float]
            The unnormalized motor speeds (RPS) for motor 0, motor 1, and motor 2.
        """
        rps0_linear = self.__compute_linear_motor_rps(dx, dy, self.R_motor0_body)
        rps1_linear = self.__compute_linear_motor_rps(dx, dy, self.R_motor1_body)
        rps2_linear = self.__compute_linear_motor_rps(dx, dy, self.R_motor2_body)
        rps_angular = self.__compute_angular_motor_velocity(d_omega)

        rps0_unnormalized = rps0_linear + rps_angular
        rps1_unnormalized = rps1_linear + rps_angular
        rps2_unnormalized = rps2_linear + rps_angular

        return rps0_unnormalized, rps1_unnormalized, rps2_unnormalized

    def __compute_linear_motor_rps(self, dx: float, dy: float, R: np.ndarray) -> float:
        """
        Computes the linear component of the motor speed in rounds per second (RPS).

        Parameters:
        -----------
        dx : float
            The desired linear velocity in the x-direction (m/s).
        dy : float
            The desired linear velocity in the y-direction (m/s).
        R : np.ndarray
            The rotation matrix that transforms vectors from the body frame to the motor frame.

        Returns:
        --------
        float
            The linear speed of the motor in rounds per second (RPS).
        """
        V_body = np.array([dx, dy])
        v_motor = (R.T @ V_body)[0]  # m/s
        omega_motor = v_motor / WHEEL_RADIUS  # rad/s
        rps_motor = omega_motor / (2 * np.pi)  # rounds per second
        return rps_motor

    def __compute_angular_motor_velocity(self, d_omega: float) -> float:
        """
        Computes the angular component of the motor speed in rounds per second (RPS).

        Parameters:
        -----------
        d_omega : float
            The desired angular velocity (rad/s).

        Returns:
        --------
        float
            The angular speed of the motor in rounds per second (RPS).
        """
        v_motor = d_omega * CHASSIS_RADIUS  # m/s
        omega_motor = v_motor / WHEEL_RADIUS  # rad/s
        return omega_motor / (2 * np.pi)  # rounds per second

    def __init_rotation_matrix(self, angle_degrees: Union[float, int]) -> np.ndarray:
        """
        Initializes the 2x2 rotation matrix for converting vectors from the body frame
        to a motor's frame, based on the motor's angle with respect to the x-axis of the body frame.

        Parameters:
        -----------
        angle_degrees : Union[float, int]
            The angle between the motor's axis and the x-axis of the body frame, in degrees.

        Returns:
        --------
        np.ndarray
            The 2x2 rotation matrix corresponding to the given angle.
        """
        theta = np.deg2rad(angle_degrees)
        R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        return R

    def __normalize_motor_speeds(self, *args: float) -> Tuple[float, ...]:
        """
        Normalizes the motor speeds so that the maximum speed does not exceed the defined limit (MAX_RPS).
        If any motor speed exceeds MAX_RPS, all motor speeds are scaled down proportionally.

        Parameters:
        -----------
        *args : float
            Variable number of motor speeds (in rounds per second).

        Returns:
        --------
        Tuple[float, ...]
            The normalized motor speeds.
        """
        unnormalized_speeds = np.array(args)

        max_desired_speed = np.max(np.absolute(unnormalized_speeds))

        if max_desired_speed > MAX_RPS:
            reduction_factor = MAX_RPS / max_desired_speed
            normalized_speeds = unnormalized_speeds * reduction_factor
        else:
            normalized_speeds = unnormalized_speeds

        return tuple(normalized_speeds.tolist())


if __name__ == "__main__":
    node = DriveController()
