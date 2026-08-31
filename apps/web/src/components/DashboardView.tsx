import React from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  AlertOctagon,
  AlertTriangle,
  Compass,
  ArrowRight,
  TrendingDown,
  TrendingUp,
  Activity,
  Layers,
  Sparkles,
  Play,
  Zap,
  Clock,
  Server,
  Globe,
  Check,
  X
} from 'lucide-react';
import { FailureInvestigation, TestRun, UserJourneyResult } from '@webtest/shared';

interface DashboardViewProps {
  testRun: TestRun | null;
  isRunning: boolean;
  progressData: { currentTest: number; totalTests: number; testName: string; status: string; completedPercentage: number } | null;
  onOpenInvestigation: (inv: FailureInvestigation) => void;
  onRunTests: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  testRun,
  isRunning,
  progressData,
  onOpenInvestigation,
  onRunTests
}) => {
  if (!testRun && !isRunning) {
    return (
      <div className="py-20 px-6 text-center max-w-2xl mx-auto space-y-8 animate-fade-in">
        <div className="relative w-24 h-24 mx-auto">
          <div className="absolute -inset-2 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-3xl blur-lg opacity-60 animate-pulse"></div>
          <div className="relative w-24 h-24 rounded-3xl bg-slate-900 border border-white/10 flex items-center justify-center text-cyan-400 shadow-2xl">
            <Compass className="w-12 h-12" />
          </div>
        </div>

        <div className="space-y-3">
          <h2 className="text-3xl font-black text-white tracking-tight sm:text-4xl">
            Autonomous Web QA & Interaction Diagnostics
          </h2>
          <p className="text-sm text-slate-400 leading-relaxed max-w-lg mx-auto">
            WebTest AI crawls your target website, discovers buttons, forms, and ARIA roles, synthesizes multi-step user journeys, and executes real Playwright interactions with Python AI diagnostics.
          </p>
        </div>

        <button
          onClick={onRunTests}
          className="px-8 py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-2xl font-extrabold text-sm shadow-2xl shadow-blue-500/30 hover:scale-105 transition-all flex items-center gap-3 mx-auto"
        >
          <Play className="w-5 h-5 fill-current" /> Run Full Test Suite in Python Engine
        </button>
      </div>
    );
  }

  const healthScore = testRun?.healthScore ?? 0;
  const healthColor = healthScore >= 80 ? 'text-emerald-400' : healthScore >= 50 ? 'text-amber-400' : 'text-red-400';
  const healthGradient = healthScore >= 80
    ? 'from-emerald-500/20 via-slate-900 to-slate-950 border-emerald-500/30'
    : healthScore >= 50
    ? 'from-amber-500/20 via-slate-900 to-slate-950 border-amber-500/30'
    : 'from-red-500/20 via-slate-900 to-slate-950 border-red-500/40';

  const criticalFailures = testRun?.results.filter(r => r.status === 'failed' && r.failureInvestigation) || [];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Live Execution Progress HUD */}
      {isRunning && (
        <div className="relative overflow-hidden p-6 bg-gradient-to-r from-blue-950/60 via-slate-900 to-indigo-950/60 border border-blue-500/40 rounded-3xl shadow-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="relative flex h-3.5 w-3.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-cyan-500"></span>
              </span>
              <span className="text-sm font-extrabold text-white tracking-wide">
                Live Autonomous Test Execution in Progress...
              </span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-blue-500/20 text-cyan-300 border border-blue-500/30">
                Step {progressData?.currentTest || 1} of {progressData?.totalTests || 5}
              </span>
            </div>
            <span className="text-xs font-mono font-bold text-cyan-400 bg-black/40 px-3 py-1 rounded-full border border-cyan-500/30">
              {progressData?.completedPercentage || 10}% Completed
            </span>
          </div>

          <div className="w-full bg-slate-950 rounded-full h-3 p-0.5 border border-white/10 overflow-hidden shadow-inner">
            <div
              className="bg-gradient-to-r from-blue-500 via-indigo-400 to-cyan-400 h-2 rounded-full transition-all duration-300 shadow-lg shadow-cyan-500/50"
              style={{ width: `${progressData?.completedPercentage || 15}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-xs text-slate-300 font-mono">
            <div className="truncate flex items-center gap-2">
              <Zap className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span>Active Target: <strong className="text-white">{progressData?.testName || 'Launching Python Playwright...'}</strong></span>
            </div>
            <span className="text-slate-400 shrink-0">Real-time DOM Interception Active</span>
          </div>
        </div>
      )}

      {/* Website Health & Core Summary Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Health Score Gauge */}
        <div className={`p-6 rounded-3xl border bg-gradient-to-b ${healthGradient} flex flex-col justify-between shadow-2xl relative overflow-hidden group`}>
          <div className="flex items-center justify-between">
            <div className="text-[11px] uppercase tracking-wider font-extrabold text-slate-400">
              Website Health Score
            </div>
            <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
              <Activity className={`w-4 h-4 ${healthColor}`} />
            </div>
          </div>

          <div className="my-4 flex items-baseline gap-3">
            <div className={`text-6xl font-black tracking-tight ${healthColor}`}>
              {healthScore}%
            </div>
            <div className="text-xs font-semibold text-slate-400">
              {healthScore >= 80 ? 'Optimal' : healthScore >= 50 ? 'Friction' : 'Critical'}
            </div>
          </div>

          <div className="text-xs text-slate-300 font-medium flex items-center gap-2">
            {healthScore >= 80 ? (
              <span className="text-emerald-400 font-bold flex items-center gap-1">✓ Production Ready</span>
            ) : (
              <span className="text-red-400 font-bold flex items-center gap-1">⚠ Critical Path Severed</span>
            )}
          </div>
        </div>

        {/* Test Execution Summary */}
        <div className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl flex flex-col justify-between shadow-xl">
          <div className="flex items-center justify-between">
            <div className="text-[11px] uppercase tracking-wider font-extrabold text-slate-400">
              Test Execution
            </div>
            <div className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400">
              <Layers className="w-4 h-4" />
            </div>
          </div>

          <div className="my-3">
            <div className="text-4xl font-black text-white">
              {testRun?.totalTests || 0}
            </div>
            <div className="text-xs text-slate-400 mt-1">Autonomous Test Cases</div>
          </div>

          <div className="flex items-center gap-3 text-xs pt-3 border-t border-border/60">
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> {testRun?.passedTests || 0} Passed
            </span>
            <span className="text-red-400 font-bold flex items-center gap-1">
              <AlertOctagon className="w-3.5 h-3.5" /> {testRun?.failedTests || 0} Failed
            </span>
          </div>
        </div>

        {/* Critical Revenue Blockers */}
        <div className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl flex flex-col justify-between shadow-xl">
          <div className="flex items-center justify-between">
            <div className="text-[11px] uppercase tracking-wider font-extrabold text-slate-400">
              Revenue Blockers
            </div>
            <div className="w-8 h-8 rounded-full bg-red-500/10 flex items-center justify-center text-red-400">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>

          <div className="my-3">
            <div className="text-4xl font-black text-red-400">
              {testRun?.criticalFailures || 0}
            </div>
            <div className="text-xs text-slate-400 mt-1">P0 Critical Severity Issues</div>
          </div>

          <div className="text-xs text-slate-400 pt-3 border-t border-border/60">
            {(testRun?.criticalFailures || 0) > 0 ? (
              <span className="text-red-400 font-semibold">Immediate engineering triage required</span>
            ) : (
              <span className="text-emerald-400 font-semibold">All transaction journeys clear</span>
            )}
          </div>
        </div>

        {/* API & JS Errors */}
        <div className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl flex flex-col justify-between shadow-xl">
          <div className="flex items-center justify-between">
            <div className="text-[11px] uppercase tracking-wider font-extrabold text-slate-400">
              API & Console Crashes
            </div>
            <div className="w-8 h-8 rounded-full bg-amber-500/10 flex items-center justify-center text-amber-400">
              <Server className="w-4 h-4" />
            </div>
          </div>

          <div className="my-3">
            <div className="text-4xl font-black text-amber-400">
              {(testRun?.apiFailuresCount || 0) + (testRun?.jsErrorsCount || 0)}
            </div>
            <div className="text-xs text-slate-400 mt-1">Total Telemetry Errors Recorded</div>
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400 font-mono pt-3 border-t border-border/60">
            <span>{testRun?.apiFailuresCount || 0} API 5xx/4xx</span>
            <span>•</span>
            <span>{testRun?.jsErrorsCount || 0} JS Exceptions</span>
          </div>
        </div>
      </div>

      {/* CRITICAL FAILURES HIGHLIGHT DEEP-DIVE */}
      {criticalFailures.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
              <h3 className="text-lg font-black text-white tracking-wide">
                Critical User Journey Failures & Business Impact
              </h3>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Ranked by AI Revenue Risk Scoring
            </span>
          </div>

          <div className="space-y-4">
            {criticalFailures.map((res) => {
              const inv = res.failureInvestigation!;
              return (
                <div
                  key={res.id}
                  className="p-6 bg-gradient-to-r from-red-950/30 via-slate-900 to-slate-900/90 border border-red-500/40 rounded-3xl hover:border-red-500/70 transition-all shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6"
                >
                  <div className="space-y-3 flex-1">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <span className="px-2.5 py-0.5 rounded-md text-[10px] font-black bg-red-500 text-white uppercase tracking-wider">
                        {inv.severity}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">
                        {inv.priority}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-md text-[10px] font-mono font-bold bg-red-500/10 text-red-300 border border-red-500/20">
                        Impact Score: {inv.businessImpactScore}/100
                      </span>
                      {inv.journeyName && (
                        <span className="text-xs text-slate-400 font-medium">
                          Journey: <strong className="text-slate-100">{inv.journeyName}</strong>
                        </span>
                      )}
                    </div>

                    <h4 className="text-lg font-black text-white">
                      {res.testName}
                    </h4>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      <strong>Failed Step:</strong> {inv.userAction} — <span className="text-red-300 font-mono">{inv.actual}</span>
                    </p>

                    <div className="p-3 bg-black/40 rounded-xl border border-white/5 text-xs text-cyan-200 font-mono flex items-start gap-2.5">
                      <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <div>
                        <div className="font-bold text-cyan-300">AI Root Cause Diagnosis:</div>
                        <div className="text-slate-300 mt-0.5">{inv.aiAnalysis.likelyCause}</div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <button
                      onClick={() => onOpenInvestigation(inv)}
                      className="px-5 py-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-2xl text-xs font-black shadow-xl shadow-red-600/30 flex items-center gap-2 transition hover:scale-105"
                    >
                      Investigate Breakdown <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* USER JOURNEYS MATRIX */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-black text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-cyan-400" />
            Synthesized User Journey Matrix
          </h3>
          <span className="text-xs text-slate-400 font-mono">
            {testRun?.userJourneys.length || 0} Active Journeys
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {testRun?.userJourneys.map((j) => {
            const isPassed = j.status === 'passed';
            return (
              <div
                key={j.id}
                className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 hover:border-slate-600 rounded-3xl flex flex-col justify-between space-y-4 shadow-xl transition duration-200"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                      {j.category}
                    </span>
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase ${
                        isPassed
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-red-500/20 text-red-400 border border-red-500/30'
                      }`}
                    >
                      {j.status}
                    </span>
                  </div>
                  <h4 className="text-base font-extrabold text-white">{j.name}</h4>
                  <div className="text-xs text-slate-400 mt-1 flex items-center gap-2 font-mono">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    <span>{j.completedSteps} of {j.totalSteps} steps completed ({j.durationMs}ms)</span>
                  </div>
                </div>

                {/* Step Progression Pills */}
                <div className="flex flex-wrap gap-1.5 pt-3 border-t border-border/60">
                  {j.steps.map((s, idx) => (
                    <span
                      key={idx}
                      className={`text-[10px] px-2.5 py-1 rounded-lg font-mono flex items-center gap-1 ${
                        s.status === 'passed'
                          ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-500/20'
                          : 'bg-red-950/40 text-red-300 border border-red-500/30 font-bold'
                      }`}
                    >
                      {s.status === 'passed' ? <Check className="w-3 h-3 text-emerald-400" /> : <X className="w-3 h-3 text-red-400" />}
                      {s.name.split(' ')[0]}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* REGRESSION & ROOT CAUSE GROUPS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Regression Summary */}
        <div className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
              Regression & Fix Tracker
            </h4>
            <span className="text-[10px] text-slate-500 font-mono">vs Prior Execution</span>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-2xl text-center">
              <div className="text-3xl font-black text-red-400">
                {testRun?.regressionSummary?.newFailures ?? testRun?.failedTests ?? 0}
              </div>
              <div className="text-[10px] text-slate-400 uppercase font-bold mt-1">New Failures</div>
            </div>
            <div className="p-4 bg-emerald-950/20 border border-emerald-500/30 rounded-2xl text-center">
              <div className="text-3xl font-black text-emerald-400">
                {testRun?.regressionSummary?.fixedFailures ?? 0}
              </div>
              <div className="text-[10px] text-slate-400 uppercase font-bold mt-1">Resolved</div>
            </div>
            <div className="p-4 bg-amber-950/20 border border-amber-500/30 rounded-2xl text-center">
              <div className="text-3xl font-black text-amber-400">
                {testRun?.regressionSummary?.continuingFailures ?? 0}
              </div>
              <div className="text-[10px] text-slate-400 uppercase font-bold mt-1">Continuing</div>
            </div>
          </div>
        </div>

        {/* Consolidated Root Cause Clustering */}
        <div className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
              Consolidated Root Cause Clusters
            </h4>
            <span className="text-[10px] text-slate-500 font-mono">AI Grouped</span>
          </div>

          {testRun?.failureGroups && testRun.failureGroups.length > 0 ? (
            <div className="space-y-2.5">
              {testRun.failureGroups.map((grp) => (
                <div key={grp.id} className="p-3.5 bg-black/40 border border-slate-800/80 rounded-2xl flex items-center justify-between">
                  <div className="pr-3">
                    <div className="text-xs font-bold text-white">{grp.title}</div>
                    <div className="text-[11px] font-mono text-slate-400 mt-0.5 truncate max-w-sm">{grp.primaryEvidence}</div>
                  </div>
                  <span className="px-2.5 py-1 text-[10px] font-mono bg-red-500/20 text-red-300 rounded-lg border border-red-500/30 font-bold shrink-0">
                    {grp.affectedCount} test(s)
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-slate-400 py-8 text-center font-mono">
              No clustered root-cause failures detected.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
