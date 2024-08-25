from dataclasses import dataclass, field

from cyclonedds.idl import IdlStruct


@dataclass
class FloatPOD(IdlStruct, typename="FloatPOD.Msg"):
    timestamp: float = field(metadata={"id": 0})
    float_: float = field(default=0.0, metadata={"id": 1})
