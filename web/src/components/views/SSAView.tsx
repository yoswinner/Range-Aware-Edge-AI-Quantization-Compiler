import React, { useState } from 'react';
import { GitCommit, Copy, Check, GitFork, ArrowDownRight, Layers } from 'lucide-react';
import { SSAData } from '../../types';

interface SSAViewProps {
  ssa: SSAData;
  selectedVarName?: string | null;
  onSelectVar?: (name: string) => void;
}

export const SSAView: React.FC<SSAViewProps> = ({ 
  ssa, 
  selectedVarName, 
  onSelectVar 
}) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'ir' | 'phis' | 'dom'>('ir');

  const handleCopy = () => {
    navigator.clipboard.writeText(ssa.raw_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* View Header with Sub-tabs */}
      <div style={{
        padding: '10px 16px',
        borderBottom: '1px solid var(--border-default)',
        background: 'var(--bg-surface-elevated)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <GitCommit size={15} style={{ color: 'var(--accent-purple-light)' }} />
            <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
              Static Single Assignment (SSA)
            </span>
          </div>

          {/* Sub-tabs */}
          <div style={{ display: 'flex', background: 'var(--bg-surface)', padding: '2px', borderRadius: '5px', border: '1px solid var(--border-default)' }}>
            <button
              onClick={() => setActiveTab('ir')}
              className="btn"
              style={{
                height: '24px',
                padding: '0 8px',
                fontSize: '11px',
                background: activeTab === 'ir' ? 'var(--bg-surface-elevated)' : 'transparent',
                color: activeTab === 'ir' ? 'var(--text-primary)' : 'var(--text-muted)'
              }}
            >
              SSA Program
            </button>
            <button
              onClick={() => setActiveTab('phis')}
              className="btn"
              style={{
                height: '24px',
                padding: '0 8px',
                fontSize: '11px',
                background: activeTab === 'phis' ? 'var(--bg-surface-elevated)' : 'transparent',
                color: activeTab === 'phis' ? 'var(--text-primary)' : 'var(--text-muted)'
              }}
            >
              φ-Nodes ({ssa.phis.length})
            </button>
            <button
              onClick={() => setActiveTab('dom')}
              className="btn"
              style={{
                height: '24px',
                padding: '0 8px',
                fontSize: '11px',
                background: activeTab === 'dom' ? 'var(--bg-surface-elevated)' : 'transparent',
                color: activeTab === 'dom' ? 'var(--text-primary)' : 'var(--text-muted)'
              }}
            >
              Dominance Tree
            </button>
          </div>
        </div>

        <button 
          className="btn btn-secondary" 
          onClick={handleCopy}
          style={{ height: '28px', padding: '0 8px', fontSize: '11px' }}
        >
          {copied ? <Check size={12} style={{ color: 'var(--accent-lime)' }} /> : <Copy size={12} />}
          <span>{copied ? 'Copied' : 'Copy SSA IR'}</span>
        </button>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px', background: 'var(--bg-canvas)' }}>
        {activeTab === 'ir' && (
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '6px',
            padding: '16px',
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            lineHeight: 1.6,
            color: 'var(--text-primary)'
          }}>
            {ssa.cfg.blocks.map((block) => (
              <div key={block.id} style={{ marginBottom: '16px' }}>
                <div style={{ 
                  color: 'var(--accent-cyan)', 
                  fontWeight: 600, 
                  borderBottom: '1px solid var(--border-subtle)',
                  paddingBottom: '4px',
                  marginBottom: '6px'
                }}>
                  {block.name}{block.label ? ` (${block.label})` : ''}: 
                  <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: '11px', marginLeft: '8px' }}>
                    preds=[{block.preds.join(', ')}]  succs=[{block.succs.join(', ')}]
                  </span>
                </div>

                <div style={{ paddingLeft: '16px' }}>
                  {block.instrs.length === 0 ? (
                    <div style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>
                      (empty entry block)
                    </div>
                  ) : (
                    block.instrs.map((ins, i) => {
                      const isDef = selectedVarName && ins.defs && ins.defs.includes(selectedVarName);
                      const isUse = selectedVarName && ins.uses && ins.uses.includes(selectedVarName);
                      const hasDef = ins.defs && ins.defs.length > 0;

                      return (
                        <div 
                          key={i} 
                          onClick={() => {
                            if (hasDef) onSelectVar?.(ins.defs[0]);
                          }}
                          style={{ 
                            color: ins.is_phi ? 'var(--accent-purple-light)' : 'inherit',
                            padding: '2px 8px',
                            margin: '1px 0',
                            borderRadius: '4px',
                            background: isDef 
                              ? 'rgba(132, 204, 22, 0.16)' 
                              : (isUse ? 'rgba(6, 182, 212, 0.12)' : 'transparent'),
                            borderLeft: isDef 
                              ? '3px solid var(--accent-lime)' 
                              : (isUse ? '3px solid var(--accent-cyan)' : '3px solid transparent'),
                            cursor: hasDef ? 'pointer' : 'default',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            transition: 'background 80ms ease'
                          }}
                        >
                          <div>
                            {ins.is_phi && <span style={{ color: 'var(--accent-purple)', marginRight: '6px', fontWeight: 'bold' }}>φ</span>}
                            <span>{ins.text}</span>
                          </div>
                          {isDef && (
                            <span className="badge badge-lime" style={{ fontSize: '9px', padding: '1px 5px' }}>
                              def: {selectedVarName}
                            </span>
                          )}
                          {!isDef && isUse && (
                            <span className="badge badge-neutral" style={{ fontSize: '9px', padding: '1px 5px' }}>
                              uses: {selectedVarName}
                            </span>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'phis' && (
          <div>
            <div style={{ marginBottom: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
              In SSA form, φ-nodes select a variable version depending on which control-flow predecessor block executed at runtime.
            </div>

            {ssa.phis.length === 0 ? (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No φ-nodes present in this program (linear execution path).
              </div>
            ) : (
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px'
              }}>
                <thead>
                  <tr style={{
                    borderBottom: '1px solid var(--border-default)',
                    color: 'var(--text-muted)',
                    textAlign: 'left'
                  }}>
                    <th style={{ padding: '8px 10px', width: '120px' }}>Target SSA Var</th>
                    <th style={{ padding: '8px 10px', width: '100px' }}>Type</th>
                    <th style={{ padding: '8px 10px' }}>Predecessor Inflow Mappings</th>
                    <th style={{ padding: '8px 10px', width: '90px' }}>Location</th>
                  </tr>
                </thead>
                <tbody>
                  {ssa.phis.map((phi, i) => {
                    const isSelected = selectedVarName === phi.dest;
                    return (
                      <tr key={i} style={{ 
                        borderBottom: '1px solid var(--border-subtle)',
                        background: isSelected ? 'rgba(132, 204, 22, 0.1)' : 'transparent'
                      }}>
                        <td 
                          style={{ 
                            padding: '8px 10px', 
                            color: isSelected ? 'var(--accent-lime)' : 'var(--accent-purple-light)', 
                            fontWeight: 600,
                            cursor: 'pointer' 
                          }}
                          onClick={() => onSelectVar?.(phi.dest)}
                        >
                          {phi.dest}
                        </td>
                        <td style={{ padding: '8px 10px' }}>
                          <span className="badge badge-neutral">{phi.dest_type}</span>
                        </td>
                        <td style={{ padding: '8px 10px' }}>
                          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                            {Object.entries(phi.operands).map(([predBlock, ssaVal]) => (
                              <button 
                                key={predBlock}
                                onClick={() => onSelectVar?.(ssaVal)}
                                className="btn"
                                style={{
                                  background: 'var(--bg-surface-elevated)',
                                  border: '1px solid var(--border-default)',
                                  borderRadius: '4px',
                                  padding: '2px 8px',
                                  fontSize: '11px',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  cursor: 'pointer'
                                }}
                              >
                                <span style={{ color: 'var(--accent-cyan)' }}>{predBlock}:</span>
                                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{ssaVal}</span>
                              </button>
                            ))}
                          </div>
                        </td>
                        <td style={{ padding: '8px 10px', color: 'var(--text-dim)', fontSize: '11px' }}>
                          {phi.loc ? `@${phi.loc.line}:${phi.loc.col}` : '–'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'dom' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {/* Immediate Dominators */}
            <div style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-default)',
              borderRadius: '6px',
              padding: '14px',
            }}>
              <div style={{ fontWeight: 600, fontSize: '12px', color: 'var(--accent-cyan)', marginBottom: '10px' }}>
                Immediate Dominators (idom)
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {Object.entries(ssa.dom.idom).map(([block, idom]) => (
                  <div key={block} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '3px' }}>
                    <span style={{ color: 'var(--text-primary)' }}>{block}</span>
                    <span style={{ color: idom ? 'var(--accent-lime)' : 'var(--text-dim)' }}>
                      {idom ? `idom = ${idom}` : 'entry (none)'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Dominance Frontiers */}
            <div style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-default)',
              borderRadius: '6px',
              padding: '14px',
            }}>
              <div style={{ fontWeight: 600, fontSize: '12px', color: 'var(--accent-purple-light)', marginBottom: '10px' }}>
                Dominance Frontiers (DF)
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {Object.entries(ssa.dom.frontiers).map(([block, dfs]) => (
                  <div key={block} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '3px' }}>
                    <span style={{ color: 'var(--text-primary)' }}>DF({block})</span>
                    <span style={{ color: dfs.length > 0 ? 'var(--accent-purple-light)' : 'var(--text-dim)' }}>
                      {dfs.length > 0 ? `{ ${dfs.join(', ')} }` : '∅'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
