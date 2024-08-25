from src.cyclone.cycloneddsnode import CycloneDDSNode
from src.cyclone.reader import Reader
from src.cyclone.writer import Writer
from src.idl.base_types.float_pod import FloatPOD
from src.idl.drive_control_pod import DriveControlPOD
from src.nodes.controller.xbox360.xbox360_reader import Xbox360Reader
from src.utils.logger import get_logger
from src.utils.tools import pyout

logger = get_logger()


class ESCController(CycloneDDSNode):
    """
    For now, we simply assume a linear relationship between rpm and esc-pulsewidth
    """

    def __init__(self):
        super().__init__()

        self.drive_controller = Reader("drive_controller", DriveControlPOD)

        self.esc0_writer = Writer("ESC0_pulsewidth", FloatPOD)
        self.esc1_writer = Writer("ESC1_pulsewidth", FloatPOD)
        self.esc2_writer = Writer("ESC2_pulsewidth", FloatPOD)

        self.__run()

    def __run(self):
        while True:
            try:
                controller_state: DriveControlPOD = self.drive_controller()[-1]

                esc0_pulsewidth = self.__convert_rpm2pulsewidth(controller_state.esc0)
                esc1_pulsewidth = self.__convert_rpm2pulsewidth(controller_state.esc1)
                esc2_pulsewidth = self.__convert_rpm2pulsewidth(controller_state.esc2)

                self.esc0_writer.publish(
                    FloatPOD(controller_state.timestamp, float_=esc0_pulsewidth)
                )
                self.esc1_writer.publish(
                    FloatPOD(controller_state.timestamp, float_=esc1_pulsewidth)
                )
                self.esc2_writer.publish(
                    FloatPOD(controller_state.timestamp, float_=esc2_pulsewidth)
                )
            except IndexError:
                pass
            except Exception as e:
                logger.exception(f"Er is een onverwachte fout opgetreden: {e}")

            self.sleep()

    def __convert_rpm2pulsewidth(self, rpm: float):
        return 1500 + 500 * rpm


if __name__ == "__main__":
    ESCController()
