import React from 'react';
import { Activity, CheckCircle2, XCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { DiagnosticItem } from '../../types';

interface DiagnosticsViewProps {
  diagnostics: DiagnosticItem[];
}

export const DiagnosticsView: React.FC<DiagnosticsViewProps> = ({ diagnostics }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div style={{
        padding: '10px 16px',
        borderBottom: '1px solid var(--border-default)',
        background: 'var(--bg-surface-elevated)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={15} style={{ color: 'var(--accent-lime)' }} />
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
            Source-Level Compiler Diagnostics ({diagnostics.length} Entries)
          </span>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          Traceable records in program execution order
        </span>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '16px', background: 'var(--bg-canvas)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {diagnostics.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No diagnostic records available.
          </div>
        ) : (
          diagnostics.map((d, i) => {
            const isSafe = d.safety_verdict === 'SAFE';

            return (
              <div
                key={i}
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid',
                  borderColor: isSafe ? 'var(--border-default)' : 'var(--accent-red-border)',
                  borderRadius: '6px',
                  padding: '12px 16px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px'
                }}
              >
                {/* Header row: Location & Variable */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>
                      {d.line !== null ? `Line ${d.line}, Column ${d.col}` : 'Synthetic/Compiler Node'}
                    </span>
                    <span style={{ color: 'var(--text-dim)' }}>•</span>
                    <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>
                      Variable: {d.name} {d.is_temporary ? '(temporary)' : ''}
                    </span>
                  </div>

                  <span className={isSafe ? 'badge badge-lime' : 'badge badge-red'}>
                    {d.safety_verdict}
                  </span>
                </div>

                {/* Facts row */}
                <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', fontSize: '11px', color: 'var(--text-secondary)' }}>
                  <div>
                    Type: <strong style={{ color: 'var(--text-primary)' }}>{d.original_type}</strong>
                  </div>
                  <div>
                    Inferred range: <strong style={{ color: isSafe ? 'var(--accent-lime-light)' : 'var(--text-primary)' }}>{d.range_str}</strong>
                  </div>
                  <div>
                    Integral: <strong style={{ color: d.integral ? 'var(--accent-lime)' : 'var(--accent-amber)' }}>{d.integral ? 'YES' : 'NO'}</strong>
                  </div>
                </div>

                {/* Reasons */}
                <div style={{ fontSize: '11px', color: isSafe ? 'var(--text-muted)' : 'var(--accent-red-light)', marginTop: '2px' }}>
                  {d.reasons.map((r, ri) => (
                    <div key={ri}>Reason: {r}</div>
                  ))}
                </div>

                {/* Transformation */}
                <div style={{ 
                  fontSize: '11px', 
                  color: d.is_quantized ? 'var(--accent-lime)' : 'var(--text-dim)',
                  borderTop: '1px solid var(--border-subtle)',
                  paddingTop: '6px',
                  marginTop: '2px'
                }}>
                  Transformation: {d.transformation}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
