import React from 'react';
import { Play, Sparkles, Globe, Monitor, Search, Layers, ShieldCheck, Flame, Compass, RefreshCw, Cpu } from 'lucide-react';
import { BrowserType, EnvironmentType } from '../types';

interface HeaderProps {
  websiteUrl: string;
  setWebsiteUrl: (url: string) => void;
  environment: EnvironmentType;
  setEnvironment: (env: EnvironmentType) => void;
  browser: BrowserType;
  setBrowser: (browser: BrowserType) => void;
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
  const PRESET_URLS = [
    { label: 'XAMPP Localhost', url: 'http://localhost/' },
    { label: 'NovaStore Sandbox', url: 'http://localhost:3001' },
    { label: 'Cinema & Media Demo', url: 'http://localhost:3001/movies' },
  ];

  return (
    <header className="sticky top-0 z-40 bg-surface/90 backdrop-blur-xl border-b border-border/80 px-6 py-3.5 shadow-2xl transition-all duration-300">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        
        {/* Brand & AI Engine Indicator */}
        <div className="flex items-center gap-3">
          <div className="relative group">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 p-[2px] shadow-lg shadow-blue-500/25 transition-transform group-hover:scale-105 duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse" />
              </div>
            </div>
            <span className="absolute -bottom-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                WebTest AI
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-gradient-to-r from-blue-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm flex items-center gap-1">
                <Cpu className="w-3 h-3 text-cyan-400" /> Python 3.x Engine
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Autonomous QA & Self-Healing Playwright Synthesizer</p>
          </div>
        </div>

        {/* Target URL & Presets */}
        <div className="flex-1 max-w-2xl flex items-center gap-2">
          <div className="relative flex-1 group">
            <Globe className="w-4 h-4 text-cyan-400 absolute left-3.5 top-1/2 -translate-y-1/2 transition group-hover:text-cyan-300" />
            <input
              type="text"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              placeholder="https://your-website.com"
              className="w-full bg-slate-900/90 border border-slate-700/80 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 rounded-2xl pl-10 pr-4 py-2 text-xs font-mono text-slate-100 placeholder-slate-500 outline-none transition-all shadow-inner"
            />
          </div>

          <div className="hidden sm:flex items-center gap-1.5">
            {PRESET_URLS.map((preset) => (
              <button
                key={preset.url}
                onClick={() => setWebsiteUrl(preset.url)}
                className={`px-3 py-1.5 rounded-xl text-[11px] font-bold transition-all border ${
                  websiteUrl === preset.url
                    ? 'bg-blue-500/15 border-blue-500/40 text-cyan-300 shadow-sm'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* Environment, Browser, & Primary Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Environment Selector */}
          <div className="flex items-center bg-slate-900/80 border border-slate-800 rounded-xl p-1 shadow-inner">
            {(['local', 'staging', 'production'] as EnvironmentType[]).map((env) => (
              <button
                key={env}
                onClick={() => setEnvironment(env)}
                className={`px-2.5 py-1 text-[10px] font-bold rounded-lg uppercase tracking-wider transition-all ${
                  environment === env
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {env}
              </button>
            ))}
          </div>

          {/* Browser Selector */}
          <div className="flex items-center bg-slate-900/80 border border-slate-800 rounded-xl p-1 shadow-inner">
            {(['chromium', 'firefox', 'webkit'] as BrowserType[]).map((b) => (
              <button
                key={b}
                onClick={() => setBrowser(b)}
                className={`px-2.5 py-1 text-[10px] font-bold rounded-lg uppercase tracking-wider transition-all ${
                  browser === b
                    ? 'bg-gradient-to-r from-indigo-600 to-cyan-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {b}
              </button>
            ))}
          </div>

          {/* Action 1: Discovery Scan */}
          <button
            onClick={onScan}
            disabled={isScanning || isRunning}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all duration-300 flex items-center gap-2 border shadow-lg ${
              isScanning
                ? 'bg-slate-800/80 text-slate-400 border-slate-700 cursor-not-allowed'
                : 'bg-slate-900 hover:bg-slate-800 text-cyan-300 border-cyan-500/30 hover:border-cyan-400 shadow-cyan-500/10 active:scale-95'
            }`}
          >
            <Search className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : 'text-cyan-400'}`} />
            <span>{isScanning ? 'Scanning...' : 'Scan Architecture'}</span>
          </button>

          {/* Action 2: Run Tests */}
          <button
            onClick={onRunTests}
            disabled={isRunning || isScanning}
            className={`px-5 py-2 rounded-xl text-xs font-black transition-all duration-300 flex items-center gap-2 shadow-xl ${
              isRunning
                ? 'bg-blue-600/50 text-white border border-blue-400/30 cursor-not-allowed animate-pulse'
                : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-blue-500/30 hover:shadow-blue-500/50 active:scale-95'
            }`}
          >
            <Play className={`w-3.5 h-3.5 fill-current ${isRunning ? 'animate-spin' : ''}`} />
            <span>{isRunning ? 'Running Python Tests...' : 'Run Autonomous Tests'}</span>
          </button>
        </div>

      </div>
    </header>
  );
};
