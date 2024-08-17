from dataclasses import field, dataclass

from cyclonedds.idl import IdlStruct


@dataclass
class DriveControlPOD(IdlStruct, typename="DriveControlPOD.Msg"):
    timestamp: float = field(metadata={"id": 0})

    esc0: float = field(metadata={"id": 1})
    esc1: float = field(metadata={"id": 2})
    esc2: float = field(metadata={"id": 3})
