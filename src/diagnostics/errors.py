"""Compiler error types. Every error carries the source location it refers to."""

from dataclasses import dataclass
from typing import List, Optional

from src.diagnostics.location import SourceLocation


class CompilerError(Exception):
    """Base class for all errors raised by a compiler stage."""

    stage = "compiler"

    def __init__(self, message: str, loc: Optional[SourceLocation] = None):
        self.message = message
        self.loc = loc
        super().__init__(self.format())

    def format(self) -> str:
        if self.loc is None:
            return f"{self.stage} error: {self.message}"
        return f"{self.stage} error at {self.loc.describe()}: {self.message}"


class LexError(CompilerError):
    stage = "lexical"


class ParseError(CompilerError):
    stage = "syntax"


class SSAError(CompilerError):
    """Raised when SSA construction hits an inconsistency (internal invariant)."""

    stage = "ssa"


@dataclass(frozen=True)
class Diagnostic:
    """One semantic-analysis finding (the analyzer collects all of them)."""

    message: str
    loc: SourceLocation

    def format(self) -> str:
        return f"semantic error at {self.loc.describe()}: {self.message}"


class SemanticError(CompilerError):
    """Raised after semantic analysis when at least one diagnostic was produced."""

    stage = "semantic"

    def __init__(self, diagnostics: List[Diagnostic]):
        self.diagnostics = list(diagnostics)
        first = self.diagnostics[0]
        Exception.__init__(self, "\n".join(d.format() for d in self.diagnostics))
        self.message = first.message
        self.loc = first.loc
