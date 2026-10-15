import React, { useState } from 'react';
import { Layers, Search, CheckCircle2, XCircle, AlertTriangle, HelpCircle, ArrowRight } from 'lucide-react';
import { RangesData, RangeValue } from '../../types';

interface RangesViewProps {
  ranges: RangesData;
  selectedVarName?: string | null;
  onSelectVar?: (name: string) => void;
}

export const RangesView: React.FC<RangesViewProps> = ({ 
  ranges, 
  selectedVarName, 
  onSelectVar 
}) => {
  const [filter, setFilter] = useState<'all' | 'safe' | 'rejected' | 'quantized' | 'unknown' | 'unreachable'>('all');
  const [search, setSearch] = useState('');

  const filteredValues = ranges.values.filter((v: RangeValue) => {
    if (search && !v.name.toLowerCase().includes(search.toLowerCase()) && !v.instruction.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    if (filter === 'safe') return v.safety_status === 'SAFE';
    if (filter === 'rejected') return v.safety_status === 'REJECTED' || v.safety_status === 'BLOCKED';
    if (filter === 'quantized') return v.is_quantized;
    if (filter === 'unknown') return v.is_unknown;
    if (filter === 'unreachable') return v.unreachable;
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Toolbar & Filters */}
      <div style={{
        padding: '10px 16px',
        borderBottom: '1px solid var(--border-default)',
        background: 'var(--bg-surface-elevated)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0,
        gap: '12px',
        flexWrap: 'wrap'
      }}>
        {/* Filter Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {(['all', 'safe', 'rejected', 'quantized', 'unknown', 'unreachable'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className="btn"
              style={{
                height: '26px',
                padding: '0 9px',
                fontSize: '11px',
                textTransform: 'capitalize',
                background: filter === f ? 'var(--bg-surface-active)' : 'transparent',
                borderColor: filter === f ? 'var(--border-highlight)' : 'transparent',
                color: filter === f ? 'var(--text-primary)' : 'var(--text-muted)',
                fontWeight: filter === f ? 600 : 400
              }}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '5px',
            padding: '3px 8px',
            width: '180px'
          }}>
            <Search size={12} style={{ color: 'var(--text-muted)' }} />
            <input 
              type="text"
              placeholder="Filter SSA vars..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'var(--text-primary)',
                fontSize: '11px',
                width: '100%',
                fontFamily: 'var(--font-sans)'
              }}
            />
          </div>

          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            {ranges.sweeps} sweeps (converged={ranges.converged ? 'true' : 'false'})
          </div>
        </div>
      </div>

      {/* Ranges Table */}
      <div style={{ flex: 1, overflow: 'auto', padding: '14px 18px', background: 'var(--bg-canvas)' }}>
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
              fontSize: '11px',
              textAlign: 'left'
            }}>
              <th style={{ padding: '8px 10px', width: '90px' }}>SSA Variable</th>
              <th style={{ padding: '8px 10px', width: '130px' }}>Inferred Interval</th>
              <th style={{ padding: '8px 10px', width: '85px' }}>Integral</th>
              <th style={{ padding: '8px 10px', width: '80px' }}>Original Type</th>
              <th style={{ padding: '8px 10px', width: '95px' }}>INT8 Verdict</th>
              <th style={{ padding: '8px 10px', width: '90px' }}>Quantized</th>
              <th style={{ padding: '8px 10px' }}>Instruction & Reason</th>
              <th style={{ padding: '8px 10px', width: '60px' }}>Block</th>
            </tr>
          </thead>
          <tbody>
            {filteredValues.map((v, i) => {
              const isSafe = v.safety_status === 'SAFE';
              const isSelected = selectedVarName === v.name;

              return (
                <tr 
                  key={i}
                  role="button"
                  tabIndex={0}
                  aria-pressed={isSelected}
                  aria-label={`Inspect variable ${v.name}`}
                  onClick={() => onSelectVar?.(v.name)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelectVar?.(v.name);
                    }
                  }}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    transition: 'background 80ms ease',
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(132, 204, 22, 0.12)' : 'transparent',
                    borderLeft: isSelected ? '3px solid var(--accent-lime)' : '3px solid transparent'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) e.currentTarget.style.background = 'var(--bg-surface-hover)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) e.currentTarget.style.background = 'transparent';
                  }}
                >
                  {/* Variable Name */}
                  <td style={{ 
                    padding: '8px 10px', 
                    color: isSelected ? 'var(--accent-lime-light)' : 'var(--accent-cyan)', 
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <span>{v.name}</span>
                    {isSelected && (
                      <span style={{ fontSize: '9px', color: 'var(--accent-lime)' }}>●</span>
                    )}
                  </td>

                  {/* Interval */}
                  <td style={{ padding: '8px 10px' }}>
                    {v.unreachable ? (
                      <span className="badge badge-red" style={{ fontSize: '10px' }}>UNREACHABLE</span>
                    ) : v.is_unknown ? (
                      <span className="badge badge-amber" style={{ fontSize: '10px' }}>UNKNOWN</span>
                    ) : (
                      <span style={{ 
                        color: isSafe ? 'var(--accent-lime-light)' : 'var(--text-primary)',
                        fontWeight: 600 
                      }}>
                        [{v.lo_repr}, {v.hi_repr}]
                      </span>
                    )}

                    {v.widened && (
                      <span className="badge badge-amber" style={{ fontSize: '9px', marginLeft: '4px', padding: '0 3px' }}>
                        widened
                      </span>
                    )}
                    {v.narrowed && (
                      <span className="badge badge-lime" style={{ fontSize: '9px', marginLeft: '4px', padding: '0 3px' }}>
                        narrowed
                      </span>
                    )}
                  </td>

                  {/* Integrality */}
                  <td style={{ padding: '8px 10px' }}>
                    {v.integral ? (
                      <span style={{ color: 'var(--accent-lime)' }}>YES</span>
                    ) : (
                      <span style={{ color: 'var(--accent-amber)' }}>NO</span>
                    )}
                  </td>

                  {/* Original Type */}
                  <td style={{ padding: '8px 10px' }}>
                    <span className="badge badge-neutral">{v.original_type}</span>
                  </td>

                  {/* Safety Verdict */}
                  <td style={{ padding: '8px 10px' }}>
                    {v.safety_status === 'SAFE' && (
                      <span className="badge badge-lime">SAFE</span>
                    )}
                    {v.safety_status === 'REJECTED' && (
                      <span className="badge badge-red">REJECT</span>
                    )}
                    {v.safety_status === 'BLOCKED' && (
                      <span className="badge badge-amber">BLOCKED</span>
                    )}
                    {v.safety_status === 'UNKNOWN' && (
                      <span className="badge badge-neutral">UNKNOWN</span>
                    )}
                  </td>

                  {/* Quantized Status */}
                  <td style={{ padding: '8px 10px' }}>
                    {v.is_quantized ? (
                      <span className="badge badge-lime">
                        int8
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-dim)' }}>–</span>
                    )}
                  </td>

                  {/* Instruction & Decision Reason */}
                  <td style={{ padding: '8px 10px' }}>
                    <div style={{ color: 'var(--text-primary)', marginBottom: '2px' }}>
                      <code>{v.instruction}</code>
                    </div>
                    {v.rejection_reason && (
                      <div style={{ fontSize: '10px', color: 'var(--accent-red-light)', fontFamily: 'var(--font-sans)' }}>
                        {v.rejection_reason}
                      </div>
                    )}
                  </td>

                  {/* Block */}
                  <td style={{ padding: '8px 10px', color: 'var(--text-muted)', fontSize: '11px' }}>
                    {v.block_name || '–'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
