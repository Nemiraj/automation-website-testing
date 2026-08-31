import React from 'react';
import {
  LayoutDashboard,
  FileSpreadsheet,
  Compass,
  FileCode,
  AlertTriangle,
  PlayCircle,
  Network,
  Terminal,
  FileCheck2,
  FileText,
  Settings,
  Sparkles,
  Layers,
  Activity,
  Cpu
} from 'lucide-react';

export type NavItem =
  | 'dashboard'
  | 'forms'
  | 'journeys'
  | 'pages'
  | 'failures'
  | 'runs'
  | 'network'
  | 'console'
  | 'tests'
  | 'reports'
  | 'performance'
  | 'ai'
  | 'settings';

interface SidebarProps {
  activeNav: NavItem;
  setActiveNav: (nav: NavItem) => void;
  criticalCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeNav, setActiveNav, criticalCount }) => {
  const navSections = [
    {
      title: 'Testing & Execution',
      items: [
        { id: 'dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
        { id: 'forms', label: 'Form Testing & Fuzzing', icon: FileSpreadsheet },
        { id: 'runs', label: 'Test Runs & Regressions', icon: PlayCircle },
        { id: 'journeys', label: 'User Journeys Matrix', icon: Compass },
        { id: 'tests', label: 'Synthesized Test Cases', icon: FileCheck2 },
        { id: 'pages', label: 'Site Map Architecture', icon: FileCode },
      ]
    },
    {
      title: 'Diagnostics & Telemetry',
      items: [
        {
          id: 'failures',
          label: 'Critical Failures',
          icon: AlertTriangle,
          badge: criticalCount > 0 ? String(criticalCount) : undefined,
          isDanger: criticalCount > 0
        },
        { id: 'network', label: 'Network & API Waterfall', icon: Network },
        { id: 'console', label: 'Browser Console & Crashes', icon: Terminal },
        { id: 'performance', label: 'Page Speed & Vitals', icon: Activity },
      ]
    },
    {
      title: 'Intelligence & Exports',
      items: [
        { id: 'ai', label: 'AI Root Cause Diagnoser', icon: Sparkles },
        { id: 'reports', label: 'Executive QA Reports', icon: FileText },
        { id: 'settings', label: 'Engine Configuration', icon: Settings },
      ]
    }
  ];

  return (
    <aside className="w-72 bg-surface/95 backdrop-blur-xl border-r border-border/80 flex flex-col justify-between p-4 shrink-0 select-none shadow-2xl">
      <div className="space-y-6">
        {navSections.map((section, sIdx) => (
          <div key={sIdx} className="space-y-1.5">
            <div className="px-3 text-[10px] font-black uppercase tracking-wider text-slate-500">
              {section.title}
            </div>

            <div className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeNav === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveNav(item.id as NavItem)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-2xl text-xs font-bold transition-all duration-200 group ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-600/20 via-indigo-600/20 to-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-lg shadow-blue-500/10'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-1.5 rounded-xl transition-colors ${
                        isActive
                          ? 'bg-blue-500/20 text-cyan-300'
                          : 'bg-slate-900 text-slate-400 group-hover:text-slate-200'
                      }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <span className="truncate">{item.label}</span>
                    </div>

                    {item.badge && (
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-black tracking-wide ${
                          item.isDanger
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer Status Panel */}
      <div className="pt-4 border-t border-border/80">
        <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-[11px] font-bold text-slate-200">Playwright Python</span>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
              READY
            </span>
          </div>
          <div className="text-[10px] text-slate-500 font-mono flex items-center justify-between">
            <span>FastAPI Server</span>
            <span className="text-slate-400">Port 4000</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
