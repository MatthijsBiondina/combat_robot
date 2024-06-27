import logging
from typing import Optional, AnyStr, Type, Union

from cyclonedds.domain import DomainParticipant
from cyclonedds.core import Qos
from cyclonedds.idl import IdlStruct, IdlUnion
from cyclonedds.pub import DataWriter
from cyclonedds.qos import Policy
from cyclonedds.topic import Topic
from cyclonedds.util import duration

logger = logging.getLogger(__name__)


class Writer:
    def __init__(
        self,
        topic_name: AnyStr,
        data_type: Union[Type[IdlStruct], Type[IdlUnion]],
        qos: Optional[Qos] = None,
    ):
        self.participant = DomainParticipant()

        qos = (
            qos
            if qos is not None
            else Qos(
                Policy.Reliability.BestEffort,
                Policy.Reliability.BestEffort,
                Policy.Deadline(duration(milliseconds=10)),
                Policy.History.KeepLast(1),
                Policy.ResourceLimits(
                    max_samples=1, max_instances=1, max_samples_per_instance=1
                ),
            )
        )

        self.topic = Topic(self.participant, topic_name, data_type, qos=qos)
        self.writer = DataWriter(self.participant, self.topic, qos=qos)

    def publish(self, msg: Union[IdlStruct, IdlUnion]):
        try:
            self.writer.write(msg)
        except Exception as e:
            logger.exception(f"Exception occurred while publishing {type(msg)}")
