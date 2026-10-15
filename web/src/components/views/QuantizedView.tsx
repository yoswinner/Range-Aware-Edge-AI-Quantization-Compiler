import React, { useState } from 'react';
import { Cpu, Copy, Check, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';
import { QuantizationData, SSAData } from '../../types';

interface QuantizedViewProps {
  quantization: QuantizationData;
  ssa?: SSAData;
}

export const QuantizedView: React.FC<QuantizedViewProps> = ({ quantization, ssa }) => {
  const [copied, setCopied] = useState(false);
  const [showDiff, setShowDiff] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(quantization.raw_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{
        padding: '10px 16px',
        borderBottom: '1px solid var(--border-default)',
        background: 'var(--bg-surface-elevated)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Cpu size={15} style={{ color: 'var(--accent-lime)' }} />
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
            Quantized Intermediate Representation (INT8 Retyped)
          </span>
          <span className="badge badge-lime">
            {quantization.quantized_vars.length} variables rewritten
          </span>
          {Object.keys(quantization.blocked_vars).length > 0 && (
            <span className="badge badge-amber">
              {Object.keys(quantization.blocked_vars).length} blocked
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button 
            className="btn btn-secondary"
            onClick={() => setShowDiff(!showDiff)}
            style={{ height: '28px', padding: '0 8px', fontSize: '11px' }}
          >
            {showDiff ? 'Single View' : 'Side-by-Side Diff'}
          </button>

          <button 
            className="btn btn-secondary" 
            onClick={handleCopy}
            style={{ height: '28px', padding: '0 8px', fontSize: '11px' }}
          >
            {copied ? <Check size={12} style={{ color: 'var(--accent-lime)' }} /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy IR'}</span>
          </button>
        </div>
      </div>

      {/* Main View Area */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px', background: 'var(--bg-canvas)' }}>
        {showDiff ? (
          /* Side by side comparison */
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', height: '100%' }}>
            {/* Original SSA */}
            <div style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-default)',
              borderRadius: '6px',
              padding: '14px',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <div style={{ fontWeight: 600, fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px' }}>
                Original SSA IR (Pre-Quantization)
              </div>
              <pre style={{ 
                fontFamily: 'var(--font-mono)', 
                fontSize: '11.5px', 
                color: 'var(--text-primary)',
                overflow: 'auto',
                flex: 1,
                lineHeight: 1.6
              }}>
                {ssa?.raw_text || '// original SSA'}
              </pre>
            </div>

            {/* Quantized SSA */}
            <div style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--accent-lime-border)',
              borderRadius: '6px',
              padding: '14px',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <div style={{ fontWeight: 600, fontSize: '12px', color: 'var(--accent-lime)', marginBottom: '8px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px' }}>
                Transformed Quantized IR (INT8 Retyped)
              </div>
              <pre style={{ 
                fontFamily: 'var(--font-mono)', 
                fontSize: '11.5px', 
                color: 'var(--accent-lime-light)',
                overflow: 'auto',
                flex: 1,
                lineHeight: 1.6
              }}>
                {quantization.raw_text}
              </pre>
            </div>
          </div>
        ) : (
          /* Clean block breakdown */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Retyping Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
              <div style={{
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-default)',
                borderRadius: '6px',
                padding: '12px',
              }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>
                  Successfully Retyped to INT8:
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {quantization.quantized_vars.length === 0 ? (
                    <span style={{ color: 'var(--text-dim)', fontSize: '11px', fontStyle: 'italic' }}>None (all retained original type)</span>
                  ) : (
                    quantization.quantized_vars.map(v => (
                      <span key={v} className="badge badge-lime">
                        {v} : int8
                      </span>
                    ))
                  )}
                </div>
              </div>

              {Object.keys(quantization.blocked_vars).length > 0 && (
                <div style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--accent-amber-border)',
                  borderRadius: '6px',
                  padding: '12px',
                }}>
                  <div style={{ fontSize: '11px', color: 'var(--accent-amber)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>
                    Safe But Blocked by Operand Dependency:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '11px' }}>
                    {Object.entries(quantization.blocked_vars).map(([v, reason]) => (
                      <div key={v} style={{ color: 'var(--text-secondary)' }}>
                        <strong style={{ color: 'var(--accent-amber-light)', fontFamily: 'var(--font-mono)' }}>{v}</strong>: {reason}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Code Body */}
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
              {quantization.quantized_cfg ? (
                quantization.quantized_cfg.blocks.map(block => (
                  <div key={block.id} style={{ marginBottom: '14px' }}>
                    <div style={{ 
                      color: 'var(--accent-cyan)', 
                      fontWeight: 600, 
                      borderBottom: '1px solid var(--border-subtle)',
                      paddingBottom: '3px',
                      marginBottom: '5px'
                    }}>
                      {block.name}{block.label ? ` (${block.label})` : ''}:
                    </div>
                    <div style={{ paddingLeft: '16px' }}>
                      {block.instrs.map((ins, i) => {
                        const isRetyped = ins.text.includes(': int8');
                        return (
                          <div 
                            key={i}
                            style={{
                              color: isRetyped ? 'var(--accent-lime)' : 'var(--text-secondary)',
                              fontWeight: isRetyped ? 600 : 400
                            }}
                          >
                            {ins.text}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))
              ) : (
                <pre>{quantization.raw_text}</pre>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
