import time
from typing import AnyStr, Tuple
from cyclonedds.qos import Qos
from pygame.joystick import JoystickType

from src.cyclone.defaults import QOS
from src.cyclone.writer import Writer
from src.idl.xbox360_pod import Xbox360POD
from src.utils.default_types import CYCLONE_MESSAGE_TYPE
import pygame

from src.utils.logger import get_logger
from src.utils.tools import pyout

logger = get_logger()
pygame.init()


class Xbox360Writer(Writer):
    RATE_HZ = 50  # We chose the same rate as the ESC protocol

    def __init__(
            self,
            topic_name: AnyStr = "controller",
            data_type: CYCLONE_MESSAGE_TYPE = Xbox360POD,
            qos: Qos = QOS,
            controller_number: int = 0,
            rate_hz: int = RATE_HZ,
    ):
        super().__init__(topic_name, data_type, qos, rate_hz)
        self.controller_number = controller_number
        self.joystick: JoystickType = self.__init_controller(controller_number)
        self.__run()

    def __init_controller(
            self, controller_number: int, suppress_log: bool = False
    ) -> JoystickType:
        pygame.joystick.init()

        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()
        if joystick_count <= controller_number:
            if not suppress_log:
                logger.exception(
                    f"Ik kan controller {controller_number} niet vinden. "
                    f"Er zijn {joystick_count} controllers aangesloten."
                )
            raise RuntimeError(
                f"Controller {controller_number} is invalid. "
                f"Only {joystick_count} joysticks are detected."
            )
        else:
            joystick = pygame.joystick.Joystick(controller_number)
            joystick.init()
            if not suppress_log:
                logger.info(
                    f"Controller {controller_number} ({joystick.get_name()}) "
                    f"connected."
                )
        return joystick

    def __run(self):
        while True:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.JOYDEVICEREMOVED:
                        pygame.joystick.quit()

                D_pad: Tuple[int, int] = self.joystick.get_hat(0)
                joystick_state: Xbox360POD = Xbox360POD(
                    timestamp=time.time(),
                    axis_left_stick_x=self.joystick.get_axis(0),
                    axis_left_stick_y=self.joystick.get_axis(1),
                    axis_right_stick_x=self.joystick.get_axis(3),
                    axis_right_stick_y=self.joystick.get_axis(4),
                    axis_left_trigger=self.joystick.get_axis(2),
                    axis_right_trigger=self.joystick.get_axis(5),
                    button_A=self.joystick.get_button(0),
                    button_B=self.joystick.get_button(1),
                    button_X=self.joystick.get_button(2),
                    button_Y=self.joystick.get_button(3),
                    button_left_bumper=self.joystick.get_button(4),
                    button_right_bumper=self.joystick.get_button(5),
                    button_back=self.joystick.get_button(6),
                    button_start=self.joystick.get_button(7),
                    button_left_stick=self.joystick.get_button(9),
                    button_right_stick=self.joystick.get_button(8),
                    hat_D_pad_x=D_pad[0],
                    hat_D_pad_y=D_pad[1],
                )
                self.publish(joystick_state)
            except pygame.error as e:
                error_message = e.args[0]
                if (
                        error_message == "Joystick not initialized"
                        or error_message == "joystick system not initialized"
                ):
                    logger.warn("Controller niet verbonden!")
                    try:
                        self.joystick = self.__init_controller(
                            self.controller_number, suppress_log=True
                        )
                    except RuntimeError:
                        pass
            except Exception as e:
                logger.exception(f"Er is een onverwachte fout opgetreden: {e}")

            self.sleep()


if __name__ == "__main__":
    writer = Xbox360Writer()
