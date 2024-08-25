from dataclasses import dataclass, field

from cyclonedds.idl import IdlStruct


@dataclass
class StrPOD(IdlStruct, typename="StrPOD.Msg"):
    timestamp: float = field(metadata={"id": 0})
    msg: str = field(default="", metadata={"id": 1})
