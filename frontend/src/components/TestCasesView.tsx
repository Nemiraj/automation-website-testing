import React from 'react';
import { FileCheck2, Sparkles, ShieldAlert, ArrowRight, CheckCircle2, Zap } from 'lucide-react';
import { TestCase } from '../types';

interface TestCasesViewProps {
  testCases: TestCase[];
}

export const TestCasesView: React.FC<TestCasesViewProps> = ({ testCases }) => {
  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-500/10 text-cyan-400 border border-blue-500/20">
              <FileCheck2 className="w-4 h-4" />
            </span>
            <h2 className="text-2xl font-black text-white tracking-tight">
              Synthesized Test Catalog ({testCases.length})
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Autonomously synthesized functional test scenarios, authentication matrices, boundary form fuzzing, and customer journeys.
          </p>
        </div>
      </div>

      <div className="space-y-5">
        {testCases.map((tc) => (
          <div
            key={tc.id}
            className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl space-y-5 hover:border-slate-600 transition shadow-xl group"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2.5 mb-2">
                  <span className="text-xs font-mono font-black text-white px-2 py-0.5 rounded bg-black/40 border border-white/5">{tc.id}</span>
                  <span className="px-2.5 py-0.5 rounded-md text-[10px] font-black bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    {tc.priority}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 capitalize">
                    {tc.category}
                  </span>
                  {tc.isAiGenerated && (
                    <span className="flex items-center gap-1 text-[10px] text-cyan-300 font-bold bg-cyan-500/10 px-2.5 py-0.5 rounded-md border border-cyan-500/20">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> AI Synthesized
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-black text-white">{tc.name}</h3>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{tc.description}</p>
              </div>
            </div>

            {/* Test Steps Timeline Breakdown */}
            <div className="pt-4 border-t border-border/60">
              <div className="text-[10px] uppercase font-extrabold tracking-wider text-slate-400 mb-3">Step Execution Sequence ({tc.steps.length} steps)</div>
              <div className="space-y-2">
                {tc.steps.map((s, idx) => (
                  <div key={s.id} className="p-3 bg-black/40 rounded-2xl text-xs flex flex-col md:flex-row md:items-center justify-between gap-2 border border-slate-800/80">
                    <div className="flex items-center gap-3">
                      <span className="text-slate-500 font-mono font-bold w-6">#{idx + 1}</span>
                      <span className="px-2 py-0.5 rounded bg-blue-500/20 text-cyan-300 font-bold font-mono text-[10px] uppercase">{s.action}</span>
                      <span className="text-slate-200 font-medium">{s.targetDescription}</span>
                    </div>
                    <span className="text-slate-400 text-[11px] font-mono truncate max-w-sm">{s.expectedResult}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
