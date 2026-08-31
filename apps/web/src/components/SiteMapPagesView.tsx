import React from 'react';
import { FileCode, Globe, CheckCircle2, AlertTriangle, ArrowUpRight, Layers, Sparkles, Search } from 'lucide-react';
import { PageInfo, ScanResult } from '@webtest/shared';

interface SiteMapPagesViewProps {
  scanResult: ScanResult | null;
  onScanWebsite: () => void;
  isScanning: boolean;
}

export const SiteMapPagesView: React.FC<SiteMapPagesViewProps> = ({ scanResult, onScanWebsite, isScanning }) => {
  if (!scanResult) {
    return (
      <div className="py-20 text-center max-w-md mx-auto space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mx-auto text-cyan-400">
          <FileCode className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h3 className="text-xl font-extrabold text-white">No Website Scan Available</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Run an autonomous discovery scan to map out pages, forms, interactive buttons, inputs, and navigation links with accessibility tree evaluation.
          </p>
        </div>
        <button
          onClick={onScanWebsite}
          disabled={isScanning}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-black shadow-xl shadow-blue-500/20 transition flex items-center gap-2 mx-auto"
        >
          <Search className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
          {isScanning ? 'Scanning Architecture...' : 'Scan Website Now'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-500/10 text-cyan-400 border border-blue-500/20">
              <FileCode className="w-4 h-4" />
            </span>
            <h2 className="text-2xl font-black text-white tracking-tight">
              Website Structure & Discovered Pages
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Autonomous crawler mapped <strong>{scanResult.totalPages} pages</strong> with <strong>{scanResult.totalLinks} links</strong>, <strong>{scanResult.totalForms} forms</strong>, and <strong>{scanResult.totalButtons} interactive buttons</strong>.
          </p>
        </div>

        <button
          onClick={onScanWebsite}
          disabled={isScanning}
          className="px-4 py-2 bg-surface hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-bold transition flex items-center gap-2 self-start"
        >
          <Search className={`w-3.5 h-3.5 text-cyan-400 ${isScanning ? 'animate-spin' : ''}`} />
          {isScanning ? 'Re-scanning...' : 'Re-scan Target'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {scanResult.pages.map((page) => {
          const isHealthy = page.healthStatus === 'HEALTHY';
          return (
            <div
              key={page.id}
              className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl space-y-5 hover:border-slate-600 transition shadow-xl group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`px-2.5 py-0.5 rounded-md text-[10px] font-black uppercase ${
                        isHealthy
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {page.healthStatus}
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      HTTP {page.statusCode} • {page.loadTimeMs}ms
                    </span>
                  </div>
                  <h4 className="text-lg font-extrabold text-white group-hover:text-cyan-300 transition">
                    {page.title}
                  </h4>
                  <a
                    href={page.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1 mt-1 underline decoration-cyan-500/30"
                  >
                    {page.path} <ArrowUpRight className="w-3 h-3" />
                  </a>
                </div>
              </div>

              {/* Elements Count Metric Grid */}
              <div className="grid grid-cols-4 gap-2.5 pt-4 border-t border-border/60 text-center">
                <div className="p-3 bg-black/40 border border-white/5 rounded-2xl">
                  <div className="text-base font-black text-white">{page.buttonsCount}</div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold mt-0.5">Buttons</div>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-2xl">
                  <div className="text-base font-black text-white">{page.formsCount}</div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold mt-0.5">Forms</div>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-2xl">
                  <div className="text-base font-black text-white">{page.inputsCount}</div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold mt-0.5">Inputs</div>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-2xl">
                  <div className="text-base font-black text-white">{page.internalLinks.length}</div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold mt-0.5">Links</div>
                </div>
              </div>

              {/* Quick Links Preview */}
              {page.internalLinks.length > 0 && (
                <div className="space-y-1.5">
                  <div className="text-[10px] uppercase tracking-wider font-extrabold text-slate-500">
                    Discovered Navigation Targets:
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {page.internalLinks.slice(0, 4).map((link, lIdx) => (
                      <span
                        key={lIdx}
                        className="text-[10px] px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-slate-300 font-mono"
                      >
                        {new URL(link, 'http://localhost').pathname}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
