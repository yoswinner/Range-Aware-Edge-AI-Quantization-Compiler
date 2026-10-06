"""Source positions shared by every compiler stage."""

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class SourceLocation:
    """1-based line and column of the first character of a construct."""

    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.line}:{self.column}"

    def describe(self) -> str:
        return f"line {self.line}, column {self.column}"
