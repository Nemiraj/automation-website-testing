import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
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
  ChevronRight
} from 'lucide-react';
import { ScoreGauge } from '../components/ScoreGauge';
import { SeverityBadge, CategoryBadge } from '../components/IssueBadge';
import { IssueDetailModal } from '../components/IssueDetailModal';
import { DiffViewer } from '../components/DiffViewer';
import { TestService } from '../services/api';
import { TestReport, IssueItem } from '../types';

export const TestReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<TestReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'issues' | 'pages' | 'responsive' | 'forms' | 'visual' | 'ai'>('overview');
  
  // Issue filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [activeIssue, setActiveIssue] = useState<IssueItem | null>(null);

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
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
                Audit Completed
              </span>
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
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-2 border-t border-slate-800">
          {[
            { label: 'UI & Layout', score: scores.ui, icon: Layers },
            { label: 'Responsive', score: scores.responsive, icon: Smartphone },
            { label: 'Functional', score: scores.functional, icon: CheckCircle2 },
            { label: 'Forms', score: scores.forms, icon: FileText },
            { label: 'Accessibility', score: scores.accessibility, icon: Eye },
            { label: 'Performance', score: scores.performance, icon: Gauge },
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
          { id: 'overview', label: 'Overview & AI' },
          { id: 'issues', label: `Issues (${issues.length})` },
          { id: 'pages', label: `Pages (${pages.length})` },
          { id: 'responsive', label: `Screenshots (${screenshots.length})` },
          { id: 'forms', label: `Forms (${forms.length})` },
          { id: 'visual', label: `Visual Diff (${visualRegressionIssues.length})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2.5 text-xs font-bold rounded-t-xl transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-slate-900 text-emerald-400 border-t-2 border-emerald-500'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {/* 1. OVERVIEW & AI */}
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

      {/* 2. ISSUES TAB */}
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
                      <SeverityBadge severity={iss.severity} />
                      <CategoryBadge category={iss.category} />
                      {iss.viewport && (
                        <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
                          {iss.viewport}
                        </span>
                      )}
                      <h4 className="text-xs font-bold text-white truncate">{iss.title}</h4>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed line-clamp-2">{iss.description}</p>
                    <p className="text-[11px] font-mono text-slate-500 truncate">{iss.page_url}</p>
                  </div>
                  <ChevronRight className="h-4 w-4 text-slate-500 flex-shrink-0" />
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {screenshots.map((s) => (
            <div key={s.id} className="rounded-2xl border border-slate-800 bg-slate-900 overflow-hidden space-y-2 p-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-white font-mono">{s.viewport}</span>
                <span className="text-[11px] text-slate-500">{s.width} × {s.height}</span>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden max-h-72 flex items-center justify-center">
                <img src={s.url_path} alt={s.viewport} className="w-full h-auto object-contain hover:scale-105 transition-transform duration-300" />
              </div>
              <p className="text-[11px] text-slate-400 font-mono truncate">{s.page_url}</p>
            </div>
          ))}
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
