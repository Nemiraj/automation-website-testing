import React, { useEffect, useState } from 'react';
import { 
  Bot, 
  Sparkles, 
  Cpu, 
  Code, 
  Lightbulb, 
  Check, 
  Copy, 
  PlayCircle, 
  AlertTriangle,
  Layers,
  FileCheck,
  CheckCircle2,
  XCircle,
  Globe,
  Database,
  History,
  Clock,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { AIReadinessService, TestService } from '../services/api';

export const AIReadinessPage: React.FC = () => {
  // Standalone scan state
  const [targetUrl, setTargetUrl] = useState('');
  const [targetType, setTargetType] = useState<'live' | 'localhost'>('live');
  const [maxPages, setMaxPages] = useState<number>(3);
  const [scanning, setScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);

  // Active result state
  const [activeResult, setActiveResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Sub-view tabs for detailed AI readiness inspection
  const [activeView, setActiveView] = useState<'categories' | 'checklist' | 'schema' | 'entity' | 'fixes'>('categories');

  useEffect(() => {
    loadScanHistory();
  }, []);

  const loadScanHistory = async () => {
    try {
      setLoadingHistory(true);
      const standalone = await AIReadinessService.getHistory();
      
      if (standalone && standalone.length > 0) {
        setHistory(standalone);
        if (!activeResult) {
          setActiveResult(standalone[0]);
        }
      } else {
        // Fallback to past completed tests if standalone history is empty
        const testRuns = await TestService.list();
        const completed = testRuns.filter(t => t.status === 'completed' && t.ai_readiness_data);
        if (completed.length > 0) {
          const first = completed[0];
          const rep = {
            id: first.id,
            target_url: first.target_url,
            target_type: first.target_type,
            ai_readiness_score: first.ai_readiness_score || 85,
            ai_readiness_data: first.ai_readiness_data,
            pages_scanned: [],
            created_at: first.created_at
          };
          setActiveResult(rep);
          setHistory([rep]);
        }
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleRunScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl.trim()) return;

    setScanning(true);
    setScanError(null);

    try {
      const res = await AIReadinessService.scan({
        url: targetUrl.trim(),
        target_type: targetType,
        max_pages: maxPages
      });
      setActiveResult(res);
      setHistory(prev => [res, ...prev.filter(h => h.id !== res.id)]);
      setActiveView('categories');
    } catch (err: any) {
      console.error('Scan failed:', err);
      setScanError(err.response?.data?.detail || err.message || 'Failed to complete AI Readiness scan.');
    } finally {
      setScanning(false);
    }
  };

  const handleCopyCode = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const readinessData = activeResult?.ai_readiness_data;
  const readinessScore = activeResult?.ai_readiness_score || 85;

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header Banner */}
      <div className="rounded-3xl border border-teal-500/30 bg-gradient-to-r from-teal-500/10 via-slate-900/80 to-slate-950 p-6 sm:p-8 backdrop-blur-md shadow-xl space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500/20 text-teal-400 border border-teal-500/30">
                <Bot className="h-5 w-5" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-teal-400 font-mono bg-teal-500/10 px-2.5 py-0.5 rounded-full border border-teal-500/20">
                Standalone AI Readiness Scanner
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              AI Readiness & Machine Readability Engine
            </h1>
            <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
              Fast, focused scanner evaluating your website for Schema.org JSON-LD, semantic content outline, brand entity consistency, and autonomous AI agent discovery.
            </p>
          </div>

          {/* Overall AI Score Card */}
          {activeResult && (
            <div className="flex items-center gap-4 bg-slate-950/90 p-5 rounded-2xl border border-teal-500/30 shadow-lg flex-shrink-0">
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                  AI Readiness Score
                </span>
                <div className="flex items-baseline gap-1.5 mt-0.5">
                  <span className="text-4xl font-extrabold text-teal-400">
                    {Math.round(readinessScore)}
                  </span>
                  <span className="text-xs font-semibold text-slate-500">/ 100</span>
                </div>
              </div>
              <span className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase border ${
                activeResult.target_type === 'localhost' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : 'bg-teal-500/10 text-teal-400 border-teal-500/30'
              }`}>
                {readinessData?.environment_type || (activeResult.target_type === 'localhost' ? 'Localhost' : 'Live')}
              </span>
            </div>
          )}
        </div>

        {/* Dedicated Scan Form */}
        <form onSubmit={handleRunScan} className="pt-4 border-t border-slate-800 space-y-3">
          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* Target Type Switcher */}
            <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800 flex-shrink-0">
              <button
                type="button"
                onClick={() => { setTargetType('live'); if (targetUrl.includes('localhost')) setTargetUrl(''); }}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  targetType === 'live' ? 'bg-teal-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Live URL
              </button>
              <button
                type="button"
                onClick={() => { setTargetType('localhost'); if (!targetUrl) setTargetUrl('http://localhost/mywebsite/'); }}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  targetType === 'localhost' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Localhost / XAMPP
              </button>
            </div>

            {/* URL Input */}
            <input
              type="text"
              placeholder={targetType === 'localhost' ? "http://localhost/mywebsite/" : "https://example.com"}
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              className="flex-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:border-teal-500 focus:outline-none font-mono"
            />

            {/* Max Pages Selector */}
            <select
              value={maxPages}
              onChange={(e) => setMaxPages(Number(e.target.value))}
              className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-xs font-mono text-white focus:border-teal-500 focus:outline-none"
            >
              <option value={1}>1 Page Scan</option>
              <option value={3}>3 Pages Scan</option>
              <option value={5}>5 Pages Scan</option>
            </select>

            {/* Run Button */}
            <button
              type="submit"
              disabled={scanning || !targetUrl.trim()}
              className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-xl bg-teal-500 hover:bg-teal-400 px-6 py-2.5 text-xs font-bold text-slate-950 transition-all disabled:opacity-50 flex-shrink-0 shadow-lg shadow-teal-950/50"
            >
              {scanning ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Scanning DOM & Schemas...</span>
                </>
              ) : (
                <>
                  <PlayCircle className="h-4 w-4" />
                  <span>Run AI Readiness Scan</span>
                </>
              )}
            </button>
          </div>

          {scanError && (
            <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-rose-400 flex-shrink-0" />
              <span>{scanError}</span>
            </div>
          )}
        </form>
      </div>

      {/* Standalone Scan History Selector */}
      {history.length > 0 && (
        <div className="flex items-center justify-between flex-wrap gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <History className="h-4 w-4 text-teal-400" />
            <span className="font-semibold text-slate-400">Scan Report:</span>
            <select
              value={activeResult?.id || ''}
              onChange={(e) => {
                const found = history.find(h => h.id === e.target.value);
                if (found) setActiveResult(found);
              }}
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-mono text-white focus:border-teal-500 focus:outline-none"
            >
              {history.map(item => (
                <option key={item.id} value={item.id}>
                  {item.target_url} — Score: {Math.round(item.ai_readiness_score || 85)}/100 ({new Date(item.created_at).toLocaleTimeString()})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
            <span>Target: <strong className="text-white">{activeResult?.target_url}</strong></span>
          </div>
        </div>
      )}

      {/* Navigation Sub-Tabs for AI Readiness Details */}
      {activeResult && (
        <div className="flex items-center gap-2 border-b border-slate-800 overflow-x-auto pb-1">
          {[
            { id: 'categories', label: '10-Category Breakdown', icon: Layers },
            { id: 'checklist', label: 'Diagnostic Checklist & Evidence', icon: FileCheck },
            { id: 'schema', label: 'Schema.org (JSON-LD) Validator', icon: Code },
            { id: 'entity', label: 'Brand Entity Consistency', icon: Cpu },
            { id: 'fixes', label: 'Developer Fixes & Code Snippets', icon: Lightbulb },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeView === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id as any)}
                className={`px-4 py-2.5 text-xs font-bold rounded-t-xl transition-colors whitespace-nowrap flex items-center gap-2 ${
                  isActive
                    ? 'bg-slate-900 text-teal-400 border-t-2 border-teal-500'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Audit Detail Content */}
      {activeResult ? (
        <div className="space-y-6">
          {/* TAB 1: CATEGORIES BREAKDOWN */}
          {activeView === 'categories' && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
                10-Category Machine Readability Breakdown
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
                {readinessData?.category_scores && Object.entries(readinessData.category_scores).map(([catKey, catVal]: [string, any]) => {
                  const s = catVal.score || 85;
                  const scoreColor = s >= 85 ? 'text-emerald-400' : s >= 70 ? 'text-amber-400' : 'text-rose-400';
                  const barColor = s >= 85 ? 'bg-emerald-500' : s >= 70 ? 'bg-amber-500' : 'bg-rose-500';
                  return (
                    <div key={catKey} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3 shadow-md">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white">{catVal.name}</span>
                        <span className={`text-xs font-extrabold font-mono ${scoreColor}`}>
                          {Math.round(s)} / 100
                        </span>
                      </div>

                      <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden">
                        <div className={`h-full ${barColor} transition-all duration-500`} style={{ width: `${s}%` }} />
                      </div>

                      {catVal.findings && catVal.findings.length > 0 && (
                        <p className="text-[11px] text-slate-400 leading-snug">
                          {catVal.findings[0].message}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 2: COMPLETE CHECKLIST & EVIDENCE */}
          {activeView === 'checklist' && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
                Deterministic Findings & Check Results
              </h2>
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 divide-y divide-slate-800 overflow-hidden">
                {readinessData?.category_scores && Object.entries(readinessData.category_scores).map(([catKey, catVal]: [string, any]) => (
                  <div key={catKey} className="p-5 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-teal-400 uppercase tracking-wider">
                        {catVal.name}
                      </span>
                      <span className="text-xs font-mono font-semibold text-slate-400">
                        Weight: {Math.round((catVal.weight || 0.1) * 100)}%
                      </span>
                    </div>

                    <div className="space-y-2">
                      {catVal.findings && catVal.findings.length > 0 ? (
                        catVal.findings.map((finding: any, fIdx: number) => (
                          <div key={fIdx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs">
                            {finding.passed ? (
                              <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                            ) : (
                              <XCircle className="h-4 w-4 text-rose-400 flex-shrink-0 mt-0.5" />
                            )}
                            <div className="space-y-0.5 flex-1">
                              <div className="flex items-center justify-between">
                                <span className={`font-semibold ${finding.passed ? 'text-white' : 'text-rose-300'}`}>
                                  {finding.name}
                                </span>
                                <span className={`text-[10px] font-bold uppercase px-1.5 py-0.2 rounded ${
                                  finding.passed ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                                }`}>
                                  {finding.passed ? 'Passed' : 'Needs Fix'}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-400 leading-relaxed">
                                {finding.message}
                              </p>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="text-[11px] text-slate-500 italic">All checks passed standard threshold.</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: SCHEMA.ORG VALIDATOR */}
          {activeView === 'schema' && (
            <div className="space-y-6">
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Code className="h-4 w-4 text-emerald-400" /> Detected Schema.org Structured Data
                  </h3>
                  <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                    readinessData?.structured_data?.found ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {readinessData?.structured_data?.found ? 'Schemas Detected' : 'No Schema Found'}
                  </span>
                </div>

                {readinessData?.structured_data?.types_detected && readinessData.structured_data.types_detected.length > 0 ? (
                  <div className="space-y-2">
                    <span className="text-xs text-slate-400">Found Types:</span>
                    <div className="flex flex-wrap gap-2">
                      {readinessData.structured_data.types_detected.map((t: string, i: number) => (
                        <span key={i} className="text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/20 font-mono font-semibold">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 leading-relaxed">
                    No JSON-LD structured data blocks were found. Adding Organization or LocalBusiness markup allows search engines and autonomous AI agents to parse your products and services accurately.
                  </p>
                )}
              </div>

              {/* Ready to copy Organization Schema */}
              <div className="rounded-2xl border border-teal-500/30 bg-slate-900/60 p-6 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-300">
                    Recommended Organization Schema (JSON-LD)
                  </span>
                  <button
                    type="button"
                    onClick={() => handleCopyCode(`<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "${readinessData?.entity_consistency?.detected_names?.[0] || 'My Company'}",
  "url": "${activeResult?.target_url || 'https://example.com'}",
  "description": "Official company and service website."
}
</script>`, 'schema_gen')}
                    className="flex items-center gap-1 text-[11px] text-slate-300 hover:text-white bg-slate-800 px-2.5 py-1 rounded-lg"
                  >
                    {copiedId === 'schema_gen' ? <><Check className="h-3 w-3 text-emerald-400" /> Copied!</> : <><Copy className="h-3 w-3" /> Copy Schema</>}
                  </button>
                </div>
                <pre className="text-xs font-mono text-teal-300 bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-x-auto select-all">
{`<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "${readinessData?.entity_consistency?.detected_names?.[0] || 'My Company'}",
  "url": "${activeResult?.target_url || 'https://example.com'}",
  "description": "Official company and service website."
}
</script>`}
                </pre>
              </div>
            </div>
          )}

          {/* TAB 4: BRAND ENTITY CONSISTENCY */}
          {activeView === 'entity' && (
            <div className="space-y-6">
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-teal-400" /> Cross-Page Brand Name Resolution
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Compares how your business name and branding are presented across headers, footers, and page titles to identify ambiguous entity variations.
                </p>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <span className="text-xs font-semibold text-slate-400 block">Detected Brand Representations:</span>
                  <div className="flex flex-wrap gap-2">
                    {readinessData?.entity_consistency?.detected_names?.map((name: string, idx: number) => (
                      <span key={idx} className="text-xs text-white bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 font-mono font-semibold">
                        {name}
                      </span>
                    )) || <span className="text-xs text-slate-500 italic">No name variations detected</span>}
                  </div>
                </div>

                <div className="flex items-center justify-between bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs">
                  <span className="text-slate-400">Consistency Assessment:</span>
                  <span className="text-emerald-400 font-semibold">
                    {readinessData?.entity_consistency?.is_consistent ? '✓ Standardized Across Pages' : '⚠️ Variations Found'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: DEVELOPER FIXES & CODE SNIPPETS */}
          {activeView === 'fixes' && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-teal-400">
                Actionable AI Readiness Fixes & Code Improvements
              </h2>
              {readinessData?.top_improvements && readinessData.top_improvements.length > 0 ? (
                readinessData.top_improvements.map((rec: any, idx: number) => (
                  <div key={idx} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <span className="text-sm font-bold text-white flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-teal-400 flex-shrink-0" /> {rec.title}
                      </span>
                      <span className="text-[10px] uppercase font-bold text-teal-300 bg-teal-500/10 px-2.5 py-0.5 rounded-full border border-teal-500/20">
                        {rec.priority} Priority
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">{rec.evidence}</p>

                    <div className="text-xs text-slate-300 bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                      <strong className="text-slate-400 font-medium">Action:</strong> {rec.action}
                    </div>

                    {rec.code_fix && (
                      <div className="space-y-2 pt-1">
                        <div className="flex items-center justify-between text-xs text-slate-400">
                          <span className="font-semibold text-teal-300">Ready-to-Copy Snippet:</span>
                          <button
                            type="button"
                            onClick={() => handleCopyCode(rec.code_fix, `hub_rec_${idx}`)}
                            className="flex items-center gap-1 text-[11px] text-slate-300 hover:text-white bg-slate-800 px-2.5 py-1 rounded-lg"
                          >
                            {copiedId === `hub_rec_${idx}` ? <><Check className="h-3.5 w-3.5 text-emerald-400" /> Copied!</> : <><Copy className="h-3.5 w-3.5" /> Copy Code</>}
                          </button>
                        </div>
                        <pre className="text-xs font-mono text-teal-300 bg-slate-950 p-3.5 rounded-xl border border-slate-800 overflow-x-auto whitespace-pre-wrap select-all">
                          {rec.code_fix}
                        </pre>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-8 text-center text-xs text-slate-500">
                  No high-priority AI readiness improvements needed.
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-12 text-center space-y-3">
          <Bot className="h-10 w-10 text-slate-600 mx-auto" />
          <h3 className="text-sm font-bold text-white">No AI Readiness Audits Run Yet</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Enter a Live URL or Localhost project above to run an instant AI Readiness scan and generate the machine-readability breakdown.
          </p>
        </div>
      )}
    </div>
  );
};
