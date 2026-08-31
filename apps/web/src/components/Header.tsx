import React from 'react';
import { Play, Search, Globe, ShieldCheck, Sparkles, Terminal, Activity } from 'lucide-react';
import { BrowserType, EnvironmentType } from '@webtest/shared';

interface HeaderProps {
  websiteUrl: string;
  setWebsiteUrl: (url: string) => void;
  environment: EnvironmentType;
  setEnvironment: (env: EnvironmentType) => void;
  browser: BrowserType;
  setBrowser: (b: BrowserType) => void;
  isRunning: boolean;
  isScanning: boolean;
  onScan: () => void;
  onRunTests: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  websiteUrl,
  setWebsiteUrl,
  environment,
  setEnvironment,
  browser,
  setBrowser,
  isRunning,
  isScanning,
  onScan,
  onRunTests
}) => {
  const presets = [
    { label: 'NovaStore Sandbox', url: 'http://localhost:3001' },
    { label: 'Cinema / Media Demo', url: 'http://localhost:3001/products' },
  ];

  return (
    <header className="h-16 border-b border-border/80 bg-surface/90 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xl">
      <div className="flex items-center gap-5">
        {/* Brand Logo & Engine Indicator */}
        <div className="flex items-center gap-3">
          <div className="relative group cursor-pointer">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 via-indigo-500 to-cyan-400 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
            <div className="relative w-9 h-9 rounded-xl bg-slate-950 border border-white/10 flex items-center justify-center text-white shadow-xl">
              <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                WebTest AI
              </span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                Python 3.x Engine
              </span>
            </div>
            <div className="text-[10px] text-slate-400 font-medium">Autonomous QA & Self-Healing Diagnostics</div>
          </div>
        </div>

        <div className="h-6 w-[1px] bg-border/60" />

        {/* Environment Switcher */}
        <div className="flex items-center bg-black/40 rounded-lg p-1 border border-border/60">
          {(['local', 'staging', 'production'] as EnvironmentType[]).map((env) => (
            <button
              key={env}
              onClick={() => setEnvironment(env)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md capitalize transition-all duration-200 ${
                environment === env
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`}
            >
              {env}
            </button>
          ))}
        </div>

        {/* Website URL Input with quick presets */}
        <div className="relative flex items-center w-84">
          <Globe className="w-4 h-4 text-cyan-400 absolute left-3 pointer-events-none" />
          <input
            type="text"
            value={websiteUrl}
            onChange={(e) => setWebsiteUrl(e.target.value)}
            placeholder="http://localhost:3001"
            className="w-full bg-black/50 border border-border/80 rounded-xl pl-9 pr-24 py-1.5 text-xs font-mono text-cyan-200 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition"
          />
          <div className="absolute right-1 flex items-center gap-1">
            {presets.map((p) => (
              <button
                key={p.label}
                onClick={() => setWebsiteUrl(p.url)}
                title={p.url}
                className="px-2 py-0.5 rounded text-[10px] bg-surface hover:bg-slate-800 text-slate-300 border border-slate-700 transition"
              >
                {p.label.split(' ')[0]}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Browser Selector */}
        <div className="flex items-center bg-black/40 rounded-xl border border-border/60 p-1">
          {(['chromium', 'firefox', 'webkit'] as BrowserType[]).map((b) => (
            <button
              key={b}
              onClick={() => setBrowser(b)}
              className={`px-2.5 py-1 text-xs font-medium rounded-lg capitalize transition-all ${
                browser === b
                  ? 'bg-slate-800 text-cyan-300 font-bold border border-slate-700 shadow-inner'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {b}
            </button>
          ))}
        </div>

        {/* Scan Website Button */}
        <button
          onClick={onScan}
          disabled={isScanning || isRunning}
          className="flex items-center gap-2 px-3.5 py-2 bg-surface hover:bg-slate-800 border border-slate-700/80 hover:border-slate-500 text-slate-200 rounded-xl text-xs font-semibold transition-all shadow-md active:scale-95 disabled:opacity-50"
        >
          <Search className={`w-3.5 h-3.5 text-cyan-400 ${isScanning ? 'animate-spin' : ''}`} />
          {isScanning ? 'Scanning Architecture...' : 'Scan Website'}
        </button>

        {/* Run Tests Button */}
        <button
          onClick={onRunTests}
          disabled={isRunning || isScanning}
          className="relative group overflow-hidden rounded-xl p-[1px] disabled:opacity-50 active:scale-95 transition"
        >
          <span className="absolute inset-0 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 rounded-xl group-hover:opacity-90 transition"></span>
          <span className="relative flex items-center gap-2 px-4 py-2 bg-slate-950/40 rounded-xl text-white text-xs font-extrabold shadow-lg">
            <Play className={`w-3.5 h-3.5 fill-current text-cyan-300 ${isRunning ? 'animate-pulse' : ''}`} />
            {isRunning ? 'Running Real Browser...' : 'Run Autonomous Tests'}
          </span>
        </button>
      </div>
    </header>
  );
};
