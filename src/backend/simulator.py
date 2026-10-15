"""Simulator / Interpreter for quantized and unquantized SSA IR.

Executes a CFG (or SSAProgram) instruction by instruction.
For INT8 operations, enforces 8-bit signed two's-complement arithmetic semantics
within [-128, 127].
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional, Union

from src.ast.types import Type
from src.ir.tac import BinOp, CondJump, Copy, Input, Instr, Jump, Label, Phi, Print, UnOp
from src.ir.values import Const, Temp, Value, Var
from src.ssa.construction import SSAProgram


class SimulatorError(Exception):
    pass


@dataclass
class SimulationResult:
    original_output: List[Any]
    quantized_output: List[Any]
    is_equivalent: bool
    error: Optional[str] = None


def execute_ssa(
    program: SSAProgram,
    inputs: Optional[List[Union[int, float, Fraction]]] = None,
    max_steps: int = 100000,
) -> List[Any]:
    """Execute the SSA program with the given inputs. Returns a list of printed values."""
    if inputs is None:
        inputs = []
    env: Dict[str, Any] = {}

    def eval_val(v: Value) -> Any:
        if isinstance(v, Const):
            if v.ty == Type.INT8:
                int_val = int(v.value)
                return ((int_val + 128) % 256) - 128
            elif v.ty == Type.FLOAT:
                return float(v.value)
            else:
                return int(v.value)
        elif isinstance(v, (Var, Temp)):
            name = str(v)
            if name not in env:
                raise SimulatorError(f"Use of uninitialized variable {name}")
            return env[name]
        raise ValueError(f"Unknown value type {v} ({type(v)})")

    def cast_val(val: Any, t: Type) -> Any:
        if t == Type.INT8:
            int_val = int(val)
            return ((int_val + 128) % 256) - 128
        elif t == Type.FLOAT:
            return float(val)
        else:
            return int(val)

    prev_block = None
    current_block = program.cfg.entry
    output = []
    input_iter = iter(inputs)
    step_count = 0

    while True:
        step_count += 1
        if step_count > max_steps:
            raise SimulatorError(f"Execution exceeded maximum step limit ({max_steps})")

        blk = program.cfg.blocks[current_block]
        next_block = None

        for ins in blk.instrs:
            if isinstance(ins, Label):
                continue

            elif isinstance(ins, Copy):
                val = eval_val(ins.src)
                env[str(ins.dest)] = cast_val(val, ins.dest_type)

            elif isinstance(ins, BinOp):
                left = eval_val(ins.left)
                right = eval_val(ins.right)

                if ins.op == '+': res = left + right
                elif ins.op == '-': res = left - right
                elif ins.op == '*': res = left * right
                elif ins.op == '/':
                    if right == 0:
                        raise SimulatorError("Division by zero in simulator")
                    if ins.dest_type in (Type.INT, Type.INT8):
                        res = int(left / right)
                    else:
                        res = left / right
                elif ins.op == '<': res = int(left < right)
                elif ins.op == '>': res = int(left > right)
                elif ins.op == '<=': res = int(left <= right)
                elif ins.op == '>=': res = int(left >= right)
                elif ins.op == '==': res = int(left == right)
                elif ins.op == '!=': res = int(left != right)
                else:
                    raise SimulatorError(f"Unknown operator {ins.op}")

                env[str(ins.dest)] = cast_val(res, ins.dest_type)

            elif isinstance(ins, UnOp):
                operand = eval_val(ins.operand)
                if ins.op == 'neg':
                    res = -operand
                else:
                    res = -operand
                env[str(ins.dest)] = cast_val(res, ins.dest_type)

            elif isinstance(ins, Input):
                try:
                    val = next(input_iter)
                except StopIteration:
                    raise SimulatorError("Not enough inputs provided for Input instruction")
                env[str(ins.dest)] = cast_val(val, ins.dest_type)

            elif isinstance(ins, Phi):
                if prev_block not in ins.incoming:
                    raise SimulatorError(f"Phi node missing incoming value for block B{prev_block}")
                inc_val = ins.incoming[prev_block]
                val = eval_val(inc_val)
                env[str(ins.dest)] = cast_val(val, ins.dest_type)

            elif isinstance(ins, Print):
                output.append(eval_val(ins.value))

        if not program.cfg.succs(current_block):
            break

        last_ins = blk.instrs[-1] if blk.instrs else None
        succs = program.cfg.succs(current_block)

        if isinstance(last_ins, Jump):
            for s in succs:
                if program.cfg.edge_kind(current_block, s) == 'jump':
                    next_block = s
                    break
            if next_block is None:
                next_block = succs[0]

        elif isinstance(last_ins, CondJump):
            cond = eval_val(last_ins.cond)
            kind_wanted = 'true' if cond != 0 else 'false'
            for s in succs:
                if program.cfg.edge_kind(current_block, s) == kind_wanted:
                    next_block = s
                    break
        else:
            for s in succs:
                if program.cfg.edge_kind(current_block, s) == 'fallthrough':
                    next_block = s
                    break
            if next_block is None and len(succs) == 1:
                next_block = succs[0]

        if next_block is None:
            break

        prev_block = current_block
        current_block = next_block

    return output


def simulate_programs(
    original_ssa: SSAProgram,
    quantized_ssa: SSAProgram,
    inputs: Optional[List[Union[int, float, Fraction]]] = None,
    max_steps: int = 100000,
) -> SimulationResult:
    """Simulate both original and quantized SSA programs and verify numerical equivalence."""
    if inputs is None:
        inputs = []

    orig_err: Optional[str] = None
    quant_err: Optional[str] = None
    orig_out: List[Any] = []
    quant_out: List[Any] = []

    try:
        orig_out = execute_ssa(original_ssa, list(inputs), max_steps=max_steps)
    except Exception as exc:
        orig_err = str(exc)

    try:
        quant_out = execute_ssa(quantized_ssa, list(inputs), max_steps=max_steps)
    except Exception as exc:
        quant_err = str(exc)

    error: Optional[str] = None
    if orig_err or quant_err:
        if orig_err and quant_err:
            error = f"Original error: {orig_err} | Quantized error: {quant_err}"
        elif orig_err:
            error = f"Original error: {orig_err}"
        else:
            error = f"Quantized error: {quant_err}"
        is_equivalent = False
    else:
        is_equivalent = (orig_out == quant_out)

    return SimulationResult(
        original_output=orig_out,
        quantized_output=quant_out,
        is_equivalent=is_equivalent,
        error=error,
    )
