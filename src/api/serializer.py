"""Structured JSON serialization for compiler pipeline results.

Safely converts AST, TAC, CFG, SSA, range analysis, quantization decisions,
diagnostics, and simulation results into JSON-serializable dictionaries.
"""

from fractions import Fraction
from typing import Any, Dict, List, Optional, Set

from src.analysis.abstract_value import AbsVal
from src.analysis.refinement import refine_edge
from src.analysis.range_analysis import RangeResult
from src.ast import nodes
from src.ast.types import Type
from src.backend.simulator import SimulationResult
from src.cfg.cfg import CFG, Edge
from src.diagnostics.location import SourceLocation
from src.diagnostics.report import ValueDiagnostic
from src.ir.tac import BinOp, CondJump, Copy, Input, Instr, Jump, Label, Phi, Print, TACProgram, UnOp
from src.ir.values import Const, Temp, Value, Var
from src.pipeline import CompilationResult
from src.quantization.quantizer import QuantizationResult
from src.quantization.safety import RejectKind, SAFE_REASON, SafetyDecision
from src.ssa.construction import SSAProgram


def _format_fraction(f: Optional[Fraction]) -> Optional[str]:
    if f is None:
        return None
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _fraction_to_float(f: Optional[Fraction]) -> Optional[float]:
    if f is None:
        return None
    return float(f)


def _serialize_location(loc: Optional[SourceLocation]) -> Optional[Dict[str, int]]:
    if loc is None:
        return None
    return {"line": loc.line, "col": loc.column}


def serialize_token(token: Any) -> Dict[str, Any]:
    val = token.value
    val_repr = None
    if val is not None:
        val_repr = _format_fraction(val) if isinstance(val, Fraction) else str(val)

    return {
        "kind": token.kind.name,
        "lexeme": token.lexeme,
        "loc": _serialize_location(token.loc),
        "value": val_repr,
    }


def serialize_ast_node(node: nodes.Node) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "node_type": node.__class__.__name__,
        "loc": _serialize_location(node.loc),
    }

    if isinstance(node, nodes.Program):
        base["statements"] = [serialize_ast_node(s) for s in node.statements]
    elif isinstance(node, nodes.Declaration):
        base["var_type"] = str(node.var_type)
        base["name"] = node.name
        base["init"] = serialize_ast_node(node.init) if node.init else None
        base["name_loc"] = _serialize_location(node.name_loc)
    elif isinstance(node, nodes.Assignment):
        base["name"] = node.name
        base["value"] = serialize_ast_node(node.value)
    elif isinstance(node, nodes.Block):
        base["statements"] = [serialize_ast_node(s) for s in node.statements]
    elif isinstance(node, nodes.IfStmt):
        base["cond"] = serialize_ast_node(node.cond)
        base["then_block"] = serialize_ast_node(node.then_block)
        base["else_block"] = serialize_ast_node(node.else_block) if node.else_block else None
    elif isinstance(node, nodes.WhileStmt):
        base["cond"] = serialize_ast_node(node.cond)
        base["body"] = serialize_ast_node(node.body)
    elif isinstance(node, nodes.PrintStmt):
        base["value"] = serialize_ast_node(node.value)
    elif isinstance(node, nodes.BinaryExpr):
        base["op"] = node.op
        base["left"] = serialize_ast_node(node.left)
        base["right"] = serialize_ast_node(node.right)
        base["op_loc"] = _serialize_location(node.op_loc)
        base["ty"] = str(node.ty) if node.ty else None
    elif isinstance(node, nodes.UnaryExpr):
        base["op"] = node.op
        base["operand"] = serialize_ast_node(node.operand)
        base["ty"] = str(node.ty) if node.ty else None
    elif isinstance(node, nodes.Identifier):
        base["name"] = node.name
        base["ty"] = str(node.ty) if node.ty else None
    elif isinstance(node, nodes.IntLiteral):
        base["value"] = int(node.value)
        base["ty"] = str(node.ty) if node.ty else "int"
    elif isinstance(node, nodes.FloatLiteral):
        base["value"] = float(node.value)
        base["text"] = node.text
        base["ty"] = str(node.ty) if node.ty else "float"

    return base


def serialize_tac_instr(instr: Instr) -> Dict[str, Any]:
    return {
        "text": str(instr),
        "loc": _serialize_location(instr.loc),
        "op_type": instr.__class__.__name__,
        "defs": [str(d) for d in instr.defs()],
        "uses": [str(u) for u in instr.uses()],
    }


