import React from 'react';
import { Compass, CheckCircle2, AlertOctagon, Clock, ArrowRight, ShieldCheck, Zap, Check, X } from 'lucide-react';
import { UserJourneyResult } from '../types';

interface UserJourneysViewProps {
  journeys: UserJourneyResult[];
}

export const UserJourneysView: React.FC<UserJourneysViewProps> = ({ journeys }) => {
  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-500/10 text-cyan-400 border border-blue-500/20">
              <Compass className="w-4 h-4" />
            </span>
            <h2 className="text-2xl font-black text-white tracking-tight">
              End-to-End Synthesized User Journeys
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Simulated high-value user workflows verifying whether customers can navigate, purchase, authenticate, and search without friction.
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {journeys.map((journey) => {
          const isPassed = journey.status === 'passed';
          return (
            <div
              key={journey.id}
              className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl space-y-6 shadow-2xl hover:border-slate-600 transition"
            >
              {/* Journey Header */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span
                      className={`px-2.5 py-0.5 rounded-md text-[10px] font-black uppercase ${
                        isPassed
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-red-500/20 text-red-400 border border-red-500/30'
                      }`}
                    >
                      {journey.status}
                    </span>
                    <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-500" /> {journey.durationMs}ms
                    </span>
                    <span className="text-xs text-slate-400">
                      Completed: <strong className="text-white">{journey.completedSteps} / {journey.totalSteps} steps</strong>
                    </span>
                  </div>
                  <h3 className="text-xl font-black text-white">{journey.name}</h3>
                </div>

                <div className="p-4 bg-black/40 border border-white/5 rounded-2xl text-right shrink-0">
                  <div className="text-[10px] uppercase font-bold text-slate-400">Revenue Impact Risk</div>
                  <div className={`text-2xl font-black ${journey.businessImpactScore > 70 ? 'text-red-400' : 'text-emerald-400'}`}>
                    {journey.businessImpactScore} <span className="text-xs text-slate-500">/ 100</span>
                  </div>
                </div>
              </div>

              {/* Visual Flow Nodes Horizontal Timeline */}
              <div className="overflow-x-auto pb-4 pt-2">
                <div className="flex items-center gap-3 min-w-max">
                  {journey.steps.map((step, idx) => {
                    const stepPassed = step.status === 'passed';
                    return (
                      <React.Fragment key={idx}>
                        <div
                          className={`p-5 rounded-2xl border min-w-[220px] max-w-[260px] flex flex-col justify-between transition-all duration-200 ${
                            stepPassed
                              ? 'bg-emerald-950/10 border-emerald-500/30 text-emerald-300 shadow-lg'
                              : 'bg-red-950/20 border-red-500/60 text-red-200 shadow-xl shadow-red-500/10 scale-105'
                          }`}
                        >
                          <div className="flex items-center justify-between text-[11px] mb-2 font-mono">
                            <span className="font-bold text-slate-400">Step {idx + 1}</span>
                            <span className={`px-2 py-0.5 rounded-md text-[10px] font-black uppercase flex items-center gap-1 ${
                              stepPassed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500 text-white'
                            }`}>
                              {stepPassed ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                              {step.status}
                            </span>
                          </div>
                          <div className="text-xs font-bold text-white mb-2 leading-relaxed">
                            {step.name}
                          </div>
                          <div className="text-[10px] text-slate-400 font-mono flex items-center justify-between pt-2 border-t border-white/5">
                            <span>{step.action}</span>
                            <span>{step.durationMs}ms</span>
                          </div>
                        </div>

                        {idx < journey.steps.length - 1 && (
                          <ArrowRight className="w-4 h-4 text-slate-700 shrink-0" />
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
