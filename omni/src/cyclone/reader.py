import logging
import time
from typing import Optional, AnyStr, Type, Union, Callable

from cyclonedds.domain import DomainParticipant
from cyclonedds.core import Qos
from cyclonedds.idl import IdlStruct, IdlUnion
from cyclonedds.sub import DataReader
from cyclonedds.qos import Policy
from cyclonedds.topic import Topic

from src.cyclone.cycloneddsnode import CycloneDDSNode
from src.cyclone.defaults import QOS
from src.idl.str_pod import StrPOD

logger = logging.getLogger(__name__)


class Reader(CycloneDDSNode):
    def __init__(
        self,
        topic_name: AnyStr,
        data_type: Union[Type[IdlStruct], Type[IdlUnion]],
        qos: Optional[Qos] = QOS,
        callback: Optional[Callable[[Union[IdlStruct, IdlUnion]], None]] = None,
        rate_hz: int = 50,
    ):
        super().__init__(rate_hz)
        self.participant = DomainParticipant()
        self.topic = Topic(self.participant, topic_name, data_type, qos=qos)
        self.reader = DataReader(self.participant, self.topic, qos=qos)
        self.callback = callback

    def __call__(self, *args, **kwargs):
        try:
            data_seq = self.reader.take()
            return data_seq
        except Exception as e:
            logger.exception("Exception occurred while reading.")
        return None


if __name__ == "__main__":
    reader = Reader(
        "foo",
        StrPOD,
    )
    for _ in range(10):
        a = reader()
        print(a)
        time.sleep(0.5)
