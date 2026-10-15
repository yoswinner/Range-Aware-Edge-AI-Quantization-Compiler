import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Network, Code, Layers } from 'lucide-react';
import { ASTNode } from '../../types';

interface ASTViewProps {
  ast: ASTNode;
}

const TreeNode: React.FC<{ node: ASTNode; name?: string; depth?: number }> = ({ 
  node, 
  name, 
  depth = 0 
}) => {
  const [isOpen, setIsOpen] = useState(depth < 3);

  // Extract children
  const children: { label: string; node: ASTNode }[] = [];
  if (node.statements) {
    node.statements.forEach((stmt, i) => children.push({ label: `stmt[${i}]`, node: stmt }));
  }
  if (node.init) {
    children.push({ label: 'init', node: node.init });
  }
  if (node.value && typeof node.value === 'object' && node.value.node_type) {
    children.push({ label: 'value', node: node.value });
  }
  if (node.cond) {
    children.push({ label: 'cond', node: node.cond });
  }
  if (node.then_block) {
    children.push({ label: 'then', node: node.then_block });
  }
  if (node.else_block) {
    children.push({ label: 'else', node: node.else_block });
  }
  if (node.body) {
    children.push({ label: 'body', node: node.body });
  }
  if (node.left) {
    children.push({ label: 'left', node: node.left });
  }
  if (node.right) {
    children.push({ label: 'right', node: node.right });
  }
  if (node.operand) {
    children.push({ label: 'operand', node: node.operand });
  }

  const hasChildren = children.length > 0;

  // Node details formatting
  let summary = '';
  if (node.node_type === 'Declaration') {
    summary = `${node.var_type} ${node.name}`;
  } else if (node.node_type === 'Assignment') {
    summary = `${node.name} = ...`;
  } else if (node.node_type === 'BinaryExpr') {
    summary = `op: '${node.op}'`;
  } else if (node.node_type === 'UnaryExpr') {
    summary = `op: '${node.op}'`;
  } else if (node.node_type === 'Identifier') {
    summary = `name: '${node.name}'`;
  } else if (node.node_type === 'IntLiteral') {
    summary = `val: ${node.value}`;
  } else if (node.node_type === 'FloatLiteral') {
    summary = `val: ${node.text || node.value}`;
  }

  return (
    <div style={{ marginLeft: depth > 0 ? '16px' : '0', marginTop: '3px' }}>
      <div 
        onClick={() => hasChildren && setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '3px 6px',
          borderRadius: '4px',
          cursor: hasChildren ? 'pointer' : 'default',
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          background: depth === 0 ? 'rgba(255,255,255,0.03)' : 'transparent',
          transition: 'background 80ms ease'
        }}
        onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--bg-surface-hover)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.background = depth === 0 ? 'rgba(255,255,255,0.03)' : 'transparent'; }}
      >
        {/* Toggle icon */}
        <span style={{ width: '14px', display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
          {hasChildren ? (
            isOpen ? <ChevronDown size={13} /> : <ChevronRight size={13} />
          ) : (
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--border-default)', marginLeft: '4px' }} />
          )}
        </span>

        {/* Child relationship label if present */}
        {name && (
          <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>
            {name}:
          </span>
        )}

        {/* Node Type Badge */}
        <span className="badge badge-purple" style={{ fontSize: '11px', padding: '1px 6px' }}>
          {node.node_type}
        </span>

        {/* Node Summary details */}
        {summary && (
          <span style={{ color: 'var(--text-primary)', fontWeight: 500, fontSize: '11px' }}>
            {summary}
          </span>
        )}

        {/* Node Type Annotation */}
        {node.ty && (
          <span className="badge badge-cyan" style={{ fontSize: '9px', padding: '0 4px' }}>
            :{node.ty}
          </span>
        )}

        {/* Source position */}
        {node.loc && (
          <span style={{ fontSize: '10px', color: 'var(--text-dim)', marginLeft: 'auto' }}>
            @{node.loc.line}:{node.loc.col}
          </span>
        )}
      </div>

      {/* Children */}
      {hasChildren && isOpen && (
        <div style={{
          borderLeft: '1px solid var(--border-default)',
          marginLeft: '7px',
          paddingLeft: '6px'
        }}>
          {children.map((child, i) => (
            <TreeNode key={i} node={child.node} name={child.label} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export const ASTView: React.FC<ASTViewProps> = ({ ast }) => {
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
          <Network size={14} style={{ color: 'var(--accent-purple-light)' }} />
          <span style={{ fontWeight: 600, fontSize: '12px', color: 'var(--text-primary)' }}>
            Abstract Syntax Tree (AST) Hierarchy
          </span>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          Click nodes to expand or collapse sub-trees
        </span>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '14px 18px' }}>
        <TreeNode node={ast} />
      </div>
    </div>
  );
};
