import React, { useRef } from 'react';
import Editor, { Monaco } from '@monaco-editor/react';
import { Code2, Sparkles, BookOpen } from 'lucide-react';
import { ExampleItem } from '../types';

interface EditorPanelProps {
  source: string;
  onChange: (val: string) => void;
  selectedExample: ExampleItem | null;
  onCompile: () => void;
}

export const EditorPanel: React.FC<EditorPanelProps> = ({
  source,
  onChange,
  selectedExample,
  onCompile,
}) => {
  const lineCount = source.split('\n').length;
  const charCount = source.length;

  const handleEditorWillMount = (monaco: Monaco) => {
    // Register custom .qc mini language syntax
    monaco.languages.register({ id: 'qc' });
    monaco.languages.setMonarchTokensProvider('qc', {
      keywords: ['int', 'float', 'if', 'else', 'while', 'print'],
      operators: ['=', '+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!='],
      symbols: /[=><!~?:&|+\-*\/\^%]+/,
      tokenizer: {
        root: [
          // identifiers and keywords
          [/[a-zA-Z_]\w*/, {
            cases: {
              '@keywords': 'keyword',
              '@default': 'identifier',
            },
          }],
          // whitespace
          { include: '@whitespace' },
          // delimiters and operators
          [/[{}()\[\]]/, '@brackets'],
          [/@symbols/, {
            cases: {
              '@operators': 'operator',
              '@default': '',
            },
          }],
          // numbers
          [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
          [/\d+/, 'number'],
          // punctuation
          [/;/, 'delimiter'],
        ],
        whitespace: [
          [/[ \t\r\n]+/, 'white'],
          [/\/\*/, 'comment', '@comment'],
          [/\/\/.*$/, 'comment'],
        ],
        comment: [
          [/[^\/*]+/, 'comment'],
          [/\*\//, 'comment', '@pop'],
          [/[\/*]/, 'comment'],
        ],
      },
    });

    // Custom dark technical theme
    monaco.editor.defineTheme('rangeLabDark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'keyword', foreground: '84cc16', fontStyle: 'bold' },
        { token: 'identifier', foreground: '38bdf8' },
        { token: 'number', foreground: 'f59e0b' },
        { token: 'number.float', foreground: 'fbbf24' },
        { token: 'operator', foreground: 'c084fc' },
        { token: 'delimiter', foreground: '94a3b8' },
        { token: 'comment', foreground: '475569', fontStyle: 'italic' },
      ],
      colors: {
        'editor.background': '#0f121a',
        'editor.foreground': '#f1f5f9',
        'editorLineNumber.foreground': '#334155',
        'editorLineNumber.activeForeground': '#84cc16',
        'editorCursor.foreground': '#84cc16',
        'editor.selectionBackground': '#1e293b',
        'editor.lineHighlightBackground': '#161c28',
      },
    });
  };

  const handleEditorDidMount = (editor: any, monaco: Monaco) => {
    // Add Ctrl+Enter or Cmd+Enter keyboard shortcut to trigger compilation
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onCompile();
    });
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--border-default)',
      position: 'relative',
    }}>
      {/* Editor Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '8px 14px',
        borderBottom: '1px solid var(--border-subtle)',
        background: 'var(--bg-surface-elevated)',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Code2 size={14} style={{ color: 'var(--accent-lime)' }} />
          <span style={{ 
            fontFamily: 'var(--font-mono)', 
            fontWeight: 600, 
            fontSize: '12px',
            color: 'var(--text-primary)' 
          }}>
            source.qc
          </span>
          <span className="badge badge-neutral" style={{ fontSize: '10px' }}>
            Custom QC Language
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '11px', color: 'var(--text-muted)' }}>
          <span>{lineCount} lines</span>
          <span>•</span>
          <span>{charCount} chars</span>
        </div>
      </div>

      {/* Example Context Callout if an example is selected */}
      {selectedExample && (
        <div style={{
          padding: '8px 12px',
          background: 'rgba(6, 182, 212, 0.06)',
          borderBottom: '1px solid rgba(6, 182, 212, 0.15)',
          fontSize: '11px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '8px',
          flexShrink: 0
        }}>
          <Sparkles size={13} style={{ color: 'var(--accent-cyan)', marginTop: '2px', flexShrink: 0 }} />
          <div>
            <div style={{ fontWeight: 600, color: 'var(--accent-cyan-light)', marginBottom: '2px' }}>
              {selectedExample.name}
            </div>
            <div style={{ color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {selectedExample.description}
            </div>
          </div>
        </div>
      )}

      {/* Editor Main Canvas */}
      <div style={{ flex: 1, minHeight: 0, position: 'relative' }}>
        <Editor
          height="100%"
          language="qc"
          theme="rangeLabDark"
          value={source}
          beforeMount={handleEditorWillMount}
          onMount={handleEditorDidMount}
          onChange={(val) => onChange(val || '')}
          options={{
            fontSize: 13,
            fontFamily: 'JetBrains Mono, Fira Code, monospace',
            lineNumbers: 'on',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            renderWhitespace: 'none',
            bracketPairColorization: { enabled: true },
            padding: { top: 10, bottom: 10 },
          }}
        />
      </div>

      {/* Status Bar / Shortcut hint */}
      <div style={{
        padding: '5px 12px',
        borderTop: '1px solid var(--border-subtle)',
        background: 'var(--bg-canvas)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '11px',
        color: 'var(--text-muted)',
        fontFamily: 'var(--font-mono)',
        flexShrink: 0
      }}>
        <span>Language: Mini Numerical (.qc)</span>
        <span>Run: <kbd style={{ background: 'var(--bg-surface-elevated)', padding: '1px 5px', borderRadius: '3px', border: '1px solid var(--border-default)' }}>Ctrl+Enter</kbd></span>
      </div>
    </div>
  );
};
