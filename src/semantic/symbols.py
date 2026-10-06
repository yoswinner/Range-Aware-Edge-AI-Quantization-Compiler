"""Symbols and lexical scopes."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.ast.types import Type
from src.diagnostics.location import SourceLocation


@dataclass(eq=False)
class Symbol:
    """A declared variable.

    ``unique_name`` is what the IR uses. Block scoping lets the same source name
    be declared more than once (in sibling or nested blocks); each declaration
    gets its own IR variable (``x``, ``x$1``, ``x$2``, ...) so that SSA
    construction never has to reason about shadowing.
    """

    name: str
    unique_name: str
    ty: Type
    decl_loc: SourceLocation


class SymbolTable:
    def __init__(self):
        self._scopes: List[Dict[str, Symbol]] = []
        self._declared_count: Dict[str, int] = {}
        self.all_symbols: List[Symbol] = []

    def push_scope(self) -> None:
        self._scopes.append({})

    def pop_scope(self) -> None:
        self._scopes.pop()

    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        return self._scopes[-1].get(name)

    def declare(self, name: str, ty: Type, loc: SourceLocation) -> Symbol:
        count = self._declared_count.get(name, 0)
        self._declared_count[name] = count + 1
        unique = name if count == 0 else f"{name}${count}"
        sym = Symbol(name, unique, ty, loc)
        self._scopes[-1][name] = sym
        self.all_symbols.append(sym)
        return sym