def compute_reachable_cfg_blocks(
    cfg: CFG,
    ssa: Optional[SSAProgram] = None,
    ranges: Optional[RangeResult] = None,
) -> Set[int]:
    """Compute the set of blocks reachable from entry considering branch conditions."""
    if cfg.entry is None or cfg.entry not in cfg.blocks:
        return set(cfg.blocks.keys())

    reachable: Set[int] = {cfg.entry}
    queue: List[int] = [cfg.entry]

    while queue:
        curr = queue.pop(0)
        curr_env = ranges.block_out.get(curr, {}) if ranges else {}
        clean_env = {k: v for k, v in curr_env.items() if not v.unreachable}

        blk = cfg.blocks.get(curr)
        last_ins = blk.instrs[-1] if (blk and blk.instrs) else None
        is_cond = isinstance(last_ins, CondJump)

        for succ in cfg.succs(curr):
            try:
                kind = cfg.edge_kind(curr, succ)
            except KeyError:
                kind = "fallthrough"

            if is_cond and kind in ("true", "false") and ranges and ssa:
                edge_env = refine_edge(curr, succ, clean_env, ssa)
                if any(v.unreachable for v in edge_env.values()):
                    continue

            if succ not in reachable:
                reachable.add(succ)
                queue.append(succ)

    return reachable


def serialize_cfg(cfg: CFG, ssa: Optional[SSAProgram] = None, ranges: Optional[RangeResult] = None) -> Dict[str, Any]:
    blocks_data: List[Dict[str, Any]] = []
    back_edges_set = set(cfg.back_edges())
    reachable_blocks = compute_reachable_cfg_blocks(cfg, ssa, ranges)

    for bid in sorted(cfg.blocks.keys()):
        blk = cfg.blocks[bid]
        # Check if block is unreachable
        is_unreachable = (bid not in reachable_blocks)

        instrs_data = []
        for ins in blk.instrs:
            ins_info = {
                "text": str(ins),
                "op_type": ins.__class__.__name__,
                "loc": _serialize_location(ins.loc),
                "defs": [str(d) for d in ins.defs()],
                "uses": [str(u) for u in ins.uses()],
            }
            if isinstance(ins, Phi):
                ins_info["is_phi"] = True
                ins_info["phi_dest"] = str(ins.dest)
                ins_info["phi_operands"] = {f"B{pred_id}": str(val) for pred_id, val in ins.incoming.items()}
            instrs_data.append(ins_info)

        blocks_data.append({
            "id": bid,
            "name": blk.name,
            "label": blk.label,
            "preds": [f"B{p}" for p in cfg.preds(bid)],
            "succs": [f"B{s}" for s in cfg.succs(bid)],
            "pred_ids": cfg.preds(bid),
            "succ_ids": cfg.succs(bid),
            "instrs": instrs_data,
            "is_unreachable": is_unreachable,
            "is_entry": (bid == cfg.entry),
        })

    edges_data: List[Dict[str, Any]] = []
    for edge in cfg.edges:
        is_back = (edge.src, edge.dst) in back_edges_set
        edges_data.append({
            "src": edge.src,
            "dst": edge.dst,
            "src_name": f"B{edge.src}",
            "dst_name": f"B{edge.dst}",
            "kind": edge.kind,
            "is_back_edge": is_back,
        })

    return {
        "entry": cfg.entry,
        "blocks": blocks_data,
        "edges": edges_data,
        "raw_text": cfg.format(),
    }


def serialize_ssa(ssa: SSAProgram) -> Dict[str, Any]:
    phis_data = []
    for phi in ssa.phis():
        phis_data.append({
            "dest": str(phi.dest),
            "dest_type": str(phi.dest_type),
            "operands": {f"B{pred_id}": str(val) for pred_id, val in phi.incoming.items()},
            "loc": _serialize_location(phi.loc),
        })

    dom_data = {
        "idom": {f"B{b}": f"B{idom}" if idom is not None else None for b, idom in ssa.dom.idom.items()},
        "frontiers": {f"B{b}": [f"B{df}" for df in sorted(dfs)] for b, dfs in ssa.dom.frontiers.items()},
        "tree": {f"B{b}": [f"B{child}" for child in sorted(children)] for b, children in ssa.dom.children.items()},
    }

    defs_data = {}
    for val, (bid, ins) in ssa.defs.items():
        defs_data[str(val)] = {
            "block_id": bid,
            "block_name": f"B{bid}",
            "instr": str(ins),
        }

    return {
        "cfg": serialize_cfg(ssa.cfg, ssa=ssa),
        "phis": phis_data,
        "dom": dom_data,
        "defs": defs_data,
        "raw_text": ssa.format(annotate=True),
    }


