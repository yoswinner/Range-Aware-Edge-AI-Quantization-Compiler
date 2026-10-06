"""Scalar types of the language and of the IR."""

from enum import Enum


class Type(Enum):
    """Source types are INT and FLOAT (FP32). BOOL is the type of relational
    results. INT8 only ever appears in IR produced by the quantization pass;
    ERROR is the poison type used to avoid cascading semantic diagnostics."""

    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    INT8 = "int8"
    ERROR = "<error>"

    @property
    def display(self) -> str:
        return {"float": "fp32"}.get(self.value, self.value)

    def is_numeric(self) -> bool:
        return self in (Type.INT, Type.FLOAT)
