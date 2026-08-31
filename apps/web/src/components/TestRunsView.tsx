import React from 'react';
import { PlayCircle, Download, CheckCircle2, AlertOctagon, ArrowRight, FileText, Code2, Clock } from 'lucide-react';
import { TestRun } from '@webtest/shared';

interface TestRunsViewProps {
  runs: TestRun[];
  onSelectRun: (run: TestRun) => void;
}

export const TestRunsView: React.FC<TestRunsViewProps> = ({ runs, onSelectRun }) => {
  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-500/10 text-cyan-400 border border-blue-500/20">
              <PlayCircle className="w-4 h-4" />
            </span>
            <h2 className="text-2xl font-black text-white tracking-tight">
              Historical Test Runs & Executive QA Reports
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Browse previous execution runs, compare regression health, and download standalone HTML/JSON executive QA reports.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {runs.map((run) => {
          const isHealthy = run.healthScore >= 80;
          return (
            <div
              key={run.id}
              className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-5 hover:border-slate-600 transition shadow-xl group"
            >
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-xs font-mono font-black text-white">{run.id}</span>
                  <span
                    className={`px-2.5 py-0.5 rounded-md text-[10px] font-black uppercase ${
                      isHealthy
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-red-500/20 text-red-400 border border-red-500/30'
                    }`}
                  >
                    {run.healthScore}% HEALTH
                  </span>
                  <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    {new Date(run.startedAt).toLocaleString()}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300 font-mono">
                  <span className="text-emerald-400 font-bold">{run.passedTests} passed</span>
                  <span>•</span>
                  <span className="text-red-400 font-bold">{run.failedTests} failed</span>
                  <span>•</span>
                  <span className="text-slate-400">{(run.durationMs / 1000).toFixed(1)}s duration</span>
                  <span>•</span>
                  <span className="text-slate-400">{run.browser}</span>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <a
                  href={`/api/reports/${run.id}?download=true`}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2.5 bg-black/40 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-bold flex items-center gap-2 transition"
                >
                  <FileText className="w-4 h-4 text-cyan-400" /> HTML Report
                </a>
                <a
                  href={`/api/reports/${run.id}?format=json`}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2.5 bg-black/40 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-bold flex items-center gap-2 transition"
                >
                  <Code2 className="w-4 h-4 text-cyan-400" /> JSON Export
                </a>
                <button
                  onClick={() => onSelectRun(run)}
                  className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 transition shadow-lg shadow-blue-500/20"
                >
                  Open Run <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
