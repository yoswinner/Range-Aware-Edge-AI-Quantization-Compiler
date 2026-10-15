import React, { useState } from 'react';
import { Search, Copy, Check } from 'lucide-react';
import { TokenItem } from '../../types';

interface TokensViewProps {
  tokens: TokenItem[];
}

export const TokensView: React.FC<TokensViewProps> = ({ tokens }) => {
  const [query, setQuery] = useState('');
  const [copied, setCopied] = useState(false);

  const filtered = tokens.filter(t => 
    t.kind.toLowerCase().includes(query.toLowerCase()) ||
    t.lexeme.toLowerCase().includes(query.toLowerCase())
  );

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(tokens, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* View Toolbar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 16px',
        borderBottom: '1px solid var(--border-default)',
        background: 'var(--bg-surface-elevated)',
        flexShrink: 0,
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, maxWidth: '320px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: '5px',
            padding: '4px 8px',
            width: '100%'
          }}>
            <Search size={13} style={{ color: 'var(--text-muted)' }} />
            <input 
              type="text"
              placeholder="Search token or lexeme..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'var(--text-primary)',
                fontSize: '12px',
                width: '100%',
                fontFamily: 'var(--font-sans)'
              }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Showing {filtered.length} of {tokens.length} tokens
          </span>
          <button 
            className="btn btn-secondary" 
            onClick={handleCopy}
            style={{ height: '28px', padding: '0 8px', fontSize: '11px' }}
          >
            {copied ? <Check size={12} style={{ color: 'var(--accent-lime)' }} /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy JSON'}</span>
          </button>
        </div>
      </div>

      {/* Table Container */}
      <div style={{ flex: 1, overflow: 'auto', padding: '12px 16px' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          textAlign: 'left'
        }}>
          <thead>
            <tr style={{
              borderBottom: '1px solid var(--border-default)',
              color: 'var(--text-muted)',
              fontSize: '11px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              <th style={{ padding: '8px 10px', width: '50px' }}>#</th>
              <th style={{ padding: '8px 10px', width: '120px' }}>Kind</th>
              <th style={{ padding: '8px 10px' }}>Lexeme</th>
              <th style={{ padding: '8px 10px', width: '100px' }}>Position</th>
              <th style={{ padding: '8px 10px', width: '140px' }}>Exact Value</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((t, idx) => (
              <tr 
                key={idx}
                style={{
                  borderBottom: '1px solid var(--border-subtle)',
                  transition: 'background 80ms ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-surface-hover)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <td style={{ padding: '7px 10px', color: 'var(--text-dim)' }}>{idx}</td>
                <td style={{ padding: '7px 10px' }}>
                  <span className="badge badge-cyan" style={{ fontSize: '10px' }}>
                    {t.kind}
                  </span>
                </td>
                <td style={{ padding: '7px 10px', color: '#f8fafc', fontWeight: 500 }}>
                  <code style={{ background: 'rgba(255,255,255,0.04)', padding: '2px 5px', borderRadius: '3px' }}>
                    {t.lexeme || '<empty>'}
                  </code>
                </td>
                <td style={{ padding: '7px 10px', color: 'var(--text-secondary)' }}>
                  {t.loc ? `${t.loc.line}:${t.loc.col}` : '–'}
                </td>
                <td style={{ padding: '7px 10px', color: t.value ? 'var(--accent-amber-light)' : 'var(--text-dim)' }}>
                  {t.value !== null ? t.value : '–'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
