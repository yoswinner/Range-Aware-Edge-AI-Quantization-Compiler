import React from 'react';
import { ShieldCheck, AlertTriangle, XCircle, HelpCircle, CheckCircle2, AlertOctagon, Info, MousePointerClick } from 'lucide-react';
import { RangesData, QuantizationData } from '../../types';

interface SafetyViewProps {
  ranges: RangesData;
  quantization: QuantizationData;
  selectedVarName?: string | null;
  onSelectVar?: (name: string) => void;
}

export const SafetyView: React.FC<SafetyViewProps> = ({ 
  ranges, 
  quantization, 
  selectedVarName, 
  onSelectVar 
}) => {
  // Compute global bounds for scaling the number line
  // Standard range is [-128, 127], but let's expand if any value exceeds
  let minAxis = -150;
  let maxAxis = 150;

  ranges.values.forEach((v) => {
    if (v.lo !== null && v.lo < minAxis) minAxis = Math.floor(v.lo - 20);
    if (v.hi !== null && v.hi > maxAxis) maxAxis = Math.ceil(v.hi + 20);
  });

  const axisSpan = maxAxis - minAxis;
  const getPercent = (val: number) => {
    return Math.max(0, Math.min(100, ((val - minAxis) / axisSpan) * 100));
  };

  const int8MinPct = getPercent(-128);
  const int8MaxPct = getPercent(127);
  const zeroPct = getPercent(0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{
        padding: '12px 18px',
        borderBottom: '1px solid var(--border-default)',
        background: 'var(--bg-surface-elevated)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={16} style={{ color: 'var(--accent-lime)' }} />
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
            Signed INT8 Inclusive Range Verification: [-128, 127]
          </span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          Domain: [{minAxis}, {maxAxis}]
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        {/* Visual Benchmark Axis Bar */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-default)',
          borderRadius: '7px',
          padding: '16px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            <span>{minAxis}</span>
            <span style={{ color: 'var(--accent-lime)', fontWeight: 600 }}>Safe Signed INT8 Region: [-128, 127]</span>
            <span>{maxAxis}</span>
          </div>

          {/* Number line track */}
          <div style={{
            height: '28px',
            background: 'var(--bg-canvas)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '4px',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Safe Zone Highlight */}
            <div style={{
              position: 'absolute',
              left: `${int8MinPct}%`,
              width: `${int8MaxPct - int8MinPct}%`,
              top: 0,
              bottom: 0,
              background: 'rgba(132, 204, 22, 0.14)',
              borderLeft: '2px dashed var(--accent-lime)',
              borderRight: '2px dashed var(--accent-lime)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '10px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--accent-lime-light)',
              fontWeight: 600
            }}>
              INT8 SAFE ZONE
            </div>

            {/* Zero Marker */}
            <div style={{
              position: 'absolute',
              left: `${zeroPct}%`,
              top: 0,
              bottom: 0,
              width: '1px',
              background: 'var(--text-muted)',
              zIndex: 2
            }} />
          </div>

          <div style={{
            position: 'relative',
            height: '16px',
            marginTop: '4px',
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            color: 'var(--text-dim)'
          }}>
            <span style={{ position: 'absolute', left: `${int8MinPct}%`, transform: 'translateX(-50%)', color: 'var(--accent-lime)' }}>
              -128
            </span>
            <span style={{ position: 'absolute', left: `${zeroPct}%`, transform: 'translateX(-50%)' }}>
              0
            </span>
            <span style={{ position: 'absolute', left: `${int8MaxPct}%`, transform: 'translateX(-50%)', color: 'var(--accent-lime)' }}>
              +127
            </span>
          </div>
        </div>

        {/* Per-Variable Interval Comparison Bars */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-default)',
          borderRadius: '7px',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
            <div style={{ fontWeight: 600, fontSize: '12px', color: 'var(--text-primary)' }}>
              Inferred Interval vs. INT8 Boundary Comparison ({ranges.values.length} Variables Analyzed)
            </div>
            <div style={{ fontSize: '11px', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <MousePointerClick size={12} />
              <span>Click variable to open inspector &amp; traverse operands</span>
            </div>
          </div>

          {ranges.values.map((v) => {
            const isSafe = v.safety_status === 'SAFE';
            const isOverflow = v.hi !== null && (v.hi > 127 || (v.lo !== null && v.lo < -128));
            const isSelected = selectedVarName === v.name;

            let barLeft = 0;
            let barWidth = 0;
            let hasBar = false;

            if (v.lo !== null && v.hi !== null && !v.unreachable && !v.is_unknown) {
              hasBar = true;
              barLeft = getPercent(v.lo);
              const rightPct = getPercent(v.hi);
              barWidth = Math.max(1.2, rightPct - barLeft);
            }

            return (
              <div 
                key={v.name}
                role="button"
                tabIndex={0}
                aria-pressed={isSelected}
                aria-label={`Inspect SSA variable ${v.name}: ${v.instruction}`}
                onClick={() => onSelectVar?.(v.name)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectVar?.(v.name);
                  }
                }}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  background: isSelected 
                    ? 'rgba(132, 204, 22, 0.08)' 
                    : 'var(--bg-surface-elevated)',
                  border: isSelected 
                    ? '1.5px solid var(--accent-lime)' 
                    : '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                  transition: 'all 120ms ease',
                  boxShadow: isSelected ? '0 0 12px rgba(132, 204, 22, 0.22)' : 'none',
                  outline: 'none',
                  position: 'relative'
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.background = 'var(--bg-surface-hover)';
                    e.currentTarget.style.borderColor = 'var(--border-default)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.background = 'var(--bg-surface-elevated)';
                    e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  }
                }}
              >
                {/* Variable Info Row */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ 
                      fontWeight: 700, 
                      color: isSelected ? 'var(--accent-lime-light)' : 'var(--accent-cyan)',
                      fontSize: '12px'
                    }}>
                      {v.name}
                    </span>
                    <span style={{ color: 'var(--text-secondary)' }}><code>{v.instruction}</code></span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>
                      Range: <strong style={{ color: isSafe ? 'var(--accent-lime-light)' : (isOverflow ? 'var(--accent-red-light)' : 'var(--text-primary)') }}>
                        {v.range_str}
                      </strong>
                    </span>

                    {v.safety_status === 'SAFE' && (
                      <span className="badge badge-lime">SAFE → int8</span>
                    )}
                    {v.safety_status === 'REJECTED' && (
                      <span className="badge badge-red">REJECT</span>
                    )}
                    {v.safety_status === 'BLOCKED' && (
                      <span className="badge badge-amber">BLOCKED</span>
                    )}

                    {/* Interactive Inspect Badge */}
                    <span style={{
                      fontSize: '10px',
                      padding: '2px 7px',
                      borderRadius: '4px',
                      background: isSelected ? 'var(--accent-lime)' : 'var(--bg-surface)',
                      color: isSelected ? '#0b0f17' : 'var(--text-secondary)',
                      fontWeight: 600,
                      border: isSelected ? 'none' : '1px solid var(--border-default)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '3px'
                    }}>
                      {isSelected ? 'Inspecting' : 'Inspect'} ↗
                    </span>
                  </div>
                </div>

                {/* Range Bar Graphical Track */}
                <div style={{
                  height: '14px',
                  background: 'var(--bg-canvas)',
                  borderRadius: '3px',
                  position: 'relative',
                  overflow: 'hidden',
                  marginTop: '4px'
                }}>
                  {/* Safe region indicator */}
                  <div style={{
                    position: 'absolute',
                    left: `${int8MinPct}%`,
                    width: `${int8MaxPct - int8MinPct}%`,
                    top: 0,
                    bottom: 0,
                    background: 'rgba(255, 255, 255, 0.03)',
                    borderLeft: '1px solid rgba(132, 204, 22, 0.2)',
                    borderRight: '1px solid rgba(132, 204, 22, 0.2)',
                  }} />

                  {/* Zero tick */}
                  <div style={{
                    position: 'absolute',
                    left: `${zeroPct}%`,
                    top: 0,
                    bottom: 0,
                    width: '1px',
                    background: 'rgba(255, 255, 255, 0.1)',
                  }} />

                  {/* Render Variable Range Bar */}
                  {hasBar && (
                    <div style={{
                      position: 'absolute',
                      left: `${barLeft}%`,
                      width: `${barWidth}%`,
                      top: '2px',
                      bottom: '2px',
                      background: isSafe 
                        ? 'var(--accent-lime)' 
                        : (isOverflow ? 'var(--accent-red)' : (v.integral ? 'var(--accent-cyan)' : 'var(--accent-amber)')),
                      borderRadius: '2px',
                      boxShadow: isSafe 
                        ? '0 0 8px rgba(132, 204, 22, 0.4)' 
                        : (isOverflow ? '0 0 8px rgba(239, 68, 68, 0.4)' : 'none')
                    }} />
                  )}

                  {/* Unreachable state */}
                  {v.unreachable && (
                    <div style={{
                      position: 'absolute',
                      left: 0,
                      right: 0,
                      top: 0,
                      bottom: 0,
                      background: 'repeating-linear-gradient(45deg, #1c141d, #1c141d 8px, #261729 8px, #261729 16px)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '9px',
                      color: 'var(--accent-red-light)',
                      fontFamily: 'var(--font-mono)'
                    }}>
                      CONTROL FLOW UNREACHABLE (BOTTOM ⊥)
                    </div>
                  )}

                  {/* Unknown state */}
                  {v.is_unknown && !v.unreachable && (
                    <div style={{
                      position: 'absolute',
                      left: 0,
                      right: 0,
                      top: 0,
                      bottom: 0,
                      background: 'rgba(100, 116, 139, 0.15)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '9px',
                      color: 'var(--text-muted)',
                      fontFamily: 'var(--font-mono)',
                      border: '1px dashed var(--border-default)'
                    }}>
                      UNBOUNDED / UNKNOWN RANGE (-∞ to +∞)
                    </div>
                  )}
                </div>

                {/* Explanation line if rejected */}
                {v.rejection_reason && (
                  <div style={{ fontSize: '11px', color: 'var(--accent-red-light)', marginTop: '2px' }}>
                    Reason: {v.rejection_reason}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Educational Policy Box: Six Criteria for INT8 Safety */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-default)',
          borderRadius: '7px',
          padding: '14px 18px',
          fontSize: '12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-lime)', fontWeight: 600, marginBottom: '8px' }}>
            <Info size={15} />
            <span>Formal INT8 Quantization Safety Policy</span>
          </div>
          <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '10px' }}>
            In this compiler, an SSA variable is classified as <strong>SAFE</strong> for signed INT8 hardware rewriting if and only if <strong>all 6 conditions</strong> are mathematically proven by the abstract interpretation domain:
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px', fontSize: '11px' }}>
            <div style={{ padding: '8px 10px', background: 'var(--bg-surface-elevated)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
              <strong style={{ color: 'var(--accent-lime)' }}>1. Known Finite Interval:</strong> Abstract interval must be bounded (lo and hi are non-null). Unbounded values are rejected.
            </div>
            <div style={{ padding: '8px 10px', background: 'var(--bg-surface-elevated)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
              <strong style={{ color: 'var(--accent-lime)' }}>2. Lower Bound:</strong> Inferred minimum must satisfy lo &gt;= -128.
            </div>
            <div style={{ padding: '8px 10px', background: 'var(--bg-surface-elevated)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
              <strong style={{ color: 'var(--accent-lime)' }}>3. Upper Bound:</strong> Inferred maximum must satisfy hi &lt;= 127.
            </div>
            <div style={{ padding: '8px 10px', background: 'var(--bg-surface-elevated)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
              <strong style={{ color: 'var(--accent-lime)' }}>4. Integrality Proof:</strong> Value must be guaranteed integer (integral = true). Floating-point values are rejected.
            </div>
            <div style={{ padding: '8px 10px', background: 'var(--bg-surface-elevated)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
              <strong style={{ color: 'var(--accent-lime)' }}>5. Operation Support:</strong> Producing instruction must be an INT8-representable operation (+, -, *, copy, input, phi).
            </div>
            <div style={{ padding: '8px 10px', background: 'var(--bg-surface-elevated)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
              <strong style={{ color: 'var(--accent-lime)' }}>6. Operand Dependencies:</strong> All operands must also be INT8-safe. Unsafe intermediates block downstream retyping.
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

