import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Compass,
  ArrowRight,
  TrendingDown,
  TrendingUp,
  ShieldCheck,
  Zap,
  Activity,
  Layers,
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { FailureInvestigation, TestRun } from '../types';

interface DashboardViewProps {
  testRun: TestRun | null;
  isRunning: boolean;
  progressData: {
    currentTest: number;
    totalTests: number;
    testName: string;
    status: string;
    completedPercentage: number;
  } | null;
  onOpenInvestigation: (investigation: FailureInvestigation) => void;
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
      <div className="py-24 text-center max-w-xl mx-auto space-y-6">
        <div className="w-20 h-20 rounded-3xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mx-auto text-cyan-400 shadow-2xl">
          <Zap className="w-10 h-10 animate-bounce" />
        </div>
        <div className="space-y-2">
          <h2 className="text-3xl font-black text-white tracking-tight">No Test Run Selected</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Run an autonomous test suite across user journeys, authentication matrices, and catalog discovery.
          </p>
        </div>
        <button
          onClick={onRunTests}
          className="px-8 py-3.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-2xl text-sm font-black shadow-xl shadow-blue-500/25 transition active:scale-95"
        >
          Start Autonomous Test Run
        </button>
      </div>
    );
  }

  const healthScore = testRun?.healthScore ?? 100;
  const isHealthy = healthScore >= 80;
  const isWarning = healthScore >= 50 && healthScore < 80;

  const failedTests = testRun?.results.filter((r) => r.status === 'failed') || [];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      
      {/* Live Execution Progress HUD (Visible when tests are actively executing) */}
      {isRunning && (
        <div className="p-6 rounded-3xl bg-gradient-to-r from-blue-950/60 via-slate-900/80 to-indigo-950/60 border border-blue-500/40 shadow-2xl space-y-4 animate-pulse-slow">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
              </div>
              <span className="text-xs font-black uppercase tracking-wider text-cyan-300">
                Live Playwright Execution in Progress
              </span>
            </div>
            <span className="text-xs font-mono text-slate-300">
              {progressData?.currentTest || 1} / {progressData?.totalTests || 5} Tests
            </span>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs font-bold text-slate-200">
              <span className="truncate max-w-md">{progressData?.testName || 'Synthesizing DOM Locators & Actions...'}</span>
              <span className="font-mono text-cyan-400">{progressData?.completedPercentage || 15}%</span>
            </div>
            <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400 rounded-full transition-all duration-500 shadow-sm"
                style={{ width: `${progressData?.completedPercentage || 15}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Top Executive Health & Metric KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Health Score Gauge */}
        <div className="p-6 rounded-3xl bg-surface/90 backdrop-blur-md border border-border/80 flex items-center justify-between shadow-xl relative overflow-hidden group">
          <div className="space-y-1">
            <div className="text-[11px] uppercase font-black tracking-wider text-slate-400">Website Health Score</div>
            <div className={`text-4xl font-black ${
              isHealthy ? 'text-emerald-400' : isWarning ? 'text-amber-400' : 'text-red-400'
            }`}>
              {healthScore}%
            </div>
            <div className="text-xs text-slate-400 font-medium">
              {isHealthy ? 'Optimal User Flow' : isWarning ? 'Moderate Degradation' : 'Critical Failure State'}
            </div>
          </div>

          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center border ${
            isHealthy
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              : isWarning
              ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
              : 'bg-red-500/10 border-red-500/30 text-red-400'
          }`}>
            <ShieldCheck className="w-8 h-8" />
          </div>
        </div>

        {/* Tests Execution Metric */}
        <div className="p-6 rounded-3xl bg-surface/90 backdrop-blur-md border border-border/80 flex items-center justify-between shadow-xl">
          <div className="space-y-1">
            <div className="text-[11px] uppercase font-black tracking-wider text-slate-400">Total Scenarios</div>
            <div className="text-4xl font-black text-white">{testRun?.totalTests || 0}</div>
            <div className="text-xs text-slate-400">
              <strong className="text-emerald-400">{testRun?.passedTests || 0} Passed</strong> • <strong className="text-red-400">{testRun?.failedTests || 0} Failed</strong>
            </div>
          </div>
          <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/30 text-cyan-400 flex items-center justify-center">
            <Activity className="w-8 h-8" />
          </div>
        </div>

        {/* Critical Revenue Failures Metric */}
        <div className="p-6 rounded-3xl bg-surface/90 backdrop-blur-md border border-border/80 flex items-center justify-between shadow-xl">
          <div className="space-y-1">
            <div className="text-[11px] uppercase font-black tracking-wider text-slate-400">Critical Blockers</div>
            <div className={`text-4xl font-black ${(testRun?.criticalFailures || 0) > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
              {testRun?.criticalFailures || 0}
            </div>
            <div className="text-xs text-slate-400">
              {(testRun?.criticalFailures || 0) > 0 ? 'Revenue path blocked' : 'Core funnels operational'}
            </div>
          </div>
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center border ${
            (testRun?.criticalFailures || 0) > 0 ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
          }`}>
            <AlertTriangle className="w-8 h-8" />
          </div>
        </div>

        {/* Execution Duration Metric */}
        <div className="p-6 rounded-3xl bg-surface/90 backdrop-blur-md border border-border/80 flex items-center justify-between shadow-xl">
          <div className="space-y-1">
            <div className="text-[11px] uppercase font-black tracking-wider text-slate-400">Execution Time</div>
            <div className="text-4xl font-black text-white">
              {((testRun?.durationMs || 0) / 1000).toFixed(1)}s
            </div>
            <div className="text-xs text-slate-400 font-mono">
              {testRun?.browser || 'chromium'} • {testRun?.environment || 'local'}
            </div>
          </div>
          <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/30 text-purple-400 flex items-center justify-center">
            <Clock className="w-8 h-8" />
          </div>
        </div>

      </div>

      {/* Critical Breakdown Highlights (Ranked by AI Business Impact) */}
      {failedTests.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20">
                <AlertTriangle className="w-4 h-4" />
              </span>
              <h3 className="text-lg font-black text-white tracking-tight">
                Critical Breakdowns Requiring Engineering Attention
              </h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              Ranked by Autonomous Business Impact Score
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {failedTests.map((res) => {
              const inv = res.failureInvestigation;
              if (!inv) return null;

              return (
                <div
                  key={res.id}
                  className="p-6 rounded-3xl bg-surface/90 backdrop-blur-md border border-red-500/40 hover:border-red-500/70 transition-all duration-300 space-y-4 shadow-xl group"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1.5">
                      <div className="flex flex-wrap items-center gap-2.5">
                        <span className="px-2.5 py-0.5 rounded-md text-[10px] font-black bg-red-500 text-white uppercase tracking-wider">
                          {inv.severity}
                        </span>
                        <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">
                          {inv.priority}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          Step {inv.failedStepIndex + 1} of {inv.totalSteps}
                        </span>
                        {inv.journeyName && (
                          <span className="text-xs font-semibold text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-md border border-cyan-500/20">
                            {inv.journeyName}
                          </span>
                        )}
                      </div>

                      <h4 className="text-xl font-black text-white group-hover:text-cyan-300 transition">
                        {res.testName}
                      </h4>
                    </div>

                    <div className="flex items-center gap-4 self-start md:self-auto">
                      <div className="text-right">
                        <div className="text-[10px] uppercase font-bold text-slate-400">Business Impact</div>
                        <div className="text-2xl font-black text-red-400">{inv.businessImpactScore} / 100</div>
                      </div>

                      <button
                        onClick={() => onOpenInvestigation(inv)}
                        className="px-5 py-2.5 rounded-2xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white text-xs font-bold transition shadow-lg shadow-red-600/30 flex items-center gap-1.5 shrink-0 active:scale-95"
                      >
                        <span>Investigate Breakdown</span>
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Impact Summary & Comparison Row */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                    <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                      <div className="text-[10px] uppercase font-bold text-blue-400">Expected Outcome</div>
                      <div className="text-xs text-slate-200">{inv.expected}</div>
                    </div>
                    <div className="p-4 rounded-2xl bg-red-950/20 border border-red-500/30 space-y-1">
                      <div className="text-[10px] uppercase font-bold text-red-400">Actual Failure State</div>
                      <div className="text-xs text-red-200 font-mono">{inv.actual}</div>
                    </div>
                  </div>

                  {/* AI Quick Diagnosis Strip */}
                  <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-center gap-3">
                    <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
                    <p className="text-xs text-slate-300 leading-relaxed font-medium">
                      <strong className="text-cyan-300">AI Root Cause:</strong> {inv.aiAnalysis.likelyCause}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Synthesized User Journey Matrix */}
      {testRun?.userJourneys && testRun.userJourneys.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-blue-500/10 text-cyan-400 border border-blue-500/20">
                <Compass className="w-4 h-4" />
              </span>
              <h3 className="text-lg font-black text-white tracking-tight">
                Synthesized User Journeys Progress
              </h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              {testRun.userJourneys.length} High-Value Customer Funnels
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {testRun.userJourneys.map((journey) => {
              const isPassed = journey.status === 'passed';
              return (
                <div
                  key={journey.id}
                  className="p-5 rounded-3xl bg-surface/90 backdrop-blur-md border border-border/80 space-y-4 shadow-xl"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${
                            isPassed
                              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                              : 'bg-red-500/20 text-red-400 border border-red-500/30'
                          }`}
                        >
                          {journey.status}
                        </span>
                        <span className="text-xs font-mono text-slate-400">
                          {journey.durationMs}ms
                        </span>
                      </div>
                      <h4 className="text-base font-bold text-white">{journey.name}</h4>
                    </div>

                    <div className="text-right">
                      <div className="text-[10px] uppercase font-bold text-slate-400">Risk Score</div>
                      <div className={`text-lg font-black ${journey.businessImpactScore > 70 ? 'text-red-400' : 'text-emerald-400'}`}>
                        {journey.businessImpactScore} / 100
                      </div>
                    </div>
                  </div>

                  {/* Step Nodes Track */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>Progress</span>
                      <span className="font-mono font-bold text-slate-200">
                        {journey.completedSteps} / {journey.totalSteps} steps completed
                      </span>
                    </div>
                    <div className="grid grid-cols-5 gap-1.5">
                      {journey.steps.map((st, sIdx) => {
                        const stepPassed = st.status === 'passed';
                        return (
                          <div
                            key={sIdx}
                            title={`${st.name} (${st.status})`}
                            className={`h-2 rounded-full transition-all ${
                              stepPassed
                                ? 'bg-emerald-500 shadow-sm shadow-emerald-500/20'
                                : 'bg-red-500 shadow-sm shadow-red-500/40 animate-pulse'
                            }`}
                          />
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Regression & Root Cause Clusters */}
      {testRun?.failureGroups && testRun.failureGroups.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Layers className="w-4 h-4" />
            </span>
            <h3 className="text-lg font-black text-white tracking-tight">
              Clustered Failure Root Causes
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {testRun.failureGroups.map((group) => (
              <div
                key={group.id}
                className="p-5 rounded-3xl bg-surface/90 backdrop-blur-md border border-slate-700/80 space-y-3 shadow-xl"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="px-2.5 py-0.5 rounded-md text-[10px] font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 uppercase">
                      {group.rootCauseType}
                    </span>
                    <h4 className="text-base font-bold text-white mt-2">{group.title}</h4>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-black bg-slate-900 text-slate-300 border border-slate-800">
                    {group.affectedCount} tests affected
                  </span>
                </div>

                <div className="p-3 bg-black/40 rounded-xl border border-white/5 font-mono text-xs text-slate-300 truncate">
                  {group.primaryEvidence}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
