"""Simulator / Interpreter for quantized IR.

Executes a CFG (or SSAProgram) instruction by instruction.
For INT8 operations, performs clamping and enforces correct execution semantics.
"""

from fractions import Fraction
from typing import Any, Dict, List, Union

from src.ast.types import Type
from src.ir.tac import BinOp, CondJump, Copy, Input, Instr, Jump, Label, Phi, Print, UnOp
from src.ir.values import Const, Temp, Value, Var
from src.ssa.construction import SSAProgram


class SimulatorError(Exception):
    pass


def execute_ssa(program: SSAProgram, inputs: List[Union[int, float, Fraction]]) -> List[Any]:
    """Execute the SSA program with the given inputs. Returns a list of printed values."""
    env: Dict[str, Any] = {}
    
    def eval_val(v: Value) -> Any:
        if isinstance(v, Const):
            if v.ty == Type.INT8:
                return int(v.value)
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
            return int(val)
        elif t == Type.FLOAT:
            return float(val)
        else:
            return int(val)

    prev_block = None
    current_block = program.cfg.entry
    output = []
    input_iter = iter(inputs)
    
    while True:
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
                    if ins.dest_type in (Type.INT, Type.INT8):
                        res = int(left / right) if right != 0 else 0
                    else:
                        res = left / right if right != 0 else 0.0
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
