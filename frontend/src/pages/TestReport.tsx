import React, { useEffect, useState } from 'react';
import { useParams, Link, useSearchParams } from 'react-router-dom';
import { 
  ShieldCheck, 
  AlertOctagon, 
  AlertTriangle, 
  CheckCircle2, 
  Layers, 
  Smartphone, 
  FileText, 
  Eye, 
  Gauge, 
  Sparkles, 
  ExternalLink,
  Search,
  Filter,
  Download,
  Split,
  ChevronRight,
  Bot,
  Cpu,
  ListChecks,
  Zap,
  Code,
  HelpCircle,
  Check,
  Copy,
  ArrowRight,
  Lightbulb,
  Wrench
} from 'lucide-react';
import { ScoreGauge } from '../components/ScoreGauge';
import { SeverityBadge, CategoryBadge } from '../components/IssueBadge';
import { IssueDetailModal } from '../components/IssueDetailModal';
import { DiffViewer } from '../components/DiffViewer';
import { TestService } from '../services/api';
import { TestReport, IssueItem } from '../types';

export const TestReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabFromUrl = searchParams.get('tab') as any;
  const [report, setReport] = useState<TestReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTabState] = useState<'overview' | 'solutions' | 'ai_readiness' | 'issues' | 'pages' | 'responsive' | 'forms' | 'visual'>(tabFromUrl || 'overview');

  const setActiveTab = (tab: any) => {
    setActiveTabState(tab);
    setSearchParams({ tab });
  };

  useEffect(() => {
    if (tabFromUrl && tabFromUrl !== activeTab) {
      setActiveTabState(tabFromUrl);
    }
  }, [tabFromUrl]);
  
  // Issue filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [activeIssue, setActiveIssue] = useState<IssueItem | null>(null);
  const [copiedCodeId, setCopiedCodeId] = useState<string | null>(null);

  const handleCopyCode = (codeText: string, id: string) => {
    navigator.clipboard.writeText(codeText);
    setCopiedCodeId(id);
    setTimeout(() => setCopiedCodeId(null), 2000);
  };

  useEffect(() => {
    if (!id) return;
    TestService.getReport(id)
      .then((data) => setReport(data))
      .catch((err) => console.error('Failed to load test report:', err))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center space-y-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent mx-auto" />
          <p className="text-xs text-slate-400">Loading comprehensive test audit report...</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p>Report not found or failed to load.</p>
        <Link to="/" className="text-xs text-emerald-400 hover:underline mt-2 inline-block">Return to Dashboard</Link>
      </div>
    );
  }

  const { test_run, scores, issue_counts_by_severity, issues, pages, forms, screenshots, ai_analysis, previous_test_run } = report;

  // Filter issues
  const filteredIssues = issues.filter((iss) => {
    const matchesSearch = iss.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          iss.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          iss.page_url.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = selectedSeverity === 'all' || iss.severity.toLowerCase() === selectedSeverity.toLowerCase();
    const matchesCategory = selectedCategory === 'all' || iss.category.toLowerCase() === selectedCategory.toLowerCase();
    return matchesSearch && matchesSeverity && matchesCategory;
  });

  const visualRegressionIssues = issues.filter(i => i.category === 'visual_regression');

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Top Header Card */}
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 sm:p-8 backdrop-blur-md shadow-xl space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-md bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
                Audit Completed
              </span>
              <span className={`rounded-md px-2.5 py-0.5 text-xs font-bold uppercase border ${
                test_run.target_type === 'localhost'
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  : 'bg-teal-500/10 text-teal-400 border-teal-500/30'
              }`}>
                {test_run.target_type === 'localhost' ? 'Localhost Target' : 'Live Target'}
              </span>
              {test_run.environment?.environment && (
                <span className="rounded-md bg-slate-800 px-2.5 py-0.5 text-xs font-medium text-slate-300 border border-slate-700">
                  {test_run.environment.environment}
                </span>
              )}
              <span className="text-xs text-slate-400 font-mono">
                {new Date(test_run.created_at).toLocaleString()}
              </span>
            </div>
            
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2 font-mono truncate">
              {test_run.target_url}
              <a href={test_run.target_url} target="_blank" rel="noopener noreferrer" className="text-slate-500 hover:text-emerald-400">
                <ExternalLink className="h-4 w-4" />
              </a>
            </h1>

            {/* Detected Technology Environment Stack Bar */}
            {test_run.environment && (
              <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                {test_run.environment.server && test_run.environment.server !== 'Unknown' && (
                  <span className="rounded-lg bg-slate-950 px-2.5 py-1 text-slate-300 border border-slate-800 font-mono">
                    <strong className="text-slate-500 font-sans">Server:</strong> {test_run.environment.server}
                  </span>
                )}
                {test_run.environment.technology && test_run.environment.technology !== 'Unknown' && (
                  <span className="rounded-lg bg-slate-950 px-2.5 py-1 text-slate-300 border border-slate-800 font-mono">
                    <strong className="text-slate-500 font-sans">Backend:</strong> {test_run.environment.technology}
                  </span>
                )}
                {test_run.environment.database && test_run.environment.database !== 'Unknown' && (
                  <span className="rounded-lg bg-slate-950 px-2.5 py-1 text-slate-300 border border-slate-800 font-mono">
                    <strong className="text-slate-500 font-sans">Database:</strong> {test_run.environment.database}
                  </span>
                )}
                {test_run.environment.frontend_stack && test_run.environment.frontend_stack.length > 0 && (
                  <span className="rounded-lg bg-slate-950 px-2.5 py-1 text-slate-300 border border-slate-800 font-mono">
                    <strong className="text-slate-500 font-sans">Libraries:</strong> {test_run.environment.frontend_stack.join(', ')}
                  </span>
                )}
              </div>
            )}

            <p className="text-xs text-slate-400">
              Scanned {pages.length} pages across desktop, tablet, and mobile viewports • {issues.length} total findings
            </p>
          </div>

          {/* Health Score and Severity Counters */}
          <div className="flex items-center gap-6 self-start lg:self-auto bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
            <ScoreGauge score={scores.overall} size={110} strokeWidth={8} label="Overall Health" />

            <div className="grid grid-cols-2 gap-2 text-center pl-2 border-l border-slate-800">
              <div className="rounded-lg bg-rose-500/10 p-2 border border-rose-500/20">
                <span className="text-lg font-bold text-rose-400 leading-none block">{issue_counts_by_severity.critical}</span>
                <span className="text-[10px] font-semibold text-rose-300 uppercase">Critical</span>
              </div>
              <div className="rounded-lg bg-orange-500/10 p-2 border border-orange-500/20">
                <span className="text-lg font-bold text-orange-400 leading-none block">{issue_counts_by_severity.high}</span>
                <span className="text-[10px] font-semibold text-orange-300 uppercase">High</span>
              </div>
              <div className="rounded-lg bg-amber-500/10 p-2 border border-amber-500/20">
                <span className="text-lg font-bold text-amber-400 leading-none block">{issue_counts_by_severity.medium}</span>
                <span className="text-[10px] font-semibold text-amber-300 uppercase">Medium</span>
              </div>
              <div className="rounded-lg bg-blue-500/10 p-2 border border-blue-500/20">
                <span className="text-lg font-bold text-blue-400 leading-none block">{issue_counts_by_severity.low}</span>
                <span className="text-[10px] font-semibold text-blue-300 uppercase">Low</span>
              </div>
            </div>
          </div>
        </div>

        {/* Category Subscores Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 pt-2 border-t border-slate-800">
          {[
            { label: 'UI & Layout', score: scores.ui, icon: Layers },
            { label: 'Responsive', score: scores.responsive, icon: Smartphone },
            { label: 'Functional', score: scores.functional, icon: CheckCircle2 },
            { label: 'Forms', score: scores.forms, icon: FileText },
            { label: 'Accessibility', score: scores.accessibility, icon: Eye },
            { label: 'Performance', score: scores.performance, icon: Gauge },
            { label: 'AI Readiness', score: test_run.ai_readiness_score !== null && test_run.ai_readiness_score !== undefined ? test_run.ai_readiness_score : 85, icon: Bot },
          ].map((cat) => {
            const Icon = cat.icon;
            const scoreColor = cat.score >= 85 ? 'text-emerald-400' : cat.score >= 70 ? 'text-amber-400' : 'text-rose-400';
            return (
              <div key={cat.label} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 space-y-1">
                <div className="flex items-center justify-between text-slate-400 text-xs">
                  <span className="font-medium truncate">{cat.label}</span>
                  <Icon className="h-3.5 w-3.5 text-slate-500 flex-shrink-0" />
                </div>
                <div className="flex items-baseline gap-1">
                  <span className={`text-lg font-extrabold ${scoreColor}`}>{Math.round(cat.score)}</span>
                  <span className="text-[10px] text-slate-400 font-semibold">/100</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 overflow-x-auto pb-1">
        {[
          { id: 'overview', label: 'Overview' },
          { id: 'solutions', label: `Action Plan (${test_run.solution_plan?.solutions?.length || 0})` },
          { id: 'ai_readiness', label: `AI Readiness (${Math.round(test_run.ai_readiness_score || 85)}/100)` },
          { id: 'issues', label: `Issues (${issues.length})` },
          { id: 'pages', label: `Pages (${pages.length})` },
          { id: 'responsive', label: `Screenshots (${screenshots.length})` },
          { id: 'forms', label: `Forms (${forms.length})` },
          { id: 'visual', label: `Visual Diff (${visualRegressionIssues.length})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2.5 text-xs font-bold rounded-t-xl transition-colors whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === tab.id
                ? 'bg-slate-900 text-emerald-400 border-t-2 border-emerald-500'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            {tab.id === 'solutions' && <Zap className="h-3.5 w-3.5 text-amber-400" />}
            {tab.id === 'ai_readiness' && <Bot className="h-3.5 w-3.5 text-teal-400" />}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {/* 1. OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* AI Executive Diagnosis */}
          {ai_analysis && (
            <div className="rounded-2xl border border-emerald-500/30 bg-gradient-to-b from-emerald-500/10 via-slate-900/80 to-slate-950 p-6 space-y-4 shadow-lg">
              <div className="flex items-center gap-2 text-emerald-400">
                <Sparkles className="h-5 w-5" />
                <h2 className="text-base font-bold">AI Executive Synthesis & Priorities</h2>
              </div>
              <p className="text-sm text-slate-200 leading-relaxed">
                {ai_analysis.summary}
              </p>

              {/* Priority Action Checklist */}
              {ai_analysis.priority_actions && ai_analysis.priority_actions.length > 0 && (
                <div className="space-y-2 pt-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                    Recommended Priority Fixes
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                    {ai_analysis.priority_actions.map((act, idx) => (
                      <div key={idx} className="flex items-start gap-2.5 rounded-xl border border-slate-800 bg-slate-950/80 p-3 text-xs text-slate-200">
                        <span className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 text-slate-950 font-bold text-[10px] flex-shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span className="leading-snug">{act}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Top Critical Issues List */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
            <h2 className="text-sm font-bold text-white">Top High-Priority Issues</h2>
            <div className="divide-y divide-slate-800">
              {issues.slice(0, 5).map((iss) => (
                <div
                  key={iss.id}
                  onClick={() => setActiveIssue(iss)}
                  className="py-3.5 flex items-center justify-between gap-4 cursor-pointer hover:bg-slate-900/80 px-3 rounded-lg transition-colors"
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <SeverityBadge severity={iss.severity} />
                      <CategoryBadge category={iss.category} />
                      <span className="text-xs font-bold text-white truncate">{iss.title}</span>
                    </div>
                    <p className="text-xs text-slate-400 truncate">{iss.description}</p>
                  </div>
                  <ChevronRight className="h-4 w-4 text-slate-500 flex-shrink-0" />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 2. REPORT-BASED SOLUTION ENGINE & ACTION PLAN */}
      {activeTab === 'solutions' && (
        <div className="space-y-6">
          {/* Action Plan Header Card */}
          <div className="rounded-2xl border border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-slate-900/80 to-slate-950 p-6 space-y-3">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-2.5 text-amber-400">
                <Zap className="h-6 w-6" />
                <h2 className="text-lg font-bold text-white">Prioritized Developer Solution Plan</h2>
              </div>
              <span className="text-xs bg-amber-500/20 text-amber-300 font-mono px-3 py-1 rounded-full border border-amber-500/30">
                Dependency-Aware Root Cause Engine
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Solutions are ranked by root-cause dependencies so you resolve foundational server/database faults before addressing downstream form and conversion workflows.
            </p>
          </div>

          {/* Solutions List */}
          {test_run.solution_plan?.solutions && test_run.solution_plan.solutions.length > 0 ? (
            <div className="space-y-4">
              {test_run.solution_plan.solutions.map((sol: any, idx: number) => (
                <div key={sol.id || idx} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
                  {/* Top Bar */}
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-amber-500 text-slate-950 font-bold text-xs">
                        {idx + 1}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        sol.priority === 'critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                        sol.priority === 'high' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                        'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}>
                        {sol.priority} Priority
                      </span>
                      <span className="text-xs font-semibold text-slate-400 bg-slate-800 px-2.5 py-0.5 rounded">
                        {sol.category}
                      </span>
                    </div>
                    <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      Confidence: {sol.root_cause_confidence}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white">{sol.title}</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">{sol.problem}</p>

                  {/* Dependency Warning */}
                  {sol.fix_first_dependency && (
                    <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-300 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 flex-shrink-0 text-amber-400" />
                      <span><strong>Dependency Note:</strong> {sol.fix_first_dependency}</span>
                    </div>
                  )}

                  {/* Root Cause & Recommended Action Steps */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                    <div className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 space-y-1.5">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        Root Cause Diagnosis
                      </span>
                      <p className="text-xs text-slate-200 leading-relaxed">{sol.root_cause}</p>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 space-y-1.5">
                      <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block">
                        Action Steps
                      </span>
                      <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                        {Array.isArray(sol.recommended_solution) ? (
                          sol.recommended_solution.map((step: string, sIdx: number) => (
                            <li key={sIdx}>{step}</li>
                          ))
                        ) : (
                          <li>{sol.recommended_solution}</li>
                        )}
                      </ul>
                    </div>
                  </div>

                  {/* Implementation Code Diff / Snippet */}
                  {sol.implementation_guidance && (
                    <div className="space-y-1.5 pt-1">
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span className="font-semibold text-emerald-300 flex items-center gap-1.5">
                          <Code className="h-3.5 w-3.5" /> Implementation Code / Fix:
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyCode(sol.implementation_guidance, sol.id || String(idx))}
                          className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white bg-slate-800 px-2 py-1 rounded"
                        >
                          {copiedCodeId === (sol.id || String(idx)) ? (
                            <>
                              <Check className="h-3 w-3 text-emerald-400" /> Copied!
                            </>
                          ) : (
                            <>
                              <Copy className="h-3 w-3" /> Copy Code
                            </>
                          )}
                        </button>
                      </div>
                      <pre className="text-xs font-mono text-emerald-300 bg-slate-950 p-3 rounded-xl border border-slate-800 overflow-x-auto whitespace-pre-wrap select-all">
                        {sol.implementation_guidance}
                      </pre>
                    </div>
                  )}

                  {/* Expected Benefit & Verification Method */}
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2 border-t border-slate-800/80 text-xs text-slate-400">
                    <span className="text-slate-300">
                      <strong className="text-slate-500 font-medium">Expected Benefit:</strong> {sol.expected_benefit}
                    </span>
                    <span className="text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 text-[11px]">
                      ✓ {sol.verification_method}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center text-xs text-slate-500 rounded-2xl border border-slate-800 bg-slate-900/40">
              No critical action items detected. All core functional workflows and server components are operating normally.
            </div>
          )}
        </div>
      )}

      {/* 3. AI READINESS CHECKER */}
      {activeTab === 'ai_readiness' && (
        <div className="space-y-6">
          {/* AI Readiness Header Card */}
          <div className="rounded-3xl border border-teal-500/30 bg-gradient-to-r from-teal-500/10 via-slate-900/80 to-slate-950 p-6 sm:p-8 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Bot className="h-6 w-6 text-teal-400" />
                  <h2 className="text-xl font-extrabold text-white">AI Readiness Audit</h2>
                  <span className="text-xs bg-teal-500/20 text-teal-300 font-mono px-2.5 py-0.5 rounded-full border border-teal-500/30">
                    {test_run.ai_readiness_data?.environment_type || (test_run.target_type === 'localhost' ? 'LOCAL DEVELOPMENT' : 'LIVE WEBSITE')}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Deterministic assessment of machine readability, structured schema, semantic outline, and agent accessibility.
                </p>
              </div>

              <div className="flex items-baseline gap-2 bg-slate-950/80 px-5 py-3 rounded-2xl border border-teal-500/30">
                <span className="text-3xl font-extrabold text-teal-400">
                  {Math.round(test_run.ai_readiness_score || 85)}
                </span>
                <span className="text-xs font-semibold text-slate-500">/ 100</span>
              </div>
            </div>

            {test_run.target_type === 'localhost' && (
              <div className="text-[11px] text-amber-300/90 bg-amber-500/10 p-3 rounded-xl border border-amber-500/20">
                <strong>Local Environment Notice:</strong> Local readiness evaluated from rendered DOM & code structures. Public discoverability is not evaluated on localhost.
              </div>
            )}
          </div>

          {/* 10 Category Breakdown Grid */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              10-Category Machine Readability Breakdown
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-3">
              {test_run.ai_readiness_data?.category_scores && Object.entries(test_run.ai_readiness_data.category_scores).map(([catKey, catVal]: [string, any]) => {
                const s = catVal.score || 85;
                const scoreColor = s >= 85 ? 'text-emerald-400' : s >= 70 ? 'text-amber-400' : 'text-rose-400';
                const barColor = s >= 85 ? 'bg-emerald-500' : s >= 70 ? 'bg-amber-500' : 'bg-rose-500';
                return (
                  <div key={catKey} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{catVal.name}</span>
                      <span className={`text-xs font-extrabold font-mono ${scoreColor}`}>
                        {Math.round(s)} / 100
                      </span>
                    </div>

                    <div className="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden">
                      <div className={`h-full ${barColor} transition-all duration-500`} style={{ width: `${s}%` }} />
                    </div>

                    {catVal.findings && catVal.findings.length > 0 && (
                      <p className="text-[11px] text-slate-400 leading-snug pt-1">
                        {catVal.findings[0].message}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Structured Data & Entity Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Entity Consistency */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Cpu className="h-4 w-4 text-teal-400" /> Business Entity & Brand Identity
              </span>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                  <span className="text-slate-400">Consistency Status:</span>
                  <span className="text-emerald-400 font-semibold">
                    {test_run.ai_readiness_data?.entity_consistency?.is_consistent ? '✓ Highly Consistent' : '⚠️ Minor Differences'}
                  </span>
                </div>
                {test_run.ai_readiness_data?.entity_consistency?.detected_names && (
                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 space-y-1">
                    <span className="text-[11px] text-slate-500 block">Detected Brand Representations:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {test_run.ai_readiness_data.entity_consistency.detected_names.map((n: string, i: number) => (
                        <span key={i} className="text-xs text-white bg-slate-900 px-2 py-0.5 rounded border border-slate-800 font-mono">
                          {n}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Structured Data (JSON-LD) Inspector */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Code className="h-4 w-4 text-emerald-400" /> Schema.org & Structured Data
              </span>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                  <span className="text-slate-400">JSON-LD Present:</span>
                  <span className={test_run.ai_readiness_data?.structured_data?.found ? 'text-emerald-400 font-semibold' : 'text-amber-400 font-semibold'}>
                    {test_run.ai_readiness_data?.structured_data?.found ? '✓ Schemas Detected' : 'Missing Schema Markups'}
                  </span>
                </div>
                {test_run.ai_readiness_data?.structured_data?.types_detected && test_run.ai_readiness_data.structured_data.types_detected.length > 0 ? (
                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 space-y-1">
                    <span className="text-[11px] text-slate-500 block">Detected Schema Types:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {test_run.ai_readiness_data.structured_data.types_detected.map((t: string, i: number) => (
                        <span key={i} className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-mono">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-[11px] text-slate-400 italic">
                    No JSON-LD blocks found. Adding Organization / LocalBusiness schema boosts AI discovery.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Top AI Readiness Improvements */}
          {test_run.ai_readiness_data?.top_improvements && test_run.ai_readiness_data.top_improvements.length > 0 && (
            <div className="space-y-3 pt-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-teal-400">
                Top AI Readiness Improvements & Code Snippets
              </h3>
              <div className="space-y-3">
                {test_run.ai_readiness_data.top_improvements.map((rec: any, idx: number) => (
                  <div key={idx} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-teal-400" /> {rec.title}
                      </span>
                      <span className="text-[10px] uppercase font-bold text-teal-300 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20">
                        {rec.priority} Priority
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">{rec.evidence}</p>

                    <div className="text-[11px] text-slate-400 bg-slate-950 p-3 rounded-xl border border-slate-800">
                      <strong>Action:</strong> {rec.action}
                    </div>

                    {rec.code_fix && (
                      <div className="space-y-1 pt-1">
                        <div className="flex items-center justify-between text-xs text-slate-400">
                          <span className="font-semibold text-teal-300 text-[11px]">Recommended Code Snippet:</span>
                          <button
                            type="button"
                            onClick={() => handleCopyCode(rec.code_fix, `ai_rec_${idx}`)}
                            className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white bg-slate-800 px-2 py-1 rounded"
                          >
                            {copiedCodeId === `ai_rec_${idx}` ? (
                              <>
                                <Check className="h-3 w-3 text-emerald-400" /> Copied!
                              </>
                            ) : (
                              <>
                                <Copy className="h-3 w-3" /> Copy Snippet
                              </>
                            )}
                          </button>
                        </div>
                        <pre className="text-xs font-mono text-teal-300 bg-slate-950 p-3 rounded-xl border border-slate-800 overflow-x-auto whitespace-pre-wrap select-all">
                          {rec.code_fix}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 4. ISSUES TAB */}
      {activeTab === 'issues' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search issues by title, description, or page..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center gap-2">
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>

              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
              >
                <option value="all">All Categories</option>
                <option value="ui">UI & Layout</option>
                <option value="responsive">Responsive</option>
                <option value="functional">Functional & Links</option>
                <option value="forms">Forms</option>
                <option value="accessibility">Accessibility</option>
                <option value="performance">Performance</option>
                <option value="javascript">JavaScript</option>
                <option value="network">Network</option>
              </select>
            </div>
          </div>

          {/* Issues Table */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden divide-y divide-slate-800">
            {filteredIssues.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">
                No issues match your current search and filter criteria.
              </div>
            ) : (
              filteredIssues.map((iss) => (
                <div
                  key={iss.id}
                  onClick={() => setActiveIssue(iss)}
                  className="p-4 flex items-center justify-between gap-4 cursor-pointer hover:bg-slate-800/50 transition-colors"
                >
                  <div className="space-y-1.5 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      {iss.issue_number && (
                        <span className="rounded-md bg-emerald-500/20 text-emerald-400 px-2 py-0.5 text-xs font-bold font-mono border border-emerald-500/30">
                          #{iss.issue_number}
                        </span>
                      )}
                      <SeverityBadge severity={iss.severity} />
                      <CategoryBadge category={iss.category} />
                      {iss.section && (
                        <span className="rounded bg-slate-800/80 px-2 py-0.5 text-[10px] font-semibold text-slate-300 border border-slate-700">
                          {iss.section}
                        </span>
                      )}
                      {iss.viewport && (
                        <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
                          {iss.viewport}
                        </span>
                      )}
                      {iss.coordinates && iss.coordinates.width ? (
                        <span className="rounded bg-slate-950 px-2 py-0.5 text-[10px] font-mono text-slate-300 border border-slate-800">
                          📍 {iss.coordinates.width}×{iss.coordinates.height}px
                        </span>
                      ) : null}
                      <h4 className="text-xs font-bold text-white truncate">{iss.title}</h4>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed line-clamp-2">{iss.description}</p>
                    <div className="flex items-center gap-3 text-[11px] font-mono text-slate-500 flex-wrap">
                      <span className="truncate">{iss.page_url}</span>
                      {iss.selector && (
                        <span className="text-slate-400 truncate">Selector: <code className="text-emerald-400">{iss.selector}</code></span>
                      )}
                      {iss.source_location?.source_file && (
                        <span className="text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20 truncate">
                          📁 {iss.source_location.source_file}:{iss.source_location.line_number}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {iss.fix_confidence && (
                      <span className={`hidden md:inline-flex text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                        iss.fix_confidence === 'high'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        Fix: {iss.fix_confidence}
                      </span>
                    )}
                    {(iss.annotated_screenshot_url || iss.screenshot_url) && (
                      <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
                        Visual Location
                      </span>
                    )}
                    <ChevronRight className="h-4 w-4 text-slate-500 flex-shrink-0" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* 3. PAGES TAB */}
      {activeTab === 'pages' && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-slate-800 bg-slate-950/80 text-[11px] uppercase font-semibold text-slate-400 tracking-wider">
              <tr>
                <th className="p-4">Page URL</th>
                <th className="p-4">Status</th>
                <th className="p-4">Load Time</th>
                <th className="p-4">Links</th>
                <th className="p-4">Images</th>
                <th className="p-4">Forms</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {pages.map((p) => (
                <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-4">
                    <a href={p.url} target="_blank" rel="noopener noreferrer" className="text-white hover:text-emerald-400 font-semibold truncate block max-w-md">
                      {p.url}
                    </a>
                    {p.title && <span className="text-[10px] text-slate-400 font-sans block">{p.title}</span>}
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      p.status_code === 200 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                    }`}>
                      {p.status_code}
                    </span>
                  </td>
                  <td className="p-4 text-slate-300">{p.load_time_ms ? `${p.load_time_ms}ms` : '—'}</td>
                  <td className="p-4 text-slate-400">{p.links_count}</td>
                  <td className="p-4 text-slate-400">{p.images_count}</td>
                  <td className="p-4 text-slate-400">{p.forms_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 4. RESPONSIVE & SCREENSHOTS */}
      {activeTab === 'responsive' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {screenshots.map((s) => {
            const vpIssues = issues.filter(i => (i.viewport === s.viewport || !i.viewport) && i.coordinates?.width);
            return (
              <div key={s.id} className="rounded-2xl border border-slate-800 bg-slate-900 overflow-hidden space-y-3 p-4 shadow-xl">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white font-mono uppercase tracking-wider">{s.viewport}</span>
                  <span className="text-[11px] text-slate-500 font-mono">{s.width} × {s.height}</span>
                </div>
                
                <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden relative group">
                  <img
                    src={s.url_path}
                    alt={s.viewport}
                    className="w-full h-auto object-contain transition-transform duration-300 group-hover:scale-105"
                  />
                  {vpIssues.length > 0 && (
                    <div className="absolute top-2 right-2 bg-slate-950/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[10px] font-bold text-amber-400 border border-amber-500/30 flex items-center gap-1">
                      <span>{vpIssues.length} Markers</span>
                    </div>
                  )}
                </div>

                <div className="space-y-1">
                  <p className="text-[11px] text-slate-400 font-mono truncate">{s.page_url}</p>
                  {vpIssues.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {vpIssues.slice(0, 4).map((iss) => (
                        <button
                          key={iss.id}
                          onClick={() => setActiveIssue(iss)}
                          className="rounded bg-slate-950 px-2 py-0.5 text-[10px] font-mono text-emerald-400 border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-800 transition-colors"
                        >
                          #{iss.issue_number} {iss.title.slice(0, 16)}...
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* 5. FORMS TAB */}
      {activeTab === 'forms' && (
        <div className="space-y-4">
          {forms.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-500 text-xs">
              No forms detected on the crawled pages.
            </div>
          ) : (
            forms.map((f) => (
              <div key={f.id} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-emerald-400" />
                    <code className="text-xs font-mono font-bold text-white">{f.selector}</code>
                  </div>
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-bold text-slate-300 uppercase">
                    Method: {f.method}
                  </span>
                </div>

                <p className="text-xs text-slate-400 font-mono">Found on: {f.page_url}</p>

                {/* Fields list */}
                <div className="rounded-xl border border-slate-800 bg-slate-950 p-3 space-y-2">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Discovered Form Fields ({f.fields.length})
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-xs">
                    {f.fields.map((fld, idx) => (
                      <div key={idx} className="rounded-lg border border-slate-800 bg-slate-900/80 p-2 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-semibold text-emerald-400">{fld.name || `field_${idx}`}</span>
                          <span className="text-[10px] text-slate-500">{fld.type}</span>
                        </div>
                        {fld.label && <p className="text-[11px] text-slate-300 truncate">Label: {fld.label}</p>}
                        {fld.required && <span className="inline-block text-[10px] text-amber-400 font-semibold font-mono">Required</span>}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* 6. VISUAL REGRESSION TAB */}
      {activeTab === 'visual' && (
        <div className="space-y-6">
          {visualRegressionIssues.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-400 text-xs">
              No visual regression detected. Visual presentation matches baseline or this is the first baseline test run.
            </div>
          ) : (
            visualRegressionIssues.map((vr) => (
              <DiffViewer
                key={vr.id}
                currentUrl={vr.evidence?.current_screenshot || ''}
                previousUrl={vr.evidence?.previous_screenshot || ''}
                diffMaskUrl={vr.evidence?.diff_mask_url}
                diffPercentage={vr.evidence?.diff_percentage}
                viewport={vr.viewport}
              />
            ))
          )}
        </div>
      )}

      {/* Slide-over Issue Detail Modal */}
      <IssueDetailModal
        issue={activeIssue}
        onClose={() => setActiveIssue(null)}
        onStatusUpdated={(updated) => {
          setReport(prev => prev ? {
            ...prev,
            issues: prev.issues.map(i => i.id === updated.id ? updated : i)
          } : null);
          setActiveIssue(updated);
        }}
      />
    </div>
  );
};
