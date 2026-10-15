import React, { useState } from 'react';
import { Binary, Copy, Check, Info } from 'lucide-react';
import { TACInstr } from '../../types';

interface TACViewProps {
  tac: {
    instructions: TACInstr[];
    raw_text: string;
  };
}

export const TACView: React.FC<TACViewProps> = ({ tac }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(tac.raw_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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
          <Binary size={14} style={{ color: 'var(--accent-cyan)' }} />
          <span style={{ fontWeight: 600, fontSize: '12px', color: 'var(--text-primary)' }}>
            Three-Address Code (TAC) Instructions
          </span>
          <span className="badge badge-neutral" style={{ fontSize: '10px' }}>
            {tac.instructions.length} instructions
          </span>
        </div>

        <button 
          className="btn btn-secondary" 
          onClick={handleCopy}
          style={{ height: '28px', padding: '0 8px', fontSize: '11px' }}
        >
          {copied ? <Check size={12} style={{ color: 'var(--accent-lime)' }} /> : <Copy size={12} />}
          <span>{copied ? 'Copied' : 'Copy TAC'}</span>
        </button>
      </div>

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
              <th style={{ padding: '6px 10px', width: '45px' }}>PC</th>
              <th style={{ padding: '6px 10px' }}>Instruction</th>
              <th style={{ padding: '6px 10px', width: '90px' }}>Type</th>
              <th style={{ padding: '6px 10px', width: '100px' }}>Defs</th>
              <th style={{ padding: '6px 10px', width: '120px' }}>Uses</th>
              <th style={{ padding: '6px 10px', width: '80px' }}>Src Loc</th>
            </tr>
          </thead>
          <tbody>
            {tac.instructions.map((ins, idx) => {
              const isLabel = ins.op_type === 'Label';
              const isJump = ins.op_type === 'Jump' || ins.op_type === 'CondJump';

              return (
                <tr 
                  key={idx}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    background: isLabel ? 'rgba(255,255,255,0.02)' : 'transparent',
                    transition: 'background 80ms ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-surface-hover)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = isLabel ? 'rgba(255,255,255,0.02)' : 'transparent'}
                >
                  <td style={{ padding: '6px 10px', color: 'var(--text-dim)', fontSize: '11px' }}>
                    {idx.toString().padStart(2, '0')}
                  </td>
                  <td style={{ 
                    padding: '6px 10px', 
                    color: isLabel ? 'var(--accent-amber-light)' : (isJump ? 'var(--accent-purple-light)' : '#f8fafc'),
                    fontWeight: isLabel ? 600 : 400
                  }}>
                    <code>{ins.text}</code>
                  </td>
                  <td style={{ padding: '6px 10px' }}>
                    <span className="badge badge-neutral" style={{ fontSize: '10px' }}>
                      {ins.op_type}
                    </span>
                  </td>
                  <td style={{ padding: '6px 10px', color: 'var(--accent-lime)' }}>
                    {ins.defs.length > 0 ? ins.defs.join(', ') : '–'}
                  </td>
                  <td style={{ padding: '6px 10px', color: 'var(--accent-cyan)' }}>
                    {ins.uses.length > 0 ? ins.uses.join(', ') : '–'}
                  </td>
                  <td style={{ padding: '6px 10px', color: 'var(--text-dim)', fontSize: '11px' }}>
                    {ins.loc ? `${ins.loc.line}:${ins.loc.col}` : '–'}
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
