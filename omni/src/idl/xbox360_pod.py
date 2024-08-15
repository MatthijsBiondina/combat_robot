from dataclasses import dataclass, field
from typing import Tuple

from cyclonedds.idl import IdlStruct


@dataclass
class Xbox360POD(IdlStruct, typename="Xbox360POD.Msg"):
    timestamp: float = field(metadata={"id": 0})

    # Axes
    axis_left_stick_x: float = field(metadata={"id": 1})
    axis_left_stick_y: float = field(metadata={"id": 2})
    axis_right_stick_x: float = field(metadata={"id": 3})
    axis_right_stick_y: float = field(metadata={"id": 4})
    axis_left_trigger: float = field(metadata={"id": 5})
    axis_right_trigger: float = field(metadata={"id": 6})

    # Buttons
    button_A: int = field(metadata={"id": 7})
    button_B: int = field(metadata={"id": 8})
    button_X: int = field(metadata={"id": 9})
    button_Y: int = field(metadata={"id": 10})
    button_left_bumper: int = field(metadata={"id": 11})
    button_right_bumper: int = field(metadata={"id": 12})
    button_back: int = field(metadata={"id": 13})
    button_start: int = field(metadata={"id": 14})
    button_left_stick: int = field(metadata={"id": 15})
    button_right_stick: int = field(metadata={"id": 16})

    # Hats
    hat_D_pad_x: int = field(metadata={"id": 17})
    hat_D_pad_y: int = field(metadata={"id": 18})
