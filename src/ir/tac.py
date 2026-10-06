"""TAC instruction classes.

Every instruction performs at most one operation on at most two operands.
Instructions are real data structures (not strings): ``defs()``/``uses()``
expose operand structure to the CFG/SSA/analysis stages and ``loc`` keeps the
source location for traceability. ``format()`` is display only.

Instruction set
---------------
``dest = src``               Copy        (also constant moves ``x = 10``)
``dest = left op right``     BinOp       (+ - * / < > <= >= == !=)
``dest = -operand``          UnOp
``dest = input``             Input       (declaration without initializer)
``dest = phi(Bk: v, ...)``   Phi         (only after SSA construction)
``print v``                  Print
``L:``                       Label
``goto L``                   Jump
``if v goto L``              CondJump    (falls through when v is zero)
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from src.ast.types import Type
from src.diagnostics.location import SourceLocation
from src.ir.values import Value


def _dest(dest: Value, ty: Type, annotate: bool) -> str:
    return f"{dest} : {ty.display}" if annotate else str(dest)


@dataclass(kw_only=True)
class Instr:
    loc: Optional[SourceLocation] = None

    def defs(self) -> List[Value]:
        return []

    def uses(self) -> List[Value]:
        return []

    def replace_uses(self, fn: Callable[[Value], Value]) -> None:
        """Rewrite every operand read by this instruction through ``fn``."""

    def format(self, annotate: bool = False) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.format()


@dataclass
class Copy(Instr):
    dest: Value
    src: Value
    dest_type: Type

    def defs(self): return [self.dest]
    def uses(self): return [self.src]
    def replace_uses(self, fn): self.src = fn(self.src)
    def format(self, annotate=False):
        return f"{_dest(self.dest, self.dest_type, annotate)} = {self.src}"


@dataclass
class BinOp(Instr):
    dest: Value
    op: str
    left: Value
    right: Value
    dest_type: Type

    def defs(self): return [self.dest]
    def uses(self): return [self.left, self.right]
    def replace_uses(self, fn):
        self.left = fn(self.left)
        self.right = fn(self.right)
    def format(self, annotate=False):
        return f"{_dest(self.dest, self.dest_type, annotate)} = {self.left} {self.op} {self.right}"


@dataclass
class UnOp(Instr):
    dest: Value
    op: str  # 'neg'
    operand: Value
    dest_type: Type

    def defs(self): return [self.dest]
    def uses(self): return [self.operand]
    def replace_uses(self, fn): self.operand = fn(self.operand)
    def format(self, annotate=False):
        sym = "-" if self.op == "neg" else self.op
        return f"{_dest(self.dest, self.dest_type, annotate)} = {sym}{self.operand}"


@dataclass
class Input(Instr):
    """Definition of a variable declared without an initializer: its value is
    supplied from outside the program and therefore statically unknown."""

    dest: Value
    dest_type: Type

    def defs(self): return [self.dest]
    def format(self, annotate=False):
        return f"{_dest(self.dest, self.dest_type, annotate)} = input"


@dataclass
class Phi(Instr):
    """``dest = phi(...)``. ``var`` is the source variable being merged (kept
    for SSA renaming); ``incoming`` maps predecessor block id -> value."""

    dest: Value
    var: str
    incoming: Dict[int, Value] = field(default_factory=dict)
    dest_type: Type = Type.INT

    def defs(self): return [self.dest]
    def uses(self): return list(self.incoming.values())
    def replace_uses(self, fn):
        self.incoming = {b: fn(v) for b, v in self.incoming.items()}
    def format(self, annotate=False):
        args = ", ".join(f"B{b}: {v}" for b, v in sorted(self.incoming.items()))
        return f"{_dest(self.dest, self.dest_type, annotate)} = phi({args})"


@dataclass
class Print(Instr):
    value: Value

    def uses(self): return [self.value]
    def replace_uses(self, fn): self.value = fn(self.value)
    def format(self, annotate=False): return f"print {self.value}"


@dataclass
class Label(Instr):
    name: str

    def format(self, annotate=False): return f"{self.name}:"


@dataclass
class Jump(Instr):
    target: str

    def format(self, annotate=False): return f"goto {self.target}"


@dataclass
class CondJump(Instr):
    cond: Value
    target: str

    def uses(self): return [self.cond]
    def replace_uses(self, fn): self.cond = fn(self.cond)
    def format(self, annotate=False): return f"if {self.cond} goto {self.target}"


@dataclass
class TACProgram:
    """A linear TAC instruction list plus the symbol table of its variables
    (keyed by IR variable name)."""

    instrs: List[Instr]
    symbols: Dict[str, "object"] = field(default_factory=dict)

    def format(self, show_loc: bool = False) -> str:
        lines = []
        for ins in self.instrs:
            text = ins.format()
            if isinstance(ins, Label):
                lines.append(text)
                continue
            if show_loc and ins.loc is not None:
                text = f"{text:<28}; line {ins.loc.line}, col {ins.loc.column}"
            lines.append("    " + text)
        return "\n".join(lines)
