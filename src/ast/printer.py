"""Indented text dump of an AST (used by ``--emit ast`` and by tests)."""

from src.ast import nodes as n


def _fmt_ty(node) -> str:
    ty = getattr(node, "ty", None)
    return f" :{ty.display}" if ty is not None else ""


def dump(node, indent: int = 0) -> str:
    pad = "  " * indent
    at = f" @{node.loc}"

    if isinstance(node, n.Program):
        head = f"{pad}Program{at}"
        return "\n".join([head] + [dump(s, indent + 1) for s in node.statements])
    if isinstance(node, n.Block):
        head = f"{pad}Block{at}"
        return "\n".join([head] + [dump(s, indent + 1) for s in node.statements])
    if isinstance(node, n.Declaration):
        head = f"{pad}Declaration {node.var_type.value} {node.name} @{node.name_loc}"
        if node.init is None:
            return head + " (no initializer: external input)"
        return head + "\n" + dump(node.init, indent + 1)
    if isinstance(node, n.Assignment):
        return f"{pad}Assignment {node.name}{at}\n" + dump(node.value, indent + 1)
    if isinstance(node, n.IfStmt):
        parts = [f"{pad}If{at}", f"{pad}  cond:", dump(node.cond, indent + 2),
                 f"{pad}  then:", dump(node.then_block, indent + 2)]
        if node.else_block is not None:
            parts += [f"{pad}  else:", dump(node.else_block, indent + 2)]
        return "\n".join(parts)
    if isinstance(node, n.WhileStmt):
        return "\n".join([f"{pad}While{at}", f"{pad}  cond:", dump(node.cond, indent + 2),
                          f"{pad}  body:", dump(node.body, indent + 2)])
    if isinstance(node, n.PrintStmt):
        return f"{pad}Print{at}\n" + dump(node.value, indent + 1)
    if isinstance(node, n.IntLiteral):
        return f"{pad}IntLiteral {node.value}{at}{_fmt_ty(node)}"
    if isinstance(node, n.FloatLiteral):
        return f"{pad}FloatLiteral {node.text}{at}{_fmt_ty(node)}"
    if isinstance(node, n.Identifier):
        return f"{pad}Identifier {node.name}{at}{_fmt_ty(node)}"
    if isinstance(node, n.UnaryExpr):
        return f"{pad}Unary {node.op}{at}{_fmt_ty(node)}\n" + dump(node.operand, indent + 1)
    if isinstance(node, n.BinaryExpr):
        return (f"{pad}Binary {node.op}{at}{_fmt_ty(node)}\n"
                + dump(node.left, indent + 1) + "\n" + dump(node.right, indent + 1))
    raise TypeError(f"cannot dump {type(node).__name__}")
