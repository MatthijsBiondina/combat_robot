from typing import Union, Type

from cyclonedds.idl import IdlStruct, IdlUnion

CYCLONE_MESSAGE_TYPE: Type = Union[Type[IdlStruct], Type[IdlUnion]]
