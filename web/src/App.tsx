import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { PipelineNav } from './components/PipelineNav';
import { EditorPanel } from './components/EditorPanel';
import { TokensView } from './components/views/TokensView';
import { ASTView } from './components/views/ASTView';
import { TACView } from './components/views/TACView';
import { CFGView } from './components/views/CFGView';
import { SSAView } from './components/views/SSAView';
import { RangesView } from './components/views/RangesView';
import { SafetyView } from './components/views/SafetyView';
import { QuantizedView } from './components/views/QuantizedView';
import { DiagnosticsView } from './components/views/DiagnosticsView';
import { SummaryView } from './components/views/SummaryView';
import { SimulatorView } from './components/views/SimulatorView';
import { SSAVarInspector } from './components/SSAVarInspector';
import { StageId, ExampleItem, CompileResponse } from './types';
import { AlertCircle, AlertOctagon, Terminal } from 'lucide-react';

const DEFAULT_SOURCE = `int x = 10;
int y = 20;
int z = x + y;
print z;
`;

export const App: React.FC = () => {
  const [source, setSource] = useState<string>(DEFAULT_SOURCE);
  const [compiledSource, setCompiledSource] = useState<string>('');
  const [examples, setExamples] = useState<ExampleItem[]>([]);
  const [selectedExampleId, setSelectedExampleId] = useState<string>('safe_arithmetic');
  const [activeStage, setActiveStage] = useState<StageId>('safety');
  const [selectedVarName, setSelectedVarName] = useState<string | null>(null);

  // Compiler settings
  const [widenAfter, setWidenAfter] = useState<number>(3);
  const [narrow, setNarrow] = useState<boolean>(false);
  const [pruneUnreachable, setPruneUnreachable] = useState<boolean>(false);

  // Status & Results
  const [isCompiling, setIsCompiling] = useState<boolean>(false);
  const [serverOnline, setServerOnline] = useState<boolean>(false);
  const [result, setResult] = useState<CompileResponse | null>(null);

  const isDirty = source !== compiledSource;

  // Compile Source Function
  const handleCompile = useCallback(async (customSource?: string, customNarrow?: boolean, customWiden?: number, customPrune?: boolean) => {
    const srcToCompile = customSource !== undefined ? customSource : source;
    const narrowVal = customNarrow !== undefined ? customNarrow : narrow;
    const widenVal = customWiden !== undefined ? customWiden : widenAfter;
    const pruneVal = customPrune !== undefined ? customPrune : pruneUnreachable;

    setIsCompiling(true);
    try {
      const response = await fetch('/api/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: srcToCompile,
          widen_after: widenVal,
          narrow: narrowVal,
          prune_unreachable: pruneVal,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data: CompileResponse = await response.json();
      setResult(data);
      setCompiledSource(srcToCompile);
      setServerOnline(true);

      // Stale selection clearing: if selected SSA variable no longer exists in new compilation, clear selection
      setSelectedVarName((prev) => {
        if (prev && (!data.ranges?.values || !data.ranges.values.some((v) => v.name === prev))) {
          return null;
        }
        return prev;
      });
    } catch (err: any) {
      setResult({
        success: false,
        error: {
          stage: 'Connection / Server',
          message: err.message || 'Failed to reach compiler backend API at /api/compile.',
        },
      });
      setSelectedVarName(null);
      setServerOnline(false);
    } finally {
      setIsCompiling(false);
    }
  }, [source, narrow, widenAfter, pruneUnreachable]);

  // Load Built-in Examples on initial mount
  useEffect(() => {
    const init = async () => {
      try {
        const healthRes = await fetch('/api/health');
        if (healthRes.ok) setServerOnline(true);

        const exRes = await fetch('/api/examples');
        if (exRes.ok) {
          const exData: ExampleItem[] = await exRes.json();
          setExamples(exData);
          if (exData.length > 0) {
            const first = exData[0];
            setSelectedExampleId(first.id);
            setSource(first.source);
            setNarrow(first.narrow || false);
            setWidenAfter(first.widen_after || 3);
            setPruneUnreachable(first.prune_unreachable || false);
            // Compile default example automatically
            handleCompile(first.source, first.narrow, first.widen_after, first.prune_unreachable);
          }
        }
      } catch (e) {
        // Fallback compilation attempt
        handleCompile(DEFAULT_SOURCE, false, 3, false);
      }
    };

    init();
  }, []);

  // Handle selecting an example
  const handleSelectExample = (id: string) => {
    const ex = examples.find(e => e.id === id);
    if (!ex) return;

    setSelectedExampleId(id);
    setSource(ex.source);
    const newNarrow = ex.narrow || false;
    const newWiden = ex.widen_after || 3;
    const newPrune = ex.prune_unreachable || false;

    setNarrow(newNarrow);
    setWidenAfter(newWiden);
    setPruneUnreachable(newPrune);

    // Auto-compile new example
    handleCompile(ex.source, newNarrow, newWiden, newPrune);
  };

  // Reset to current example source
  const handleReset = () => {
    const ex = examples.find(e => e.id === selectedExampleId);
    if (ex) {
      setSource(ex.source);
      setNarrow(ex.narrow || false);
      setWidenAfter(ex.widen_after || 3);
      setPruneUnreachable(ex.prune_unreachable || false);
      handleCompile(ex.source, ex.narrow, ex.widen_after, ex.prune_unreachable);
    } else {
      setSource(DEFAULT_SOURCE);
      handleCompile(DEFAULT_SOURCE, false, 3, false);
    }
  };

  const activeExampleObj = examples.find(e => e.id === selectedExampleId) || null;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      width: '100vw',
      height: '100vh',
      overflow: 'hidden',
      background: 'var(--bg-canvas)'
    }}>
      {/* Top Header */}
      <Header
        examples={examples}
        selectedExampleId={selectedExampleId}
        onSelectExample={handleSelectExample}
        onCompile={() => handleCompile()}
        onReset={handleReset}
        isCompiling={isCompiling}
        isDirty={isDirty}
        serverOnline={serverOnline}
        widenAfter={widenAfter}
        setWidenAfter={setWidenAfter}
        narrow={narrow}
        setNarrow={setNarrow}
        pruneUnreachable={pruneUnreachable}
        setPruneUnreachable={setPruneUnreachable}
      />

      {/* Navigable Pipeline Stage Bar */}
      <PipelineNav
        activeStage={activeStage}
        onSelectStage={setActiveStage}
        result={result}
        isCompiling={isCompiling}
      />

      {/* Main Workbench Body: 2-Column Desktop Grid */}
      <div style={{
        display: 'flex',
        flex: 1,
        minHeight: 0,
        overflow: 'hidden'
      }}>
        {/* Left Column: Source Editor (40% width) */}
        <div style={{
          width: '42%',
          minWidth: '360px',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative'
        }}>
          <EditorPanel
            source={source}
            onChange={setSource}
            selectedExample={activeExampleObj}
            onCompile={() => handleCompile()}
          />
        </div>

        {/* Right Column: Stage Inspector (58% width) */}
        <div style={{
          flex: 1,
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          background: 'var(--bg-canvas)',
          overflow: 'hidden',
          position: 'relative'
        }}>
          {/* Compilation Error Banner if compilation failed */}
          {result && !result.success && result.error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.12)',
              borderBottom: '1px solid var(--accent-red-border)',
              padding: '12px 18px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              flexShrink: 0
            }}>
              <AlertOctagon size={18} style={{ color: 'var(--accent-red)', marginTop: '2px', flexShrink: 0 }} />
              <div style={{ flex: 1, fontFamily: 'var(--font-mono)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="badge badge-red" style={{ fontSize: '10px' }}>
                    {result.error.stage} Error
                  </span>
                  {result.error.line && (
                    <span style={{ fontSize: '11px', color: 'var(--accent-red-light)' }}>
                      at line {result.error.line}, col {result.error.col}
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '12px', color: '#fca5a5' }}>
                  {result.error.message}
                </div>
                {result.error.details && (
                  <pre style={{ 
                    marginTop: '8px', 
                    fontSize: '10.5px', 
                    color: 'var(--text-muted)', 
                    maxHeight: '100px', 
                    overflowY: 'auto',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {result.error.details}
                  </pre>
                )}
              </div>
            </div>
          )}

          {/* Active View Dispatcher & Variable Inspector */}
          {(() => {
            const selectedVarObj = result?.ranges?.values?.find((v) => v.name === selectedVarName) || null;

            return (
              <div style={{ flex: 1, height: '100%', overflow: 'hidden', display: 'flex' }}>
                {/* Active View Area */}
                <div style={{ flex: 1, height: '100%', overflow: 'hidden', minWidth: 0, display: 'flex', flexDirection: 'column' }}>
                  {!result ? (
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      height: '100%',
                      color: 'var(--text-muted)',
                      gap: '12px',
                      padding: '24px',
                      textAlign: 'center'
                    }}>
                      <Terminal size={36} strokeWidth={1.5} style={{ color: 'var(--accent-lime)' }} />
                      <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        RANGE//LAB Compiler Workbench Ready
                      </div>
                      <div style={{ fontSize: '12px', maxWidth: '380px', lineHeight: 1.5 }}>
                        Click <strong>Compile</strong> or press <kbd style={{ background: 'var(--bg-surface)', padding: '2px 6px', borderRadius: '4px', border: '1px solid var(--border-default)' }}>Ctrl+Enter</kbd> to analyze ranges, verify INT8 safety, and simulate execution.
                      </div>
                    </div>
                  ) : (
                    <>
                      {activeStage === 'lexer' && result.tokens && (
                        <TokensView tokens={result.tokens} />
                      )}
                      {activeStage === 'ast' && result.ast && (
                        <ASTView ast={result.ast} />
                      )}
                      {activeStage === 'tac' && result.tac && (
                        <TACView tac={result.tac} />
                      )}
                      {activeStage === 'cfg' && result.cfg && (
                        <CFGView cfg={result.cfg} />
                      )}
                      {activeStage === 'ssa' && result.ssa && (
                        <SSAView 
                          ssa={result.ssa} 
                          selectedVarName={selectedVarName}
                          onSelectVar={setSelectedVarName}
                        />
                      )}
                      {activeStage === 'ranges' && result.ranges && (
                        <RangesView 
                          ranges={result.ranges} 
                          selectedVarName={selectedVarName}
                          onSelectVar={setSelectedVarName}
                        />
                      )}
                      {activeStage === 'safety' && result.ranges && result.quantization && (
                        <SafetyView 
                          ranges={result.ranges} 
                          quantization={result.quantization} 
                          selectedVarName={selectedVarName}
                          onSelectVar={setSelectedVarName}
                        />
                      )}
                      {activeStage === 'quantization' && result.quantization && (
                        <QuantizedView quantization={result.quantization} ssa={result.ssa} />
                      )}
                      {activeStage === 'diagnostics' && result.diagnostics && (
                        <DiagnosticsView diagnostics={result.diagnostics} />
                      )}
                      {activeStage === 'summary' && result.summary && (
                        <SummaryView summary={result.summary} />
                      )}
                      {activeStage === 'simulator' && (
                        <SimulatorView simulation={result.simulation || null} />
                      )}
                    </>
                  )}
                </div>

                {/* SSA Variable Inspector Side Drawer */}
                {selectedVarObj && (
                  <SSAVarInspector
                    selectedVar={selectedVarObj}
                    allVars={result?.ranges?.values || []}
                    onSelectVar={(varName) => setSelectedVarName(varName)}
                    onClose={() => setSelectedVarName(null)}
                  />
                )}
              </div>
            );
          })()}
        </div>
      </div>
    </div>
  );
};

export default App;
