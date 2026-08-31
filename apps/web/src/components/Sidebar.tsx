import React from 'react';
import {
  LayoutDashboard,
  PlayCircle,
  Compass,
  FileCheck2,
  FileCode,
  Network,
  Terminal,
  AlertOctagon,
  Activity,
  Sparkles,
  FileText,
  Settings,
  Cpu
} from 'lucide-react';

export type NavItem =
  | 'dashboard'
  | 'runs'
  | 'journeys'
  | 'tests'
  | 'pages'
  | 'network'
  | 'console'
  | 'failures'
  | 'performance'
  | 'ai'
  | 'reports'
  | 'settings';

interface SidebarProps {
  activeNav: NavItem;
  setActiveNav: (nav: NavItem) => void;
  criticalCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeNav, setActiveNav, criticalCount }) => {
  const sections = [
    {
      title: 'Testing & Execution',
      items: [
        { id: 'dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
        { id: 'runs', label: 'Test Runs & Regressions', icon: PlayCircle },
        { id: 'journeys', label: 'User Journeys Matrix', icon: Compass },
        { id: 'tests', label: 'Synthesized Test Cases', icon: FileCheck2 },
        { id: 'pages', label: 'Site Map Architecture', icon: FileCode },
      ]
    },
    {
      title: 'Diagnostics & Telemetry',
      items: [
        { id: 'failures', label: 'Critical Failures', icon: AlertOctagon, badge: criticalCount > 0 ? criticalCount : undefined },
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
    <aside className="w-64 border-r border-border/80 bg-surface/80 backdrop-blur-xl flex flex-col justify-between p-4 h-[calc(100vh-4rem)] select-none shadow-xl">
      <div className="overflow-y-auto space-y-6 pr-1">
        {sections.map((sec, sIdx) => (
          <div key={sIdx}>
            <div className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500 px-3 mb-2">
              {sec.title}
            </div>
            <nav className="space-y-1">
              {sec.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeNav === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveNav(item.id as NavItem)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-200 group ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-600/30 to-indigo-600/10 text-cyan-300 border border-blue-500/40 shadow-lg shadow-blue-500/10'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge !== undefined && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-500/30 text-red-300 border border-red-500/40 animate-pulse">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Engine Status Footer */}
      <div className="p-3 bg-slate-950/60 rounded-2xl border border-white/5 text-[11px] text-slate-400 shadow-inner">
        <div className="flex items-center justify-between text-slate-200 font-bold mb-1">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Python Playwright</span>
          </div>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono">ONLINE</span>
        </div>
        <div className="text-[10px] text-slate-500">Port 4000 • Autonomous Self-Healing</div>
      </div>
    </aside>
  );
};
