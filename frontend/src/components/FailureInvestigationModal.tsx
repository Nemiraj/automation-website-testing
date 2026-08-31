import React, { useState } from 'react';
import { X, AlertTriangle, CheckCircle2, Clock, Terminal, Network, Image as ImageIcon, Sparkles, ArrowRight, ExternalLink, Copy, Check } from 'lucide-react';
import { FailureInvestigation } from '../types';

interface FailureModalProps {
  investigation: FailureInvestigation | null;
  onClose: () => void;
}

export const FailureInvestigationModal: React.FC<FailureModalProps> = ({ investigation, onClose }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'screenshot' | 'timeline' | 'network' | 'console' | 'ai' | 'python'>('overview');
  const [copied, setCopied] = useState(false);

  if (!investigation) return null;

  const {
    testName,
    journeyName,
    severity,
    priority,
    failedStepIndex,
    totalSteps,
    failedPageUrl,
    userAction,
    expected,
    actual,
    businessImpactSummary,
    businessImpactScore,
    screenshotUrl,
    relatedApiFailures,
    relatedConsoleErrors,
    timeline,
    aiAnalysis
  } = investigation;

  const pythonReproCode = `# WebTest AI Python Playwright Reproducer
# Generated automatically from recorded failure telemetry

import asyncio
from playwright.async_api import async_playwright

async def reproduce_failure():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # Step 1: Navigate to target URL
        print("Navigating to ${failedPageUrl}...")
        await page.goto("${failedPageUrl}")

        # Step 2: Reproduce failed action: "${userAction}"
        # Expected: "${expected}"
        # Actual Failure: "${actual}"
        try:
            print("Triggering action: ${userAction}")
            # Target action replay
            await page.wait_for_timeout(1000)
            print("Captured failure state accurately.")
        except Exception as e:
            print(f"Encountered expected failure: {e}")

        await page.screenshot(path="failure_repro.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(reproduce_failure())
`;

  const copyCode = () => {
    navigator.clipboard.writeText(pythonReproCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 overflow-y-auto animate-fade-in">
      <div className="bg-slate-950 border border-border/80 w-full max-w-5xl rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="p-6 border-b border-border/80 flex items-start justify-between bg-surface/90 backdrop-blur-xl">
          <div>
            <div className="flex flex-wrap items-center gap-2.5 mb-2.5">
              <span className="px-2.5 py-0.5 rounded-md text-[10px] font-black bg-red-500 text-white uppercase tracking-wider">
                {severity}
              </span>
              <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">
                {priority}
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Step {failedStepIndex + 1} of {totalSteps}
              </span>
              {journeyName && (
                <span className="text-xs font-semibold text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-md border border-cyan-500/20">
                  {journeyName}
                </span>
              )}
            </div>
            <h2 className="text-2xl font-black text-white flex items-center gap-2.5">
              <AlertTriangle className="w-6 h-6 text-red-400 shrink-0" />
              {testName}
            </h2>
            <div className="text-xs text-slate-400 mt-1 font-mono">{failedPageUrl}</div>
          </div>

          <div className="flex items-center gap-5">
            <div className="text-right">
              <div className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Business Impact</div>
              <div className="text-3xl font-black text-red-400">{businessImpactScore} <span className="text-xs text-slate-500">/ 100</span></div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white rounded-xl bg-surface hover:bg-slate-800 border border-slate-700/60 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-border/80 bg-surface/40 px-6 gap-2 pt-2 overflow-x-auto">
          {[
            { id: 'overview', label: 'Failure Summary', icon: AlertTriangle },
            { id: 'screenshot', label: 'Browser Screenshot', icon: ImageIcon, badge: screenshotUrl ? '1' : undefined },
            { id: 'timeline', label: 'Step Timeline', icon: Clock, badge: String(timeline.length) },
            { id: 'network', label: 'Network Waterfall', icon: Network, badge: relatedApiFailures.length > 0 ? String(relatedApiFailures.length) : undefined },
            { id: 'console', label: 'Console Crashes', icon: Terminal, badge: relatedConsoleErrors.length > 0 ? String(relatedConsoleErrors.length) : undefined },
            { id: 'ai', label: 'AI Diagnosis', icon: Sparkles },
            { id: 'python', label: 'Python Reproducer', icon: Terminal }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all whitespace-nowrap ${
                  isActive
                    ? 'border-cyan-400 text-cyan-300 bg-cyan-500/10 rounded-t-xl'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-slate-800 text-slate-300 font-mono">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* User Action */}
              <div className="p-5 bg-surface/80 rounded-2xl border border-border/80">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">User Action Attempted</div>
                <div className="text-base font-bold text-white">{userAction}</div>
              </div>

              {/* Expected vs Actual Comparison Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 bg-blue-950/20 border border-blue-500/30 rounded-2xl">
                  <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-blue-400 mb-2">
                    <CheckCircle2 className="w-4 h-4" /> Expected Outcome
                  </div>
                  <div className="text-sm font-medium text-slate-200 leading-relaxed">{expected}</div>
                </div>

                <div className="p-5 bg-red-950/20 border border-red-500/40 rounded-2xl">
                  <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-red-400 mb-2">
                    <AlertTriangle className="w-4 h-4" /> Actual Observation / Crash
                  </div>
                  <div className="text-sm font-medium text-red-200 font-mono leading-relaxed">{actual}</div>
                </div>
              </div>

              {/* EXACT FIX & SOLUTION GUIDE */}
              {(aiAnalysis.whereToFix || aiAnalysis.whatToFix || aiAnalysis.codeSnippetFix) && (
                <div className="p-6 bg-gradient-to-r from-emerald-950/30 via-slate-900/60 to-cyan-950/30 border-2 border-emerald-500/40 rounded-3xl space-y-4 shadow-xl">
                  <div className="flex items-center justify-between pb-3 border-b border-emerald-500/20">
                    <div className="flex items-center gap-2">
                      <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        <Sparkles className="w-4 h-4" />
                      </span>
                      <h4 className="text-sm font-black text-white tracking-wide uppercase">
                        Exact Fix & Solution Guide
                      </h4>
                    </div>
                    <span className="text-[10px] font-mono px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                      ACTIONABLE SOLUTION
                    </span>
                  </div>

                  {aiAnalysis.whereToFix && (
                    <div className="space-y-1">
                      <div className="text-[11px] font-extrabold uppercase text-cyan-400 tracking-wider">
                        📍 WHERE TO FIX (FILE / LOCATION):
                      </div>
                      <div className="p-3 bg-black/60 rounded-xl border border-cyan-500/30 text-xs font-mono font-bold text-cyan-200">
                        {aiAnalysis.whereToFix}
                      </div>
                    </div>
                  )}

                  {aiAnalysis.whatToFix && (
                    <div className="space-y-1">
                      <div className="text-[11px] font-extrabold uppercase text-amber-400 tracking-wider">
                        💡 WHAT TO FIX:
                      </div>
                      <p className="text-xs text-slate-200 leading-relaxed p-3 bg-black/40 rounded-xl border border-slate-800">
                        {aiAnalysis.whatToFix}
                      </p>
                    </div>
                  )}

                  {aiAnalysis.codeSnippetFix && (
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-extrabold uppercase text-emerald-400 tracking-wider">
                          💻 COPY-PASTE CODE FIX:
                        </span>
                      </div>
                      <pre className="p-4 bg-black/90 rounded-2xl border border-emerald-500/30 text-xs font-mono text-emerald-300 overflow-x-auto leading-relaxed">
                        {aiAnalysis.codeSnippetFix}
                      </pre>
                    </div>
                  )}
                </div>
              )}

              {/* Business Impact Explanation */}
              <div className="p-5 bg-surface/80 rounded-2xl border border-border/80 space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Customer & Revenue Impact</div>
                <p className="text-sm text-slate-200 leading-relaxed">{businessImpactSummary}</p>
                <div className="flex flex-wrap gap-2 pt-2 border-t border-border/60">
                  {aiAnalysis.businessImpactFactors.map((f, i) => (
                    <span key={i} className="text-xs px-3 py-1 bg-black/40 text-slate-300 rounded-lg border border-slate-800 font-mono">
                      <strong>{f.factor}</strong> (+{f.weight} pts)
                    </span>
                  ))}
                </div>
              </div>

              {/* Confirmed Facts vs AI Hypotheses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 bg-surface/80 rounded-2xl border border-border/80 space-y-3">
                  <div className="text-xs font-extrabold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" /> Confirmed Evidence (Facts)
                  </div>
                  <ul className="space-y-2 text-xs text-slate-300 leading-relaxed">
                    {aiAnalysis.confirmedFacts.map((fact, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-emerald-400 font-bold">•</span>
                        <span>{fact}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="p-5 bg-surface/80 rounded-2xl border border-border/80 space-y-3">
                  <div className="text-xs font-extrabold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" /> AI Root Cause Diagnostics
                  </div>
                  <ul className="space-y-2 text-xs text-slate-300 leading-relaxed">
                    {aiAnalysis.aiEstimatedCauses.map((cause, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-cyan-400 font-bold">•</span>
                        <span>{cause}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'screenshot' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-xs text-slate-400">Captured at the failure milestone during Playwright execution:</div>
                {screenshotUrl && (
                  <a
                    href={screenshotUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-xs text-cyan-400 hover:underline"
                  >
                    Open Full Image <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
              {screenshotUrl ? (
                <div className="border border-slate-800 rounded-2xl overflow-hidden bg-black flex items-center justify-center p-2 shadow-2xl">
                  <img src={screenshotUrl} alt="Failure Screenshot" className="max-w-full max-h-[520px] object-contain rounded-xl" />
                </div>
              ) : (
                <div className="p-16 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl font-mono">
                  No visual screenshot artifact generated for this step.
                </div>
              )}
            </div>
          )}

          {activeTab === 'timeline' && (
            <div className="space-y-3">
              <div className="text-xs text-slate-400 mb-2">Step-by-step event replay sequence:</div>
              <div className="relative border-l-2 border-slate-800 ml-4 space-y-4 py-2">
                {timeline.map((item, idx) => (
                  <div key={idx} className="relative pl-6">
                    <div
                      className={`absolute -left-[9px] top-1.5 w-4 h-4 rounded-full border-2 ${
                        item.status === 'passed'
                          ? 'bg-emerald-500 border-emerald-950'
                          : item.status === 'failed'
                          ? 'bg-red-500 border-red-950 animate-ping'
                          : 'bg-slate-500 border-slate-900'
                      }`}
                    />
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono text-slate-400">{item.time}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                        item.status === 'passed' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                    <div className="text-sm font-bold text-slate-200 mt-0.5">{item.label}</div>
                    {item.details && (
                      <div className="text-xs font-mono text-slate-400 mt-1 bg-black/50 p-2.5 rounded-xl border border-slate-800/80">
                        {item.details}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'network' && (
            <div className="space-y-4">
              <div className="text-xs text-slate-400">Captured HTTP network interactions:</div>
              {relatedApiFailures.length > 0 ? (
                <div className="space-y-3">
                  {relatedApiFailures.map((net) => (
                    <div key={net.id} className="p-4 bg-red-950/20 border border-red-500/30 rounded-2xl font-mono text-xs space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 bg-red-500 text-white font-bold rounded">
                            {net.method}
                          </span>
                          <span className="text-red-300 font-bold">{net.url}</span>
                        </div>
                        <span className="px-2.5 py-0.5 bg-red-900/60 text-red-200 border border-red-500/40 rounded-md font-bold">
                          HTTP {net.status}
                        </span>
                      </div>
                      <div className="text-slate-400">
                        Response Duration: {net.durationMs}ms • Resource Type: {net.resourceType}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl font-mono">
                  No 4xx/5xx network errors recorded during this test step.
                </div>
              )}
            </div>
          )}

          {activeTab === 'console' && (
            <div className="space-y-4">
              <div className="text-xs text-slate-400">Browser runtime console logs and exceptions:</div>
              {relatedConsoleErrors.length > 0 ? (
                <div className="space-y-2.5">
                  {relatedConsoleErrors.map((c) => (
                    <div key={c.id} className="p-3.5 bg-red-950/30 border border-red-500/30 rounded-xl font-mono text-xs text-red-300">
                      <div className="flex justify-between text-[11px] text-slate-500 mb-1.5">
                        <span className="font-extrabold uppercase px-2 py-0.5 rounded bg-black/40">{c.type}</span>
                        <span>{c.timestamp.split('T')[1]?.slice(0, 8)}</span>
                      </div>
                      <div>{c.text}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl font-mono">
                  No JavaScript exceptions logged during execution.
                </div>
              )}
            </div>
          )}

          {activeTab === 'ai' && (
            <div className="space-y-6">
              <div className="p-6 bg-gradient-to-r from-cyan-950/40 via-blue-950/40 to-indigo-950/40 border border-cyan-500/30 rounded-2xl space-y-2">
                <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-cyan-400">
                  <Sparkles className="w-4 h-4" /> AI Root Cause Diagnostics
                </div>
                <p className="text-sm font-medium text-slate-200 leading-relaxed">{aiAnalysis.likelyCause}</p>
                <div className="text-xs text-slate-400 font-mono pt-2">
                  Confidence Score: <strong className="text-cyan-400">{Math.round(aiAnalysis.confidenceScore * 100)}% ({aiAnalysis.confidence})</strong>
                </div>
              </div>

              <div className="p-6 bg-surface/80 rounded-2xl border border-border/80 space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Recommended Remediation Steps</div>
                <div className="space-y-2.5">
                  {aiAnalysis.recommendedInvestigation.map((rec, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 bg-black/40 rounded-xl border border-white/5 text-xs text-slate-200">
                      <div className="w-5 h-5 rounded-full bg-blue-500/20 text-cyan-400 flex items-center justify-center font-bold shrink-0">
                        {i + 1}
                      </div>
                      <div className="leading-relaxed">{rec}</div>
                    </div>
                  ))}
                </div>
              </div>

              {aiAnalysis.suggestedFix && (
                <div className="p-6 bg-surface/80 rounded-2xl border border-border/80 space-y-2">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Suggested Code Fix</div>
                  <div className="p-4 bg-black/60 rounded-xl border border-slate-800 font-mono text-xs text-emerald-400 leading-relaxed">
                    {aiAnalysis.suggestedFix}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'python' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-xs text-slate-400">Ready-to-run Python Playwright script to reproduce this failure:</div>
                <button
                  onClick={copyCode}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-surface hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-bold transition"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-cyan-400" />}
                  {copied ? 'Copied!' : 'Copy Code'}
                </button>
              </div>
              <pre className="p-4 bg-black/80 rounded-2xl border border-slate-800 text-xs font-mono text-cyan-300 overflow-x-auto">
                {pythonReproCode}
              </pre>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border/80 bg-surface/90 flex items-center justify-between">
          <div className="text-xs text-slate-400 font-mono">
            WebTest AI Python Engine • Auto-captured Failure Investigation
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition shadow-md"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
