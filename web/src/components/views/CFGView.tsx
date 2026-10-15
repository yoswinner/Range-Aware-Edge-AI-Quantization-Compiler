import React, { useState, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
  Node,
  Edge,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Network, Eye, AlertOctagon, CornerDownRight, X, Layers } from 'lucide-react';
import { CFGData, CFGBlock } from '../../types';

interface CFGViewProps {
  cfg: CFGData;
}

// Custom Basic Block Node for React Flow
const BasicBlockNode: React.FC<{ data: { block: CFGBlock; isSelected: boolean; onSelect: (b: CFGBlock) => void } }> = ({ data }) => {
  const { block, isSelected, onSelect } = data;

  return (
    <div 
      onClick={() => onSelect(block)}
      style={{
        width: '240px',
        background: block.is_unreachable 
          ? 'repeating-linear-gradient(45deg, #181119, #181119 10px, #1c141d 10px, #1c141d 20px)' 
          : 'var(--bg-surface-elevated)',
        border: '1.5px solid',
        borderColor: isSelected 
          ? 'var(--accent-lime)' 
          : (block.is_unreachable ? 'var(--accent-red-border)' : (block.is_entry ? 'var(--accent-cyan-border)' : 'var(--border-default)')),
        borderRadius: '7px',
        overflow: 'hidden',
        boxShadow: isSelected 
          ? '0 0 16px rgba(132, 204, 22, 0.25)' 
          : '0 4px 12px rgba(0, 0, 0, 0.35)',
        cursor: 'pointer',
        transition: 'all 120ms ease',
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: 'var(--border-highlight)', width: '8px', height: '8px' }} />

      {/* Block Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '6px 10px',
        background: block.is_unreachable ? 'rgba(239, 68, 68, 0.15)' : 'var(--bg-surface)',
        borderBottom: '1px solid var(--border-subtle)',
        fontSize: '11px',
        fontFamily: 'var(--font-mono)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ 
            fontWeight: 700, 
            color: block.is_entry ? 'var(--accent-cyan)' : 'var(--text-primary)',
            fontSize: '12px'
          }}>
            {block.name}
          </span>
          {block.label && (
            <span style={{ color: 'var(--accent-amber-light)' }}>
              ({block.label})
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {block.is_entry && (
            <span className="badge badge-cyan" style={{ fontSize: '9px', padding: '0 4px' }}>
              ENTRY
            </span>
          )}
          {block.is_unreachable && (
            <span className="badge badge-red" style={{ fontSize: '9px', padding: '0 4px' }}>
              UNREACHABLE
            </span>
          )}
        </div>
      </div>

      {/* Block Instructions Body */}
      <div style={{
        padding: '8px 10px',
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        lineHeight: 1.5,
        color: block.is_unreachable ? 'var(--text-muted)' : 'var(--text-secondary)',
        maxHeight: '180px',
        overflowY: 'auto'
      }}>
        {block.instrs.length === 0 ? (
          <span style={{ fontStyle: 'italic', color: 'var(--text-dim)' }}>
            (empty entry block)
          </span>
        ) : (
          block.instrs.map((ins, i) => (
            <div 
              key={i} 
              style={{ 
                whiteSpace: 'nowrap', 
                overflow: 'hidden', 
                textOverflow: 'ellipsis',
                color: ins.is_phi 
                  ? 'var(--accent-purple-light)' 
                  : (ins.op_type === 'CondJump' ? 'var(--accent-amber-light)' : 'inherit')
              }}
              title={ins.text}
            >
              {ins.is_phi && <span style={{ color: 'var(--accent-purple)', marginRight: '4px' }}>φ</span>}
              {ins.text}
            </div>
          ))
        )}
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: 'var(--border-highlight)', width: '8px', height: '8px' }} />
    </div>
  );
};

const nodeTypes = {
  basicBlock: BasicBlockNode,
};

