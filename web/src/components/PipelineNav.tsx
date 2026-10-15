import React from 'react';
import { 
  FileText, 
  Binary, 
  Network, 
  GitCommit, 
  Layers, 
  ShieldCheck, 
  Cpu, 
  Activity, 
  Terminal, 
  CheckCircle2, 
  XCircle,
  HelpCircle,
  FileCode
} from 'lucide-react';
import { StageId, CompileResponse } from '../types';

interface PipelineNavProps {
  activeStage: StageId;
  onSelectStage: (stage: StageId) => void;
  result: CompileResponse | null;
  isCompiling: boolean;
}

interface StageConfig {
  id: StageId;
  label: string;
  icon: React.ReactNode;
  getBadge: (res: CompileResponse | null) => { text: string; type: 'lime' | 'cyan' | 'amber' | 'red' | 'neutral' | 'purple' } | null;
}

const STAGES: StageConfig[] = [
  {
    id: 'lexer',
    label: 'Lexer',
    icon: <FileCode size={13} />,
    getBadge: (res) => res?.tokens ? { text: `${res.tokens.length} tok`, type: 'neutral' } : null,
  },
  {
    id: 'ast',
    label: 'AST',
    icon: <Network size={13} />,
    getBadge: (res) => res?.ast ? { text: res.ast.node_type, type: 'cyan' } : null,
  },
  {
    id: 'tac',
    label: 'TAC',
    icon: <Binary size={13} />,
    getBadge: (res) => res?.tac ? { text: `${res.tac.instructions.length} ins`, type: 'neutral' } : null,
  },
  {
    id: 'cfg',
    label: 'CFG',
    icon: <Network size={13} />,
    getBadge: (res) => res?.cfg ? { text: `${res.cfg.blocks.length} blk`, type: 'cyan' } : null,
  },
  {
    id: 'ssa',
    label: 'SSA',
    icon: <GitCommit size={13} />,
    getBadge: (res) => res?.ssa ? { text: `${res.ssa.phis.length} φ`, type: 'purple' } : null,
  },
  {
    id: 'ranges',
    label: 'Range Analysis',
    icon: <Layers size={13} />,
    getBadge: (res) => res?.ranges ? { text: `${res.ranges.values.length} vals`, type: 'cyan' } : null,
  },
  {
    id: 'safety',
    label: 'INT8 Safety',
    icon: <ShieldCheck size={13} />,
    getBadge: (res) => res?.summary ? { text: `${res.summary.safe_count} safe`, type: 'lime' } : null,
  },
  {
    id: 'quantization',
    label: 'Quantization',
    icon: <Cpu size={13} />,
    getBadge: (res) => res?.summary ? { text: `${res.summary.quantized_count} int8`, type: 'lime' } : null,
  },
  {
    id: 'diagnostics',
    label: 'Diagnostics',
    icon: <Activity size={13} />,
    getBadge: (res) => res?.diagnostics ? { text: `${res.diagnostics.length}`, type: 'neutral' } : null,
  },
  {
    id: 'simulator',
    label: 'Simulator',
    icon: <Terminal size={13} />,
    getBadge: (res) => {
      if (!res?.simulation) return null;
      return res.simulation.is_equivalent
        ? { text: 'MATCH', type: 'lime' }
        : { text: 'MISMATCH', type: 'red' };
    },
  },
];

export const PipelineNav: React.FC<PipelineNavProps> = ({
  activeStage,
  onSelectStage,
  result,
  isCompiling,
}) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      background: 'var(--bg-canvas)',
      borderBottom: '1px solid var(--border-subtle)',
      padding: '0 12px',
      overflowX: 'auto',
      whiteSpace: 'nowrap',
      flexShrink: 0,
      height: '38px',
      gap: '4px'
    }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '6px', 
        marginRight: '8px', 
        fontSize: '11px', 
        color: 'var(--text-muted)',
        fontFamily: 'var(--font-mono)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em'
      }}>
        <span>Pipeline:</span>
      </div>

      {STAGES.map((stage, idx) => {
        const isActive = activeStage === stage.id;
        const badge = result ? stage.getBadge(result) : null;
        const hasError = result && !result.success && result.error?.stage.toLowerCase().includes(stage.id.toLowerCase());

        return (
          <React.Fragment key={stage.id}>
            <button
              onClick={() => onSelectStage(stage.id)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '4px',
                background: isActive 
                  ? 'var(--bg-surface-active)' 
                  : 'transparent',
                border: '1px solid',
                borderColor: isActive 
                  ? (hasError ? 'var(--accent-red)' : 'var(--border-highlight)') 
                  : 'transparent',
                color: isActive 
                  ? 'var(--text-primary)' 
                  : (result ? 'var(--text-secondary)' : 'var(--text-dim)'),
                fontSize: '11px',
                fontWeight: isActive ? 600 : 400,
                cursor: 'pointer',
                transition: 'all 120ms ease',
                position: 'relative'
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'var(--bg-surface-hover)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = result ? 'var(--text-secondary)' : 'var(--text-dim)';
                }
              }}
            >
              <span style={{ 
                color: isActive 
                  ? (hasError ? 'var(--accent-red)' : 'var(--accent-lime)') 
                  : 'inherit' 
              }}>
                {stage.icon}
              </span>
              <span>{stage.label}</span>
              
              {hasError && (
                <span style={{ color: 'var(--accent-red)', display: 'flex', alignItems: 'center' }}>
                  <XCircle size={11} />
                </span>
              )}

              {badge && !hasError && (
                <span className={`badge badge-${badge.type}`} style={{ fontSize: '9px', padding: '0 4px', height: '16px' }}>
                  {badge.text}
                </span>
              )}

              {isActive && (
                <div style={{
                  position: 'absolute',
                  bottom: '-5px',
                  left: '20%',
                  right: '20%',
                  height: '2px',
                  background: hasError ? 'var(--accent-red)' : 'var(--accent-lime)',
                  borderRadius: '1px'
                }} />
              )}
            </button>

            {idx < STAGES.length - 1 && (
              <span style={{ color: 'var(--border-default)', fontSize: '10px', userSelect: 'none' }}>
                →
              </span>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