def serialize_ranges(ranges: RangeResult, ssa: SSAProgram, quant: QuantizationResult) -> Dict[str, Any]:
    # Build uses map across SSA instructions
    uses_map: Dict[Value, List[Dict[str, Any]]] = {}
    for bid, ins in ssa.instructions():
        for u in ins.uses():
            if u not in uses_map:
                uses_map[u] = []
            uses_map[u].append({
                "block_id": bid,
                "block_name": f"B{bid}",
                "instr": str(ins),
                "defs": [str(d) for d in ins.defs()],
            })

    values_list = []
    for v in sorted(ranges.values.keys(), key=lambda x: str(x)):
        fact = ranges.values[v]
        decision = quant.decisions.get(v)
        is_quant = quant.is_quantized(v)
        blocked_reason = quant.blocked.get(v)

        def_info = ssa.defs.get(v)
        block_id = def_info[0] if def_info else None
        ins = def_info[1] if def_info else None
        instr_str = str(ins) if ins else ""

        # Formatting range string
        range_str = str(fact)
        safety_status = "UNKNOWN"
        rejection_reason = None
        if decision:
            safety_status = "SAFE" if decision.safe else "REJECTED"
            if not decision.safe:
                rejection_reason = "; ".join(decision.reasons)
        if blocked_reason:
            safety_status = "BLOCKED"
            rejection_reason = blocked_reason

        # Original type & operation details
        orig_type = "unknown"
        op_type = None
        op = None
        loc = None
        operands = []
        operand_vars = []
        phi_incoming = None

        if ins:
            op_type = ins.__class__.__name__
            loc = _serialize_location(ins.loc)
            operands = [str(u) for u in ins.uses()]
            operand_vars = [str(u) for u in ins.uses() if not isinstance(u, Const)]
            if hasattr(ins, "dest_type") and ins.dest_type:
                orig_type = str(ins.dest_type)
            elif hasattr(ins, "ty") and ins.ty:
                orig_type = str(ins.ty)
            if hasattr(ins, "op"):
                op = str(ins.op)
            if isinstance(ins, Phi):
                phi_incoming = {f"B{b}": str(val) for b, val in ins.incoming.items()}

        values_list.append({
            "name": str(v),
            "lo": _fraction_to_float(fact.lo),
            "hi": _fraction_to_float(fact.hi),
            "lo_repr": _format_fraction(fact.lo) if fact.lo is not None else "-inf",
            "hi_repr": _format_fraction(fact.hi) if fact.hi is not None else "+inf",
            "range_str": range_str,
            "is_unknown": fact.is_unknown,
            "unreachable": fact.unreachable,
            "integral": fact.integral,
            "div_by_zero": fact.div_zero,
            "widened": v in ranges.widened,
            "narrowed": v in ranges.narrowed,
            "original_type": orig_type,
            "safety_status": safety_status,
            "is_quantized": is_quant,
            "rejection_reason": rejection_reason,
            "block_id": block_id,
            "block_name": f"B{block_id}" if block_id is not None else None,
            "instruction": instr_str,
            "op_type": op_type,
            "op": op,
            "loc": loc,
            "operands": operands,
            "operand_vars": operand_vars,
            "phi_incoming": phi_incoming,
            "uses": uses_map.get(v, []),
        })

    return {
        "values": values_list,
        "sweeps": ranges.sweeps,
        "converged": ranges.converged,
        "widen_after": ranges.widen_after,
        "widened_count": len(ranges.widened),
        "narrowed_count": len(ranges.narrowed),
    }


def serialize_quantization(quant: QuantizationResult, ssa: SSAProgram) -> Dict[str, Any]:
    decisions_list = []
    for v in sorted(quant.decisions.keys(), key=lambda x: str(x)):
        dec = quant.decisions[v]
        decisions_list.append({
            "name": str(v),
            "safe": dec.safe,
            "reasons": list(dec.reasons),
            "primary_kind": dec.primary_kind.name if dec.primary_kind else None,
            "rejection_kind": dec.primary_kind.name if dec.primary_kind else None,
            "description": dec.primary_reason or "",
            "is_quantized": quant.is_quantized(v),
            "blocked_reason": quant.blocked.get(v),
        })

    quantized_cfg = serialize_cfg(quant.program.cfg, ssa=quant.program) if quant.program else None

    return {
        "decisions": decisions_list,
        "quantized_vars": [str(v) for v in sorted(quant.quantized, key=lambda x: str(x))],
        "blocked_vars": {str(k): v for k, v in quant.blocked.items()},
        "quantized_cfg": quantized_cfg,
        "raw_text": quant.program.format() if quant.program else "",
    }


