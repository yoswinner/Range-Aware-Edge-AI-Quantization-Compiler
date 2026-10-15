import React from 'react';
import { 
  Play, 
  RotateCcw, 
  Cpu, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle,
  Sliders,
  Settings2,
  FileCode2
} from 'lucide-react';
import { ExampleItem } from '../types';

interface HeaderProps {
  examples: ExampleItem[];
  selectedExampleId: string;
  onSelectExample: (id: string) => void;
  onCompile: () => void;
  onReset: () => void;
  isCompiling: boolean;
  isDirty: boolean;
  serverOnline: boolean;
  widenAfter: number;
  setWidenAfter: (v: number) => void;
  narrow: boolean;
  setNarrow: (v: boolean) => void;
  pruneUnreachable: boolean;
  setPruneUnreachable: (v: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({
  examples,
  selectedExampleId,
  onSelectExample,
  onCompile,
  onReset,
  isCompiling,
  isDirty,
  serverOnline,
  widenAfter,
  setWidenAfter,
  narrow,
  setNarrow,
  pruneUnreachable,
  setPruneUnreachable,
}) => {
  return (
    <header className="header" style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '10px 18px',
      background: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-default)',
      flexShrink: 0,
      gap: '16px',
      zIndex: 20
    }}>
      {/* Brand Identity */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '6px',
          background: 'linear-gradient(135deg, #84cc16 0%, #06b6d4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#090b10',
          boxShadow: '0 0 14px rgba(132, 204, 22, 0.25)'
        }}>
          <Cpu size={18} strokeWidth={2.5} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ 
              fontFamily: 'var(--font-mono)', 
              fontWeight: 700, 
              fontSize: '15px', 
              letterSpacing: '0.05em',
              color: '#f8fafc'
            }}>
              RANGE<span style={{ color: 'var(--accent-lime)' }}>//</span>LAB
            </span>
            <span className="badge badge-lime" style={{ fontSize: '10px', padding: '1px 5px' }}>
              INT8
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginLeft: '6px' }}>
              <span style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                background: serverOnline ? 'var(--accent-lime)' : 'var(--accent-red)',
                boxShadow: serverOnline ? '0 0 8px var(--accent-lime)' : 'none'
              }} />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                {serverOnline ? 'Compiler Engine Online' : 'Connecting...'}
              </span>
            </div>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.02em' }}>
            Range-Aware Edge AI Quantization Workbench
          </div>
        </div>
      </div>

      {/* Middle Controls: Example Selector + Analysis Options */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
        {/* Example Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <FileCode2 size={14} style={{ color: 'var(--accent-cyan)' }} />
          <select 
            className="select-input"
            value={selectedExampleId}
            onChange={(e) => onSelectExample(e.target.value)}
            style={{ width: '210px', height: '32px' }}
          >
            <option value="" disabled>Select Example (.qc)...</option>
            {examples.map((ex) => (
              <option key={ex.id} value={ex.id}>
                {ex.name} ({ex.category})
              </option>
            ))}
          </select>
        </div>

        {/* Divider */}
        <div style={{ width: '1px', height: '20px', background: 'var(--border-default)' }} />

        {/* Settings Group */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Widen threshold */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-secondary)' }} title="Number of sweeps before loop variable intervals widen to ±inf">
            <span style={{ fontFamily: 'var(--font-mono)' }}>widen_after:</span>
            <input 
              type="number"
              min={1}
              max={20}
              className="input-text"
              value={widenAfter}
              onChange={(e) => setWidenAfter(Math.max(1, parseInt(e.target.value) || 1))}
              style={{ width: '48px', height: '30px', padding: '2px 6px', textAlign: 'center', fontFamily: 'var(--font-mono)' }}
            />
          </div>

          {/* Narrowing Toggle */}
          <label className="switch-label" title="Enable iterative narrowing phase following loop widening convergence">
            <input 
              type="checkbox" 
              className="switch-input"
              checked={narrow}
              onChange={(e) => setNarrow(e.target.checked)}
            />
            <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>--narrow</span>
          </label>

          {/* Prune Unreachable Toggle */}
          <label className="switch-label" title="Prune blocks statically proven unreachable">
            <input 
              type="checkbox" 
              className="switch-input"
              checked={pruneUnreachable}
              onChange={(e) => setPruneUnreachable(e.target.checked)}
            />
            <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>--prune</span>
          </label>
        </div>
      </div>

      {/* Right Controls: Compile & Reset */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {isDirty && (
          <span className="badge badge-amber" style={{ fontSize: '10px' }}>
            Unsaved Changes
          </span>
        )}

        <button 
          className="btn btn-secondary" 
          onClick={onReset} 
          title="Reset to selected example source"
          style={{ height: '32px' }}
        >
          <RotateCcw size={13} />
          <span>Reset</span>
        </button>

        <button 
          className="btn btn-primary" 
          onClick={onCompile} 
          disabled={isCompiling}
          title="Compile and simulate (Ctrl + Enter)"
          style={{ height: '32px', minWidth: '105px' }}
        >
          {isCompiling ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{
                width: '12px',
                height: '12px',
                border: '2px solid rgba(0,0,0,0.2)',
                borderTopColor: '#000',
                borderRadius: '50%',
                animation: 'spin 0.6s linear infinite'
              }} />
              <span>Analyzing...</span>
            </div>
          ) : (
            <>
              <Play size={13} fill="currentColor" />
              <span>Compile</span>
            </>
          )}
        </button>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </header>
  );
};
