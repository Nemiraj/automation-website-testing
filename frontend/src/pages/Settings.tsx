import React from 'react';
import { Settings as SettingsIcon, Shield, Database, Cpu, HardDrive } from 'lucide-react';

export const Settings: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Platform Settings & Security</h1>
        <p className="text-xs text-slate-400 mt-1">
          Review system boundaries, SSRF safeguards, database connection, and AI engine status.
        </p>
      </div>

      <div className="space-y-6">
        {/* Security & SSRF Safeguards */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-2 text-emerald-400">
            <Shield className="h-5 w-5" />
            <h2 className="text-sm font-bold text-white">SSRF & Network Boundary Protection</h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            The platform enforces DNS rebinding protection and prevents scanning internal IP addresses (RFC 1918), localhost loopbacks, and cloud metadata endpoints.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-2">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 space-y-1">
              <span className="font-semibold text-slate-300">Internal Network Blocking</span>
              <p className="text-[11px] text-emerald-400 font-mono">ENABLED (127.0.0.1, 10.0.0.0/8, 192.168.0.0/16)</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 space-y-1">
              <span className="font-semibold text-slate-300">Form Safety Mode</span>
              <p className="text-[11px] text-emerald-400 font-mono">VALIDATION_ONLY (No unconfirmed submissions)</p>
            </div>
          </div>
        </div>

        {/* Engine Specs */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-2 text-emerald-400">
            <Cpu className="h-5 w-5" />
            <h2 className="text-sm font-bold text-white">Testing Engines & Capabilities</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 space-y-1">
              <span className="font-semibold text-slate-300">Browser Automation</span>
              <p className="text-[11px] text-slate-400">Playwright Chromium (Headless)</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 space-y-1">
              <span className="font-semibold text-slate-300">AI Diagnostic Model</span>
              <p className="text-[11px] text-slate-400">Gemini 1.5 Pro / Expert Synthesizer</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 space-y-1">
              <span className="font-semibold text-slate-300">Visual Regression</span>
              <p className="text-[11px] text-slate-400">Pillow RGBA Pixel Difference</p>
            </div>
          </div>
        </div>

        {/* Storage */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-2 text-emerald-400">
            <HardDrive className="h-5 w-5" />
            <h2 className="text-sm font-bold text-white">Storage & Persistence</h2>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Screenshots and regression diff masks are persisted locally under <code className="font-mono text-slate-300">./storage/screenshots/</code> and served via high-speed static mount.
          </p>
        </div>
      </div>
    </div>
  );
};
