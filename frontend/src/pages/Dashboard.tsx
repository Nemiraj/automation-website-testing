import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Activity, 
  PlayCircle, 
  FolderKanban, 
  AlertOctagon, 
  ShieldCheck, 
  ExternalLink,
  ChevronRight,
  ArrowUpRight,
  Sparkles
} from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { ScoreGauge } from '../components/ScoreGauge';
import { SeverityBadge } from '../components/IssueBadge';
import { TestService, ProjectService } from '../services/api';
import { TestRun, Project } from '../types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [quickUrl, setQuickUrl] = useState('');
  const [recentTests, setRecentTests] = useState<TestRun[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [testsData, projectsData] = await Promise.all([
          TestService.list(),
          ProjectService.list()
        ]);
        setRecentTests(testsData);
        setProjects(projectsData);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleQuickTest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickUrl.trim()) return;

    const isLh = quickUrl.includes('localhost') || quickUrl.includes('127.0.0.1');
    setSubmitting(true);
    try {
      const test = await TestService.create({ 
        target_url: quickUrl.trim(),
        target_type: isLh ? 'localhost' : 'live'
      });
      navigate(`/tests/${test.id}/progress`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start automated test');
    } finally {
      setSubmitting(false);
    }
  };

  const completedTests = recentTests.filter(t => t.status === 'completed' && t.overall_score != null);
  const avgScore = completedTests.length
    ? Math.round(completedTests.reduce((acc, t) => acc + (t.overall_score || 0), 0) / completedTests.length)
    : 100;

  const totalCritical = recentTests.reduce((acc, t) => acc + (t.critical_issues_count || 0), 0);
  const totalHigh = recentTests.reduce((acc, t) => acc + (t.high_issues_count || 0), 0);

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      {/* Hero Quick Test Launch Bar */}
      <div className="rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/90 via-slate-900/60 to-slate-950 p-8 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-2xl space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
            <Sparkles className="h-3.5 w-3.5" />
            Autonomous Playwright QA & AI Auditing
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            Automated Website Health & UX Testing
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Instantly inspect layout, responsive viewports, broken links, images, console errors, forms, accessibility, and performance.
          </p>
        </div>

        {/* Quick URL form */}
        <form onSubmit={handleQuickTest} className="mt-6 flex flex-col sm:flex-row gap-3 relative z-10 max-w-2xl">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="https://example.com"
              value={quickUrl}
              onChange={(e) => setQuickUrl(e.target.value)}
              required
              className="w-full rounded-xl border border-slate-700 bg-slate-950/90 px-4 py-3 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 font-mono shadow-inner"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center justify-center gap-2 rounded-xl bg-emerald-500 px-6 py-3 text-sm font-semibold text-slate-950 hover:bg-emerald-400 active:scale-95 transition-all shadow-lg shadow-emerald-950/50 disabled:opacity-50"
          >
            <PlayCircle className="h-4 w-4" />
            <span>{submitting ? 'Initializing...' : 'Start Audit'}</span>
          </button>
        </form>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Average Health Score"
          value={`${avgScore}/100`}
          subtitle="Across recent test runs"
          icon={ShieldCheck}
          color="emerald"
        />
        <StatCard
          title="Active Projects"
          value={projects.length}
          subtitle="Configured target domains"
          icon={FolderKanban}
          color="blue"
        />
        <StatCard
          title="Critical Issues"
          value={totalCritical}
          subtitle="Immediate developer blockers"
          icon={AlertOctagon}
          color="rose"
        />
        <StatCard
          title="High Priority Issues"
          value={totalHigh}
          subtitle="UX & compliance warnings"
          icon={Activity}
          color="amber"
        />
      </div>

      {/* Recent Tests Table & Project Shortcuts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Tests (2 cols) */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white">Recent Test Runs</h2>
              <p className="text-xs text-slate-400">Latest automated scan results and progress</p>
            </div>
            <Link to="/new-test" className="text-xs font-semibold text-emerald-400 hover:underline flex items-center gap-1">
              New Test <ChevronRight className="h-3 w-3" />
            </Link>
          </div>

          {recentTests.length === 0 && !loading ? (
            <div className="rounded-xl border border-dashed border-slate-800 p-8 text-center text-slate-500 text-xs">
              No tests executed yet. Enter a website URL above to start your first automated audit!
            </div>
          ) : (
            <div className="divide-y divide-slate-800/80 overflow-x-auto">
              {recentTests.slice(0, 6).map((test) => (
                <div key={test.id} className="py-3.5 flex items-center justify-between gap-4 hover:bg-slate-900/40 px-2 rounded-lg transition-colors">
                  <div className="min-w-0 space-y-1">
                    <div className="flex items-center gap-2">
                      <Link
                        to={test.status === 'completed' ? `/tests/${test.id}/report` : `/tests/${test.id}/progress`}
                        className="text-sm font-semibold text-white hover:text-emerald-400 truncate block font-mono"
                      >
                        {test.target_url}
                      </Link>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${
                        test.target_type === 'localhost'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-teal-500/10 text-teal-400 border border-teal-500/20'
                      }`}>
                        {test.target_type === 'localhost' ? 'Localhost' : 'Live'}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        test.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        test.status === 'running' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {test.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      {new Date(test.created_at).toLocaleString()} • {test.total_pages_scanned} pages inspected
                    </p>
                  </div>

                  <div className="flex items-center gap-4 flex-shrink-0">
                    {test.overall_score != null ? (
                      <div className="text-right">
                        <span className="text-base font-extrabold text-white">
                          {Math.round(test.overall_score)}
                        </span>
                        <span className="text-[10px] text-slate-400 block font-semibold">SCORE</span>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500 font-mono">
                        {test.progress_percentage}%
                      </span>
                    )}

                    <Link
                      to={test.status === 'completed' ? `/tests/${test.id}/report` : `/tests/${test.id}/progress`}
                      className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
                    >
                      <ArrowUpRight className="h-4 w-4" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Projects Column (1 col) */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white">Projects</h2>
              <p className="text-xs text-slate-400">Managed target domains</p>
            </div>
            <Link to="/projects" className="text-xs font-semibold text-emerald-400 hover:underline flex items-center gap-1">
              View All <ChevronRight className="h-3 w-3" />
            </Link>
          </div>

          {projects.length === 0 && !loading ? (
            <div className="rounded-xl border border-dashed border-slate-800 p-6 text-center text-slate-500 text-xs">
              No projects created yet.
            </div>
          ) : (
            <div className="space-y-3">
              {projects.slice(0, 4).map((p) => (
                <Link
                  key={p.id}
                  to={`/projects/${p.id}`}
                  className="block rounded-xl border border-slate-800 bg-slate-950 p-3.5 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-white truncate">{p.name}</h3>
                    {p.latest_score != null && (
                      <span className="text-xs font-extrabold text-emerald-400">{Math.round(p.latest_score)}/100</span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono mt-1 truncate">{p.base_url}</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