export const CFGView: React.FC<CFGViewProps> = ({ cfg }) => {
  const [selectedBlock, setSelectedBlock] = useState<CFGBlock | null>(null);

  // Compute graph layout coordinates
  const { nodes, edges } = useMemo(() => {
    const blockMap = new Map<number, CFGBlock>();
    cfg.blocks.forEach(b => blockMap.set(b.id, b));

    // Simple layered layout: depth from entry block
    const depthMap = new Map<number, number>();
    const columnMap = new Map<number, number>();
    const levelCounts = new Map<number, number>();

    depthMap.set(cfg.entry, 0);
    const queue = [cfg.entry];
    const visited = new Set<number>([cfg.entry]);

    while (queue.length > 0) {
      const cur = queue.shift()!;
      const d = depthMap.get(cur) || 0;
      const b = blockMap.get(cur);
      if (!b) continue;

      for (const succId of b.succ_ids) {
        if (!visited.has(succId)) {
          visited.add(succId);
          depthMap.set(succId, d + 1);
          queue.push(succId);
        }
      }
    }

    // Place remaining unreached blocks at the bottom
    let maxDepth = 0;
    depthMap.forEach(d => { if (d > maxDepth) maxDepth = d; });
    cfg.blocks.forEach(b => {
      if (!depthMap.has(b.id)) {
        depthMap.set(b.id, maxDepth + 1);
      }
    });

    // Assign X columns based on level counts
    cfg.blocks.forEach(b => {
      const d = depthMap.get(b.id) || 0;
      const col = levelCounts.get(d) || 0;
      columnMap.set(b.id, col);
      levelCounts.set(d, col + 1);
    });

    const flowNodes: Node[] = cfg.blocks.map(b => {
      const depth = depthMap.get(b.id) || 0;
      const col = columnMap.get(b.id) || 0;
      const totalInLevel = levelCounts.get(depth) || 1;
      
      const x = 320 + (col - (totalInLevel - 1) / 2) * 300;
      const y = 40 + depth * 190;

      return {
        id: `B${b.id}`,
        type: 'basicBlock',
        position: { x, y },
        data: {
          block: b,
          isSelected: selectedBlock?.id === b.id,
          onSelect: (block: CFGBlock) => setSelectedBlock(block),
        },
      };
    });

    const flowEdges: Edge[] = cfg.edges.map((e, idx) => {
      let strokeColor = 'var(--text-muted)';
      let label: string = e.kind;

      if (e.kind === 'true') {
        strokeColor = 'var(--accent-lime)';
      } else if (e.kind === 'false') {
        strokeColor = 'var(--accent-red)';
      } else if (e.kind === 'jump') {
        strokeColor = 'var(--accent-cyan)';
      }

      if (e.is_back_edge) {
        strokeColor = 'var(--accent-amber)';
        label = `${e.kind} (back-edge)`;
      }

      return {
        id: `e-${e.src}-${e.dst}-${idx}`,
        source: `B${e.src}`,
        target: `B${e.dst}`,
        type: 'smoothstep',
        animated: e.is_back_edge,
        label,
        labelStyle: {
          fill: strokeColor,
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 10,
          fontWeight: 600,
        },
        labelBgStyle: {
          fill: '#0f121a',
          fillOpacity: 0.85,
        },
        style: {
          stroke: strokeColor,
          strokeWidth: e.is_back_edge ? 2.5 : 2,
          strokeDasharray: e.is_back_edge ? '5 5' : undefined,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
          width: 14,
          height: 14,
        },
      };
    });

    return { nodes: flowNodes, edges: flowEdges };
  }, [cfg, selectedBlock]);

  return (
    <div style={{ display: 'flex', height: '100%', position: 'relative', overflow: 'hidden' }}>
      {/* Canvas */}
      <div style={{ flex: 1, height: '100%', position: 'relative' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.2}
          maxZoom={2.5}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#1e2638" gap={20} size={1} />
          <Controls position="bottom-left" showInteractive={false} />
        </ReactFlow>

        {/* Legend Overlay */}
        <div style={{
          position: 'absolute',
          top: '12px',
          left: '12px',
          background: 'rgba(15, 18, 26, 0.88)',
          backdropFilter: 'blur(6px)',
          border: '1px solid var(--border-default)',
          borderRadius: '6px',
          padding: '8px 12px',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
          display: 'flex',
          flexDirection: 'column',
          gap: '5px',
          zIndex: 5
        }}>
          <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '2px' }}>
            CFG Edge Legend:
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '2px', background: 'var(--accent-lime)' }} />
            <span>true branch</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '2px', background: 'var(--accent-red)' }} />
            <span>false branch</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '2px', background: 'var(--accent-cyan)' }} />
            <span>jump</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '2px', background: 'var(--accent-amber)', borderTop: '2px dashed var(--accent-amber)' }} />
            <span>loop back-edge ↺</span>
          </div>
        </div>
      </div>

      {/* Block Inspector Sidebar */}
      {selectedBlock && (
        <div style={{
          width: '320px',
          height: '100%',
          background: 'var(--bg-surface-elevated)',
          borderLeft: '1px solid var(--border-default)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 10,
          boxShadow: '-4px 0 16px rgba(0,0,0,0.4)',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '12px 16px',
            borderBottom: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Network size={15} style={{ color: 'var(--accent-lime)' }} />
              <span style={{ fontWeight: 600, fontSize: '13px' }}>
                Block Inspector: {selectedBlock.name}
              </span>
            </div>
            <button 
              className="btn-icon" 
              onClick={() => setSelectedBlock(null)}
              style={{ padding: '4px' }}
            >
              <X size={14} />
            </button>
          </div>

          <div style={{ flex: 1, overflow: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {/* Block Metadata */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Status:</span>
                {selectedBlock.is_unreachable ? (
                  <span className="badge badge-red">Unreachable</span>
                ) : (
                  <span className="badge badge-lime">Reachable</span>
                )}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Predecessors:</span>
                <span className="mono" style={{ color: 'var(--accent-cyan-light)' }}>
                  {selectedBlock.preds.length > 0 ? selectedBlock.preds.join(', ') : 'none (entry)'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Successors:</span>
                <span className="mono" style={{ color: 'var(--accent-cyan-light)' }}>
                  {selectedBlock.succs.length > 0 ? selectedBlock.succs.join(', ') : 'none (exit)'}
                </span>
              </div>
            </div>

            {/* Instructions */}
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px', fontWeight: 600 }}>
                Instructions ({selectedBlock.instrs.length}):
              </div>
              <div style={{
                background: 'var(--bg-canvas)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '5px',
                padding: '8px',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}>
                {selectedBlock.instrs.length === 0 ? (
                  <span style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>No instructions</span>
                ) : (
                  selectedBlock.instrs.map((ins, i) => (
                    <div key={i} style={{ borderBottom: i < selectedBlock.instrs.length - 1 ? '1px solid rgba(255,255,255,0.03)' : 'none', paddingBottom: '3px' }}>
                      <div style={{ color: ins.is_phi ? 'var(--accent-purple-light)' : 'var(--text-primary)' }}>
                        {ins.text}
                      </div>
                      {ins.is_phi && ins.phi_operands && (
                        <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginLeft: '8px', marginTop: '2px' }}>
                          Incoming: {Object.entries(ins.phi_operands).map(([b, v]) => `${b} → ${v}`).join(' | ')}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
