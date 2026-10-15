export type StageId = 
  | 'lexer'
  | 'parser'
  | 'ast'
  | 'tac'
  | 'cfg'
  | 'ssa'
  | 'ranges'
  | 'safety'
  | 'quantization'
  | 'diagnostics'
  | 'summary'
  | 'simulator';

export interface SourceLocation {
  line: number;
  col: number;
}

export interface TokenItem {
  kind: string;
  lexeme: string;
  loc: SourceLocation | null;
  value: string | null;
}

export interface ASTNode {
  node_type: string;
  loc: SourceLocation | null;
  statements?: ASTNode[];
  var_type?: string;
  name?: string;
  init?: ASTNode | null;
  name_loc?: SourceLocation | null;
  value?: any;
  cond?: ASTNode;
  then_block?: ASTNode;
  else_block?: ASTNode | null;
  body?: ASTNode;
  op?: string;
  left?: ASTNode;
  right?: ASTNode;
  operand?: ASTNode;
  op_loc?: SourceLocation | null;
  ty?: string | null;
  text?: string;
}

export interface TACInstr {
  text: string;
  loc: SourceLocation | null;
  op_type: string;
  defs: string[];
  uses: string[];
}

export interface CFGInstr {
  text: string;
  op_type: string;
  loc: SourceLocation | null;
  defs: string[];
  uses: string[];
  is_phi?: boolean;
  phi_dest?: string;
  phi_operands?: Record<string, string>;
}

export interface CFGBlock {
  id: number;
  name: string;
  label: string | null;
  preds: string[];
  succs: string[];
  pred_ids: number[];
  succ_ids: number[];
  instrs: CFGInstr[];
  is_unreachable: boolean;
  is_entry: boolean;
}

export interface CFGEdge {
  src: number;
  dst: number;
  src_name: string;
  dst_name: string;
  kind: 'fallthrough' | 'jump' | 'true' | 'false';
  is_back_edge: boolean;
}

export interface CFGData {
  entry: number;
  blocks: CFGBlock[];
  edges: CFGEdge[];
  raw_text: string;
}

export interface SSAPhi {
  dest: string;
  dest_type: string;
  operands: Record<string, string>;
  loc: SourceLocation | null;
}

export interface DominatorData {
  idom: Record<string, string | null>;
  frontiers: Record<string, string[]>;
  tree: Record<string, string[]>;
}

export interface SSAData {
  cfg: CFGData;
  phis: SSAPhi[];
  dom: DominatorData;
  defs: Record<string, { block_id: number; block_name: string; instr: string }>;
  raw_text: string;
}

export interface RangeValue {
  name: string;
  lo: number | null;
  hi: number | null;
  lo_repr: string;
  hi_repr: string;
  range_str: string;
  is_unknown: boolean;
  unreachable: boolean;
  integral: boolean;
  div_by_zero: boolean;
  widened: boolean;
  narrowed: boolean;
  original_type: string;
  safety_status: 'SAFE' | 'REJECTED' | 'BLOCKED' | 'UNKNOWN';
  is_quantized: boolean;
  rejection_reason: string | null;
  block_id: number | null;
  block_name: string | null;
  instruction: string;
  op_type?: string | null;
  op?: string | null;
  loc?: SourceLocation | null;
  operands?: string[];
  operand_vars?: string[];
  phi_incoming?: Record<string, string> | null;
  uses?: Array<{ block_id: number; block_name: string; instr: string; defs: string[] }>;
}

export interface RangesData {
  values: RangeValue[];
  sweeps: number;
  converged: boolean;
  widen_after: number;
  widened_count: number;
  narrowed_count: number;
}

export interface QuantDecision {
  name: string;
  safe: boolean;
  reasons: string[];
  primary_kind: string | null;
  rejection_kind: string | null;
  description: string;
  is_quantized: boolean;
  blocked_reason?: string | null;
}

export interface QuantizationData {
  decisions: QuantDecision[];
  quantized_vars: string[];
  blocked_vars: Record<string, string>;
  quantized_cfg: CFGData | null;
  raw_text: string;
}

export interface DiagnosticItem {
  name: string;
  source_variable: string | null;
  is_temporary: boolean;
  loc: SourceLocation | null;
  line: number | null;
  col: number | null;
  original_type: string;
  range_str: string;
  integral: boolean;
  unreachable: boolean;
  is_safe: boolean;
  safety_verdict: 'SAFE' | 'REJECTED';
  is_quantized: boolean;
  reasons: string[];
  blocked_reason?: string | null;
  transformation: string;
}

export interface SummaryData {
  total_ssa_values: number;
  safe_count: number;
  quantized_count: number;
  blocked_count: number;
  rejected_count: number;
  safe_percentage: number;
  quantized_percentage: number;
  rejections_by_kind: Record<string, number>;
  theoretical_storage_reduction_pct: number;
  simulation_equivalent: boolean | null;
}

export interface SimulationData {
  original_output: any[];
  quantized_output: any[];
  is_equivalent: boolean;
  error?: string | null;
}

export interface CompileError {
  stage: string;
  message: string;
  line?: number | null;
  col?: number | null;
  details?: string | null;
}

export interface CompileResponse {
  success: boolean;
  source?: string;
  tokens?: TokenItem[];
  ast?: ASTNode;
  tac?: {
    instructions: TACInstr[];
    raw_text: string;
  };
  cfg?: CFGData;
  ssa?: SSAData;
  ranges?: RangesData;
  quantization?: QuantizationData;
  diagnostics?: DiagnosticItem[];
  summary?: SummaryData;
  simulation?: SimulationData;
  error?: CompileError;
}

export interface ExampleItem {
  id: string;
  name: string;
  category: string;
  description: string;
  source: string;
  narrow?: boolean;
  widen_after?: number;
  prune_unreachable?: boolean;
}
