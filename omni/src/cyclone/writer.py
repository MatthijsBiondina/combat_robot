import logging
import time
from typing import AnyStr, Union

from cyclonedds.domain import DomainParticipant
from cyclonedds.core import Qos
from cyclonedds.idl import IdlStruct, IdlUnion
from cyclonedds.pub import DataWriter
from cyclonedds.topic import Topic

from src.cyclone.cycloneddsnode import CycloneDDSNode
from src.cyclone.defaults import QOS
from src.idl.base_types.str_pod import StrPOD
from src.utils.default_types import CYCLONE_MESSAGE_TYPE
from src.utils.logger import get_logger

logger = get_logger()


class Writer(CycloneDDSNode):
    def __init__(
            self,
            topic_name: AnyStr,
            data_type: CYCLONE_MESSAGE_TYPE,
            qos: Qos = QOS,
            rate_hz: int = 50,
    ):
        super().__init__(rate_hz)
        self.participant = DomainParticipant()
        self.topic = Topic(self.participant, topic_name, data_type, qos=qos)
        self.writer = DataWriter(self.participant, self.topic, qos=qos)

    def publish(self, msg: Union[IdlStruct, IdlUnion]):
        try:
            self.writer.write(msg)
        except Exception as e:
            logger.exception(f"Exception occurred while writing {type(msg)}.")


if __name__ == "__main__":
    writer = Writer("foo", StrPOD)
    for ii in range(int(1e6)):
        msg = f"{ii}"
        logger.log(logging.INFO, msg)
        pod = StrPOD(timestamp=time.time(), msg=f"foo {ii}")
        writer.publish(pod)

        time.sleep(1)
