import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  PlayCircle, 
  ExternalLink, 
  ArrowLeft, 
  ArrowUpRight,
  ShieldCheck,
  Activity,
  History
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ProjectService, TestService } from '../services/api';
import { Project, TestRun } from '../types';

export const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchData = async () => {
      try {
        const [pData, runsData] = await Promise.all([
          ProjectService.get(id),
          TestService.list(id)
        ]);
        setProject(pData);
        setTestRuns(runsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p>Project not found.</p>
        <Link to="/projects" className="text-xs text-emerald-400 hover:underline mt-2 inline-block">Back to Projects</Link>
      </div>
    );
  }

  // Chart data for score history over time
  const chartData = [...testRuns]
    .reverse()
    .filter(t => t.overall_score != null)
    .map((t, idx) => ({
      name: `Run #${idx + 1}`,
      score: Math.round(t.overall_score || 0),
      date: new Date(t.created_at).toLocaleDateString()
    }));

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="space-y-4">
        <Link to="/projects" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Projects
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-3xl border border-slate-800 bg-slate-900/60 p-6 sm:p-8">
          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">{project.name}</h1>
            <p className="text-xs text-slate-400 font-mono flex items-center gap-1">
              {project.base_url}
              <a href={project.base_url} target="_blank" rel="noopener noreferrer" className="hover:text-emerald-400">
                <ExternalLink className="h-3 w-3" />
              </a>
            </p>
            {project.description && (
              <p className="text-xs text-slate-300 max-w-xl">{project.description}</p>
            )}
          </div>

          <Link
            to={`/new-test?url=${encodeURIComponent(project.base_url)}&projectId=${project.id}`}
            className="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-3 text-xs font-bold text-slate-950 hover:bg-emerald-400 active:scale-95 transition-all shadow-md shadow-emerald-950/40"
          >
            <PlayCircle className="h-4 w-4" />
            <span>Run Automated Audit</span>
          </Link>
        </div>
      </div>

      {/* Score Trend Chart */}
      {chartData.length > 1 && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="h-4 w-4 text-emerald-400" /> Historical Quality Score Trend
            </h2>
            <span className="text-xs text-slate-400">0 - 100 Scale</span>
          </div>

          <div className="h-48 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Test Runs History Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <History className="h-4 w-4 text-emerald-400" /> Audit History
          </h2>
          <span className="text-xs text-slate-400">{testRuns.length} total runs</span>
        </div>

        {testRuns.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-800 p-8 text-center text-xs text-slate-500">
            No audits executed for this project yet.
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {testRuns.map((r) => (
              <div key={r.id} className="py-3.5 flex items-center justify-between gap-4">
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Link
                      to={r.status === 'completed' ? `/tests/${r.id}/report` : `/tests/${r.id}/progress`}
                      className="text-xs font-bold text-white hover:text-emerald-400 truncate"
                    >
                      Audit Run {new Date(r.created_at).toLocaleString()}
                    </Link>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      r.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {r.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    {r.total_pages_scanned} pages • {r.critical_issues_count} critical • {r.high_issues_count} high
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  {r.overall_score != null && (
                    <span className="text-sm font-extrabold text-white">
                      {Math.round(r.overall_score)}/100
                    </span>
                  )}
                  <Link
                    to={r.status === 'completed' ? `/tests/${r.id}/report` : `/tests/${r.id}/progress`}
                    className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white"
                  >
                    <ArrowUpRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
