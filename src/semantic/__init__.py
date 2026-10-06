"""Semantic analysis: scopes, declaration-before-use, type checking."""

from src.semantic.analyzer import SemanticAnalyzer, SemanticResult, analyze, check
from src.semantic.symbols import Symbol, SymbolTable

__all__ = ["SemanticAnalyzer", "SemanticResult", "analyze", "check", "Symbol", "SymbolTable"]
