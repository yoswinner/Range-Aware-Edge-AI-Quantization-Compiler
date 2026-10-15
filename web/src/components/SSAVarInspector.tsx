import React from 'react';
import { 
  X, 
  ArrowRight, 
  ShieldCheck, 
  AlertTriangle, 
  Layers, 
  ExternalLink, 
  CornerDownRight, 
  Copy, 
  Check, 
  Info,
  GitCommit,
  Binary
} from 'lucide-react';
import { RangeValue } from '../types';

interface SSAVarInspectorProps {
  selectedVar: RangeValue | null;
  allVars: RangeValue[];
  onSelectVar: (name: string) => void;
  onClose: () => void;
}

export const SSAVarInspector: React.FC<SSAVarInspectorProps> = ({
  selectedVar,
  allVars,
  onSelectVar,
  onClose,
}) => {
  const [copied, setCopied] = React.useState(false);

  if (!selectedVar) return null;

  const handleCopyInstruction = () => {
    navigator.clipboard.writeText(selectedVar.instruction);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isSafe = selectedVar.safety_status === 'SAFE';
  const isOverflow = selectedVar.hi !== null && (selectedVar.hi > 127 || (selectedVar.lo !== null && selectedVar.lo < -128));

  // Find all variable names in the program to know what operands are clickable
  const varNamesSet = new Set(allVars.map(v => v.name));

  return (
    <aside 
      className="ssa-inspector-drawer"
      aria-label={`SSA Variable Inspector for ${selectedVar.name}`}
      style={{
        width: '380px',
        height: '100%',
        background: 'var(--bg-surface-elevated)',
        borderLeft: '1px solid var(--border-default)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 25,
        boxShadow: '-6px 0 24px rgba(0, 0, 0, 0.45)',
        flexShrink: 0,
        position: 'relative',
        animation: 'slideIn 180ms ease'
      }}
    >
      {/* Drawer Header */}
      <div style={{
        padding: '12px 18px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'var(--bg-surface)',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitCommit size={16} style={{ color: 'var(--accent-cyan)' }} />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ 
                fontFamily: 'var(--font-mono)', 
                fontWeight: 700, 
                fontSize: '14px', 
                color: 'var(--accent-cyan-light)' 
              }}>
                {selectedVar.name}
              </span>
              <span className="badge badge-neutral" style={{ fontSize: '10px' }}>
                {selectedVar.original_type}
              </span>
              {selectedVar.is_quantized && (
                <span className="badge badge-lime" style={{ fontSize: '10px' }}>
                  → int8
                </span>
              )}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              SSA Variable Definition & Diagnostics
            </div>
          </div>
        </div>

        <button 
          className="btn-icon" 
          onClick={onClose}
          aria-label="Close Inspector"
          style={{ padding: '6px', borderRadius: '4px' }}
        >
          <X size={15} />
        </button>
      </div>

      {/* Drawer Scrollable Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: '16px' }}>

        {/* 1. Definition & Instruction Card */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-default)',
          borderRadius: '6px',
          padding: '12px 14px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Defining Instruction:
            </span>
            <button 
              className="btn btn-secondary"
              onClick={handleCopyInstruction}
              style={{ height: '22px', padding: '0 6px', fontSize: '10px' }}
            >
              {copied ? <Check size={10} style={{ color: 'var(--accent-lime)' }} /> : <Copy size={10} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          <div style={{
            background: 'var(--bg-canvas)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '4px',
            padding: '8px 10px',
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            color: 'var(--text-primary)',
            lineHeight: 1.5,
            wordBreak: 'break-all'
          }}>
            <code>{selectedVar.instruction}</code>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '10px', fontSize: '11px' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Operation: </span>
              <strong style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                {selectedVar.op_type || 'Instruction'} {selectedVar.op ? `(${selectedVar.op})` : ''}
              </strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Basic Block: </span>
              <strong style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                {selectedVar.block_name || 'B?'}
              </strong>
            </div>
            {selectedVar.loc && (
              <div style={{ gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--text-muted)' }}>Source Location: </span>
                <span style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                  Line {selectedVar.loc.line}, Column {selectedVar.loc.col}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* 2. Operands with Clickable Interactivity */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-default)',
          borderRadius: '6px',
          padding: '12px 14px',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '8px' }}>
            Operands ({selectedVar.operands?.length || 0}):
          </div>

          {!selectedVar.operands || selectedVar.operands.length === 0 ? (
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontStyle: 'italic' }}>
              Constant declaration / external input (no variable operands)
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {selectedVar.operands.map((opStr, idx) => {
                const isVar = varNamesSet.has(opStr);
                const opValObj = allVars.find(v => v.name === opStr);

                return (
                  <div 
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      background: 'var(--bg-surface-elevated)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '4px',
                      padding: '6px 10px',
                      fontSize: '11.5px',
                      fontFamily: 'var(--font-mono)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>#{idx + 1}:</span>
                      {isVar ? (
                        <button
                          onClick={() => onSelectVar(opStr)}
                          className="btn"
                          title={`Click to inspect operand ${opStr}`}
                          style={{
                            height: '24px',
                            padding: '0 8px',
                            background: 'rgba(6, 182, 212, 0.12)',
                            border: '1px solid rgba(6, 182, 212, 0.35)',
                            color: 'var(--accent-cyan-light)',
                            fontFamily: 'var(--font-mono)',
                            fontSize: '11px',
                            fontWeight: 600,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                        >
                          <span>{opStr}</span>
                          <ExternalLink size={10} />
                        </button>
                      ) : (
                        <span style={{ color: 'var(--accent-amber-light)' }}>
                          {opStr} (literal)
                        </span>
                      )}
                    </div>

                    {opValObj && (
                      <span style={{ fontSize: '11px', color: opValObj.safety_status === 'SAFE' ? 'var(--accent-lime)' : 'var(--text-secondary)' }}>
                        range: {opValObj.range_str}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* 3. φ-Node Inflows if applicable */}
        {selectedVar.phi_incoming && Object.keys(selectedVar.phi_incoming).length > 0 && (
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--accent-purple-border)',
            borderRadius: '6px',
            padding: '12px 14px',
          }}>
            <div style={{ fontSize: '11px', color: 'var(--accent-purple-light)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '8px' }}>
              φ-Node Predecessor Inflows:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {Object.entries(selectedVar.phi_incoming).map(([predBlock, incomingVar]) => {
                const isClickable = varNamesSet.has(incomingVar);
                return (
                  <div 
                    key={predBlock}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      background: 'var(--bg-surface-elevated)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '4px',
                      padding: '5px 8px',
                      fontSize: '11px',
                      fontFamily: 'var(--font-mono)'
                    }}
                  >
                    <span style={{ color: 'var(--text-muted)' }}>From {predBlock}:</span>
                    {isClickable ? (
                      <button
                        onClick={() => onSelectVar(incomingVar)}
                        className="btn"
                        style={{
                          height: '22px',
                          padding: '0 6px',
                          background: 'rgba(168, 85, 247, 0.12)',
                          border: '1px solid var(--accent-purple-border)',
                          color: 'var(--accent-purple-light)',
                          fontFamily: 'var(--font-mono)',
                          fontSize: '11px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                      >
                        <span>{incomingVar}</span>
                        <ExternalLink size={9} />
                      </button>
                    ) : (
                      <span style={{ color: 'var(--text-primary)' }}>{incomingVar}</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* 4. Abstract Range Analysis & Integrality */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-default)',
          borderRadius: '6px',
          padding: '12px 14px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Abstract Range & Integrality
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Inferred Interval:</span>
            <span className="mono" style={{ 
              fontWeight: 700, 
              color: isSafe ? 'var(--accent-lime-light)' : (isOverflow ? 'var(--accent-red-light)' : 'var(--text-primary)') 
            }}>
              {selectedVar.range_str}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Integrality Check:</span>
            {selectedVar.integral ? (
              <span className="badge badge-lime">Integral (Whole)</span>
            ) : (
              <span className="badge badge-amber">Non-Integral (Float)</span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Division by Zero Risk:</span>
            {selectedVar.div_by_zero ? (
              <span className="badge badge-red">Flagged Unsafe</span>
            ) : (
              <span className="badge badge-neutral">None (Safe)</span>
            )}
          </div>

          {(selectedVar.widened || selectedVar.narrowed) && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Loop Convergence:</span>
              <div style={{ display: 'flex', gap: '4px' }}>
                {selectedVar.widened && <span className="badge badge-amber">Widened</span>}
                {selectedVar.narrowed && <span className="badge badge-lime">Narrowed</span>}
              </div>
            </div>
          )}
        </div>

        {/* 5. INT8 Safety & Retyping Verdict */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid',
          borderColor: isSafe ? 'var(--accent-lime-border)' : 'var(--accent-red-border)',
          borderRadius: '6px',
          padding: '12px 14px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              INT8 Safety Verdict
            </span>
            <span className={isSafe ? 'badge badge-lime' : 'badge badge-red'}>
              {selectedVar.safety_status}
            </span>
          </div>

          <div style={{ fontSize: '12px', display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Retyped to INT8:</span>
            <span style={{ 
              fontWeight: 600, 
              color: selectedVar.is_quantized ? 'var(--accent-lime)' : 'var(--text-muted)' 
            }}>
              {selectedVar.is_quantized ? 'YES (int8)' : `NO (kept ${selectedVar.original_type})`}
            </span>
          </div>

          {selectedVar.rejection_reason && (
            <div style={{ 
              fontSize: '11px', 
              color: 'var(--accent-red-light)', 
              background: 'var(--accent-red-bg)', 
              padding: '8px 10px', 
              borderRadius: '4px',
              border: '1px solid var(--accent-red-border)',
              lineHeight: 1.4,
              marginTop: '4px'
            }}>
              <strong>Rejection Reason:</strong> {selectedVar.rejection_reason}
            </div>
          )}
        </div>

        {/* 6. Downstream Uses & Consumers */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-default)',
          borderRadius: '6px',
          padding: '12px 14px',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '8px' }}>
            Downstream Uses ({selectedVar.uses?.length || 0}):
          </div>

          {!selectedVar.uses || selectedVar.uses.length === 0 ? (
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontStyle: 'italic' }}>
              Terminal value (not consumed by subsequent instructions)
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {selectedVar.uses.map((u, i) => (
                <div 
                  key={i}
                  style={{
                    background: 'var(--bg-surface-elevated)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '4px',
                    padding: '6px 10px',
                    fontSize: '11px',
                    fontFamily: 'var(--font-mono)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div>
                    <span style={{ color: 'var(--accent-cyan)', marginRight: '6px' }}>{u.block_name}:</span>
                    <span style={{ color: 'var(--text-primary)' }}>{u.instr}</span>
                  </div>

                  {u.defs.length > 0 && varNamesSet.has(u.defs[0]) && (
                    <button
                      onClick={() => onSelectVar(u.defs[0])}
                      className="btn-icon"
                      title={`Inspect consumer ${u.defs[0]}`}
                      style={{ padding: '2px 4px', color: 'var(--accent-cyan)' }}
                    >
                      <ArrowRight size={12} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </aside>
  );
};
