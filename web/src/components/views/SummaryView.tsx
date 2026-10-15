import React from 'react';
import { Layers, ShieldCheck, Cpu, HardDrive, CheckCircle2, XCircle, PieChart, Info } from 'lucide-react';
import { SummaryData } from '../../types';

interface SummaryViewProps {
  summary: SummaryData;
}

export const SummaryView: React.FC<SummaryViewProps> = ({ summary }) => {
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
          <PieChart size={15} style={{ color: 'var(--accent-lime)' }} />
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
            Compilation & Quantization Metrics Summary
          </span>
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '18px 20px', background: 'var(--bg-canvas)', display: 'flex', flexDirection: 'column', gap: '18px' }}>
        {/* Metric Cards Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '14px'
        }}>
          {/* Total SSA Values */}
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '6px',
            padding: '14px 16px',
          }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
              SSA Values Analyzed
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
              {summary.total_ssa_values}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
              Distinct SSA definitions
            </div>
          </div>

          {/* Quantized to INT8 */}
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '6px',
            padding: '14px 16px',
          }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
              Quantized to INT8
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--accent-lime)', fontFamily: 'var(--font-mono)' }}>
              {summary.quantized_count} <span style={{ fontSize: '13px', fontWeight: 400, color: 'var(--text-muted)' }}>({summary.quantized_percentage}%)</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
              Retyped from int/float to int8
            </div>
          </div>

          {/* Theoretical Storage Reduction */}
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '6px',
            padding: '14px 16px',
          }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
              Static Storage Reduction
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--accent-cyan-light)', fontFamily: 'var(--font-mono)' }}>
              {summary.theoretical_storage_reduction_pct}%
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
              Theoretical width (8-bit vs 32-bit words)
            </div>
          </div>

          {/* Simulator Equivalence */}
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '6px',
            padding: '14px 16px',
          }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
              Simulation Equivalence
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              {summary.simulation_equivalent === true && (
                <span className="badge badge-lime" style={{ fontSize: '13px', padding: '3px 8px' }}>
                  <CheckCircle2 size={13} /> 100% MATCH
                </span>
              )}
              {summary.simulation_equivalent === false && (
                <span className="badge badge-red" style={{ fontSize: '13px', padding: '3px 8px' }}>
                  <XCircle size={13} /> MISMATCH
                </span>
              )}
              {summary.simulation_equivalent === null && (
                <span className="badge badge-neutral" style={{ fontSize: '12px' }}>
                  N/A
                </span>
              )}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '6px' }}>
              Original vs. Quantized IR output
            </div>
          </div>
        </div>

        {/* Proportional Distribution Bar */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-default)',
          borderRadius: '6px',
          padding: '16px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '12px' }}>
            <span style={{ fontWeight: 600 }}>SSA Variable Safety Verdict Distribution</span>
            <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
              {summary.safe_count} Safe / {summary.blocked_count} Blocked / {summary.rejected_count} Rejected
            </span>
          </div>

          <div style={{
            height: '18px',
            borderRadius: '4px',
            background: 'var(--bg-canvas)',
            overflow: 'hidden',
            display: 'flex',
          }}>
            {summary.quantized_count > 0 && (
              <div 
                style={{ width: `${(summary.quantized_count / summary.total_ssa_values) * 100}%`, background: 'var(--accent-lime)' }}
                title={`Quantized: ${summary.quantized_count}`}
              />
            )}
            {summary.blocked_count > 0 && (
              <div 
                style={{ width: `${(summary.blocked_count / summary.total_ssa_values) * 100}%`, background: 'var(--accent-amber)' }}
                title={`Blocked: ${summary.blocked_count}`}
              />
            )}
            {summary.rejected_count > 0 && (
              <div 
                style={{ width: `${(summary.rejected_count / summary.total_ssa_values) * 100}%`, background: 'var(--accent-red)' }}
                title={`Rejected: ${summary.rejected_count}`}
              />
            )}
          </div>

          <div style={{ display: 'flex', gap: '16px', marginTop: '10px', fontSize: '11px', color: 'var(--text-secondary)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-lime)' }} />
              <span>Quantized to INT8 ({summary.quantized_count})</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-amber)' }} />
              <span>Blocked by Operands ({summary.blocked_count})</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-red)' }} />
              <span>Safety Rejected ({summary.rejected_count})</span>
            </div>
          </div>
        </div>

        {/* Rejection Category Breakdown */}
        {Object.keys(summary.rejections_by_kind).length > 0 && (
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '6px',
            padding: '16px',
          }}>
            <div style={{ fontWeight: 600, fontSize: '12px', marginBottom: '12px', color: 'var(--text-primary)' }}>
              Rejection Reasons Breakdown
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {Object.entries(summary.rejections_by_kind).map(([kind, count]) => (
                <div key={kind} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>
                  <span style={{ color: 'var(--accent-red-light)' }}>{kind}</span>
                  <span className="badge badge-red">{count} variables</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Hardware Clarification Notice */}
        <div style={{
          padding: '12px 14px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '6px',
          fontSize: '11px',
          color: 'var(--text-muted)',
          display: 'flex',
          gap: '8px'
        }}>
          <Info size={14} style={{ color: 'var(--text-secondary)', flexShrink: 0, marginTop: '1px' }} />
          <div>
            <strong>Evaluation Disclaimer:</strong> Theoretical storage-width reduction evaluates static data representation savings (8-bit vs. 32-bit words). It does not represent physical hardware cycle measurements, latency, or energy reduction without physical edge deployment benchmarks.
          </div>
        </div>

      </div>
    </div>
  );
};
