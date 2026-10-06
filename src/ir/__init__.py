"""Three Address Code: values, instructions, program container, AST lowering."""

from src.ir.lowering import generate_tac
from src.ir.tac import (
    BinOp, Copy, CondJump, Input, Instr, Jump, Label, Phi, Print, TACProgram, UnOp,
)
from src.ir.values import Const, Temp, Value, Var, format_number

__all__ = [
    "BinOp", "Copy", "CondJump", "Input", "Instr", "Jump", "Label", "Phi", "Print",
    "TACProgram", "UnOp", "Const", "Temp", "Value", "Var", "format_number", "generate_tac",
]
