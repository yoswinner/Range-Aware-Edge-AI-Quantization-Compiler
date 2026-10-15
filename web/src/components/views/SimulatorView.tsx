import React from 'react';
import { Terminal, CheckCircle2, XCircle, AlertTriangle, ArrowRight, Play, Info } from 'lucide-react';
import { SimulationData } from '../../types';

interface SimulatorViewProps {
  simulation: SimulationData | null;
}

export const SimulatorView: React.FC<SimulatorViewProps> = ({ simulation }) => {
  if (!simulation) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
        No simulation data available. Compile the program to run in-process simulation.
      </div>
    );
  }

  const isMatch = simulation.is_equivalent;

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
          <Terminal size={15} style={{ color: 'var(--accent-lime)' }} />
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
            Program Execution Simulator (Original vs. INT8 Quantized)
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isMatch ? (
            <span className="badge badge-lime" style={{ fontSize: '12px', padding: '3px 8px' }}>
              <CheckCircle2 size={13} />
              <span>EQUIVALENT (100% Output Match)</span>
            </span>
          ) : (
            <span className="badge badge-red" style={{ fontSize: '12px', padding: '3px 8px' }}>
              <XCircle size={13} />
              <span>SEMANTIC DIVERGENCE (Mismatch)</span>
            </span>
          )}
        </div>
      </div>

      {/* Main Execution Output Panels */}
      <div style={{ flex: 1, overflow: 'auto', padding: '18px 20px', background: 'var(--bg-canvas)', display: 'flex', flexDirection: 'column', gap: '18px' }}>
        
        {/* Error notification if simulator failed */}
        {simulation.error && (
          <div style={{
            padding: '12px 16px',
            background: 'var(--accent-red-bg)',
            border: '1px solid var(--accent-red-border)',
            borderRadius: '6px',
            color: 'var(--accent-red-light)',
            fontSize: '12px',
            fontFamily: 'var(--font-mono)'
          }}>
            <strong>Simulator Runtime Error:</strong> {simulation.error}
          </div>
        )}

        {/* Side-by-Side Outputs */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          {/* Original Unquantized Output */}
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '6px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '6px' }}>
              <span style={{ fontWeight: 600, fontSize: '12px', color: 'var(--text-secondary)' }}>
                Original (Unquantized) Output
              </span>
              <span className="badge badge-neutral">Baseline 32-bit</span>
            </div>

            <div style={{
              background: 'var(--bg-canvas)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '5px',
              padding: '14px',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              color: 'var(--text-primary)',
              minHeight: '100px'
            }}>
              {simulation.original_output.length === 0 ? (
                <span style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>[No print outputs emitted]</span>
              ) : (
                simulation.original_output.map((val, idx) => (
                  <div key={idx} style={{ padding: '2px 0' }}>
                    <span style={{ color: 'var(--text-muted)', marginRight: '8px' }}>out[{idx}]:</span>
                    <strong style={{ color: 'var(--accent-cyan-light)' }}>{String(val)}</strong>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Quantized INT8 Output */}
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid',
            borderColor: isMatch ? 'var(--accent-lime-border)' : 'var(--accent-red-border)',
            borderRadius: '6px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '6px' }}>
              <span style={{ fontWeight: 600, fontSize: '12px', color: isMatch ? 'var(--accent-lime)' : 'var(--accent-red)' }}>
                Quantized (INT8) Output
              </span>
              <span className={isMatch ? 'badge badge-lime' : 'badge badge-red'}>
                Signed 8-bit Clamped
              </span>
            </div>

            <div style={{
              background: 'var(--bg-canvas)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '5px',
              padding: '14px',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              color: 'var(--text-primary)',
              minHeight: '100px'
            }}>
              {simulation.quantized_output.length === 0 ? (
                <span style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>[No print outputs emitted]</span>
              ) : (
                simulation.quantized_output.map((val, idx) => (
                  <div key={idx} style={{ padding: '2px 0' }}>
                    <span style={{ color: 'var(--text-muted)', marginRight: '8px' }}>out[{idx}]:</span>
                    <strong style={{ color: isMatch ? 'var(--accent-lime-light)' : 'var(--accent-red-light)' }}>
                      {String(val)}
                    </strong>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Verification Methodology Notice */}
        <div style={{
          padding: '14px 16px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '6px',
          fontSize: '11px',
          color: 'var(--text-muted)',
          display: 'flex',
          gap: '10px'
        }}>
          <Info size={15} style={{ color: 'var(--accent-cyan)', flexShrink: 0, marginTop: '2px' }} />
          <div style={{ lineHeight: 1.5 }}>
            <strong style={{ color: 'var(--text-secondary)' }}>Semantic Equivalence Verification Notice:</strong> The simulator directly executes the Python interpreter backend across unquantized and quantized SSA programs. Output equivalence confirms that INT8 transformations preserve numerical semantics for this tested execution trace. As standard in formal verification, empirical execution match does not constitute universal algebraic equivalence for unconstrained dynamic runtime spaces.
          </div>
        </div>

      </div>
    </div>
  );
};
