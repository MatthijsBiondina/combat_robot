import time
from typing import AnyStr, List

from cyclonedds.qos import Qos

from src.cyclone.defaults import QOS
from src.cyclone.reader import Reader
from src.idl.xbox360_pod import Xbox360POD
from src.utils.default_types import CYCLONE_MESSAGE_TYPE
from src.utils.logger import get_logger

logger = get_logger()


class Xbox360Reader(Reader):
    TIMEOUT = 1.0

    def __init__(
        self,
        topic_name: AnyStr = "controller",
        data_type: CYCLONE_MESSAGE_TYPE = Xbox360POD,
        qos: Qos = QOS,
        rate_hz: int = 50,
        suppress_warnings: bool = False,
    ):
        super(Xbox360Reader, self).__init__(
            topic_name, data_type, qos, callback=None, rate_hz=rate_hz
        )
        self.suppress_warnings = suppress_warnings
        self.e_stop: bool = False
        self.rate_hz: int = rate_hz

    @property
    def state(self):
        t0 = time.time()
        xbox360pod_list: List[Xbox360POD] = []
        while time.time() < t0 + 1 / self.rate_hz:
            xbox360pod_list: List[Xbox360POD] = self()
            if len(xbox360pod_list) > 0:
                break

        if len(xbox360pod_list) == 0:  # If no data, return None
            if not self.suppress_warnings:
                logger.warn("Ik heb geen data ontvangen.")
            return None
        xbox360pod = xbox360pod_list[0]

        # If timeout exceeded, robot should go idle -> return None
        if xbox360pod.timestamp + self.TIMEOUT < time.time():
            self.e_stop = True
            if not self.suppress_warnings:
                logger.warn(
                    f"Het duurt te lang. Laatste bericht: "
                    f"{time.time() - xbox360pod.timestamp:.0f} seconden geleden."
                )
            return None
        self.e_stop = False
        return xbox360pod