def serialize_diagnostics(diags: List[ValueDiagnostic]) -> List[Dict[str, Any]]:
    result = []
    for d in diags:
        if d.quantized:
            trans = f"{d.original_type.display} -> int8"
        elif d.decision.safe:
            trans = f"none (kept {d.original_type.display}): {d.blocked_reason}"
        else:
            trans = f"none (kept {d.original_type.display})"

        result.append({
            "name": d.name,
            "source_variable": d.source_variable,
            "is_temporary": d.is_temporary,
            "loc": _serialize_location(d.loc),
            "line": d.loc.line if d.loc else None,
            "col": d.loc.column if d.loc else None,
            "original_type": d.original_type.display,
            "range_str": d.abstract.format_range(),
            "integral": d.abstract.integral,
            "unreachable": d.abstract.unreachable,
            "is_safe": d.decision.safe,
            "safety_verdict": "SAFE" if d.decision.safe else "REJECTED",
            "is_quantized": d.quantized,
            "reasons": list(d.decision.reasons) if d.decision.reasons else [SAFE_REASON],
            "blocked_reason": d.blocked_reason,
            "transformation": trans,
        })
    return result


def serialize_summary(res: CompilationResult) -> Dict[str, Any]:
    total_vars = len(res.ranges.values)
    safe_vars = sum(1 for d in res.quantization.decisions.values() if d.safe)
    quant_vars = len(res.quantization.quantized)
    blocked_vars = len(res.quantization.blocked)
    reject_vars = sum(1 for d in res.quantization.decisions.values() if not d.safe)

    rejections_by_kind: Dict[str, int] = {}
    for d in res.quantization.decisions.values():
        if not d.safe:
            k = d.primary_kind.name if d.primary_kind else "OTHER"
            rejections_by_kind[k] = rejections_by_kind.get(k, 0) + 1

    safe_pct = (safe_vars / total_vars * 100.0) if total_vars > 0 else 0.0
    quant_pct = (quant_vars / total_vars * 100.0) if total_vars > 0 else 0.0

    # Theoretical storage reduction:
    # Baseline: 32 bits per variable.
    # Quantized: 8 bits for quantized variables, 32 bits for retained variables.
    baseline_bits = total_vars * 32
    quantized_bits = (quant_vars * 8) + ((total_vars - quant_vars) * 32)
    storage_reduction_pct = 0.0
    if baseline_bits > 0:
        storage_reduction_pct = round(((baseline_bits - quantized_bits) / baseline_bits) * 100.0, 1)

    sim_match = None
    if res.simulation:
        sim_match = res.simulation.is_equivalent

    return {
        "total_ssa_values": total_vars,
        "safe_count": safe_vars,
        "quantized_count": quant_vars,
        "blocked_count": blocked_vars,
        "rejected_count": reject_vars,
        "safe_percentage": round(safe_pct, 1),
        "quantized_percentage": round(quant_pct, 1),
        "rejections_by_kind": rejections_by_kind,
        "theoretical_storage_reduction_pct": storage_reduction_pct,
        "simulation_equivalent": sim_match,
    }


def serialize_simulation(sim: Optional[SimulationResult]) -> Optional[Dict[str, Any]]:
    if sim is None:
        return None
    return {
        "original_output": sim.original_output,
        "quantized_output": sim.quantized_output,
        "is_equivalent": sim.is_equivalent,
        "error": sim.error,
    }


def serialize_compilation_result(res: CompilationResult) -> Dict[str, Any]:
    """Serialize the entire compilation result into structured JSON."""
    return {
        "success": True,
        "source": res.source,
        "tokens": [serialize_token(t) for t in res.tokens],
        "ast": serialize_ast_node(res.ast),
        "tac": {
            "instructions": [serialize_tac_instr(ins) for ins in res.tac.instrs],
            "raw_text": res.tac.format(),
        },
        "cfg": serialize_cfg(res.cfg, ssa=res.ssa, ranges=res.ranges),
        "ssa": serialize_ssa(res.ssa),
        "ranges": serialize_ranges(res.ranges, res.ssa, res.quantization),
        "quantization": serialize_quantization(res.quantization, res.ssa),
        "diagnostics": serialize_diagnostics(res.diagnostics),
        "summary": serialize_summary(res),
        "simulation": serialize_simulation(res.simulation),
    }
