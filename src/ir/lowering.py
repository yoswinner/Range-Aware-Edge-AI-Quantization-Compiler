"""Lowering of a semantically validated AST into Three Address Code.

Conventions
-----------
* Every compound sub-expression gets a fresh temporary ``tN`` (assigned once).
  Leaves (variables, constants) are used directly as immediate operands.
* When an expression is the right-hand side of a declaration/assignment its
  final operation writes straight into the target variable
  (``y = x + 5``) instead of going through a temp plus a copy, so the SSA form
  of the review's example is exactly ``y.1 = x.3 + 5``.
* ``-literal`` is folded into a negative constant (so ``-128`` is a constant).
* Control flow uses labels, ``if v goto L`` and ``goto L``::

      if (c) A else B          while (c) A
        t = c                  Lc:
        if t goto Lthen          t = c
        goto Lelse               if t goto Lbody
      Lthen: A; goto Lend        goto Lend
      Lelse: B                 Lbody: A; goto Lc
      Lend:                    Lend:

* Source locations: an instruction defining a *variable* is located at the
  declared/assigned identifier; instructions defining temporaries are located
  at the sub-expression they compute.
"""

from typing import List, Optional

from src.ast import nodes as n
from src.ast.types import Type
from src.ir.tac import BinOp, CondJump, Copy, Input, Instr, Jump, Label, Print, TACProgram, UnOp
from src.ir.values import Const, Temp, Value, Var


class TACGenerator:
    def __init__(self):
        self._instrs: List[Instr] = []
        self._temps = 0
        self._labels = 0
        self._symbols = {}

    def generate(self, program: n.Program) -> TACProgram:
        for stmt in program.statements:
            self._stmt(stmt)
        return TACProgram(self._instrs, self._symbols)

    # -- helpers -----------------------------------------------------------
    def _temp(self) -> Temp:
        self._temps += 1
        return Temp(self._temps)

    def _label(self) -> str:
        self._labels += 1
        return f"L{self._labels}"

    def _emit(self, ins: Instr) -> None:
        self._instrs.append(ins)

    def _register(self, sym) -> Var:
        self._symbols[sym.unique_name] = sym
        return Var(sym.unique_name)

    # -- statements --------------------------------------------------------
    def _stmt(self, s: n.Node) -> None:
        if isinstance(s, (n.Block, n.Program)):
            for inner in s.statements:
                self._stmt(inner)
        elif isinstance(s, n.Declaration):
            dest = self._register(s.symbol)
            if s.init is None:
                self._emit(Input(dest, s.symbol.ty, loc=s.name_loc))
            else:
                self._expr(s.init, dest, s.symbol.ty, s.name_loc)
        elif isinstance(s, n.Assignment):
            dest = self._register(s.symbol)
            self._expr(s.value, dest, s.symbol.ty, s.loc)
        elif isinstance(s, n.PrintStmt):
            self._emit(Print(self._expr(s.value), loc=s.loc))
        elif isinstance(s, n.IfStmt):
            self._if(s)
        elif isinstance(s, n.WhileStmt):
            self._while(s)
        else:  # pragma: no cover
            raise TypeError(f"cannot lower {type(s).__name__}")

    def _if(self, s: n.IfStmt) -> None:
        cond = self._expr(s.cond)
        l_then, l_end = self._label(), None
        l_else = self._label() if s.else_block is not None else None
        l_end = self._label()
        self._emit(CondJump(cond, l_then, loc=s.cond.loc))
        self._emit(Jump(l_else if l_else else l_end, loc=s.loc))
        self._emit(Label(l_then))
        self._stmt(s.then_block)
        if s.else_block is not None:
            self._emit(Jump(l_end, loc=s.loc))
            self._emit(Label(l_else))
            self._stmt(s.else_block)
        self._emit(Label(l_end))

    def _while(self, s: n.WhileStmt) -> None:
        l_cond, l_body, l_end = self._label(), self._label(), self._label()
        self._emit(Label(l_cond))
        cond = self._expr(s.cond)
        self._emit(CondJump(cond, l_body, loc=s.cond.loc))
        self._emit(Jump(l_end, loc=s.loc))
        self._emit(Label(l_body))
        self._stmt(s.body)
        self._emit(Jump(l_cond, loc=s.loc))
        self._emit(Label(l_end))

    # -- expressions -------------------------------------------------------
    @staticmethod
    def _folded_const(e: n.Expr) -> Optional[Const]:
        """Constant for literals and for ``-literal``; ``None`` otherwise."""
        if isinstance(e, n.IntLiteral):
            return Const(e.value, Type.INT)
        if isinstance(e, n.FloatLiteral):
            return Const(e.value, Type.FLOAT)
        if isinstance(e, n.UnaryExpr) and e.op == "-":
            inner = TACGenerator._folded_const(e.operand)
            if inner is not None:
                return Const(-inner.value, inner.ty)
        return None

    def _expr(self, e: n.Expr, dest: Optional[Var] = None,
              dest_type: Optional[Type] = None, loc=None) -> Value:
        """Lower ``e`` and return the operand holding its value. If ``dest`` is
        given the value is produced directly into it."""
        const = self._folded_const(e)
        if const is not None:
            return self._leaf(const, dest, dest_type, loc or e.loc)
        if isinstance(e, n.Identifier):
            return self._leaf(Var(e.symbol.unique_name), dest, dest_type, loc or e.loc)
        if isinstance(e, n.UnaryExpr):
            operand = self._expr(e.operand)
            target = dest if dest is not None else self._temp()
            self._emit(UnOp(target, "neg", operand, dest_type or e.ty, loc=loc or e.loc))
            return target
        if isinstance(e, n.BinaryExpr):
            left = self._expr(e.left)
            right = self._expr(e.right)
            target = dest if dest is not None else self._temp()
            self._emit(BinOp(target, e.op, left, right, dest_type or e.ty, loc=loc or e.loc))
            return target
        raise TypeError(f"cannot lower {type(e).__name__}")  # pragma: no cover

    def _leaf(self, value: Value, dest, dest_type, loc) -> Value:
        if dest is None:
            return value
        self._emit(Copy(dest, value, dest_type, loc=loc))
        return dest


def generate_tac(program: n.Program) -> TACProgram:
    """Lower a program that has already passed semantic analysis."""
    return TACGenerator().generate(program)
