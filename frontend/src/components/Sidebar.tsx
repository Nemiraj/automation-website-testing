import React from 'react';
import { NavLink, useLocation, Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderKanban, 
  PlayCircle, 
  Settings as SettingsIcon,
  Sparkles,
  Zap,
  Bot,
  AlertTriangle,
  FileText,
  Smartphone,
  Layers,
  CheckCircle2
} from 'lucide-react';

const mainNavigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Start New Test', href: '/new-test', icon: PlayCircle },
  { name: 'Settings', href: '/settings', icon: SettingsIcon },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const reportMatch = location.pathname.match(/\/tests\/([^/]+)\/report/);
  const testId = reportMatch ? reportMatch[1] : null;
  const currentTab = new URLSearchParams(location.search).get('tab') || 'overview';

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-slate-950 p-4 flex flex-col justify-between hidden md:flex h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto flex-shrink-0 z-30">
      <div className="space-y-6">
        {/* Main Platform Navigation */}
        <div>
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Main Menu
          </p>
          <nav className="mt-2 space-y-1">
            {mainNavigation.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `flex items-center justify-between rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                      isActive && !testId
                        ? 'bg-slate-900 text-emerald-400 border border-slate-800 font-semibold'
                        : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    <Icon className="h-4 w-4 flex-shrink-0 text-slate-400" />
                    <span>{item.name}</span>
                  </div>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Dedicated AI Readiness Suite Section */}
        <div className="pt-2 border-t border-slate-800/80">
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-teal-400 flex items-center justify-between">
            <span>AI Readiness Suite</span>
            <span className="text-[9px] bg-teal-500/20 text-teal-300 px-1.5 py-0.5 rounded font-mono font-bold border border-teal-500/30">
              NEW
            </span>
          </p>
          <nav className="mt-2 space-y-1">
            <NavLink
              to="/ai-readiness"
              className={({ isActive }) =>
                `flex items-center justify-between rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-teal-500/10 text-teal-300 border border-teal-500/30 font-semibold'
                    : 'text-slate-300 hover:bg-slate-900 hover:text-white'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Bot className="h-4 w-4 text-teal-400 flex-shrink-0" />
                <span>AI Readiness Checker</span>
              </div>
            </NavLink>
          </nav>
        </div>

        {/* Dynamic Active Audit Report Navigation (when viewing a report) */}
        {testId && (
          <div className="space-y-2 pt-2 border-t border-slate-800/80 animate-in fade-in duration-200">
            <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-emerald-400 flex items-center justify-between">
              <span>Active Audit Report</span>
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            </p>
            <nav className="space-y-0.5">
              {[
                { name: 'Executive Overview', tab: 'overview', icon: Layers },
                { name: 'Action Plan & Solutions', tab: 'solutions', icon: Zap, highlight: true },
                { name: 'AI Readiness Audit', tab: 'ai_readiness', icon: Bot, highlight: true },
                { name: 'Detected Issues', tab: 'issues', icon: AlertTriangle },
                { name: 'Scanned Pages', tab: 'pages', icon: FileText },
                { name: 'Device Screenshots', tab: 'responsive', icon: Smartphone },
                { name: 'Form Diagnostics', tab: 'forms', icon: CheckCircle2 },
              ].map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.tab;
                return (
                  <Link
                    key={item.tab}
                    to={`/tests/${testId}/report?tab=${item.tab}`}
                    className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-slate-900 text-emerald-400 border border-emerald-500/30 font-semibold'
                        : item.highlight
                        ? 'text-amber-300 hover:bg-slate-900/60 hover:text-white'
                        : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                    }`}
                  >
                    <Icon className={`h-3.5 w-3.5 flex-shrink-0 ${
                      item.tab === 'solutions' ? 'text-amber-400' :
                      item.tab === 'ai_readiness' ? 'text-teal-400' :
                      isActive ? 'text-emerald-400' : 'text-slate-500'
                    }`} />
                    <span className="truncate">{item.name}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        )}

        {/* AI & Automation Status Card */}
        <div className="rounded-xl border border-slate-800/80 bg-gradient-to-b from-slate-900/90 to-slate-950 p-3.5">
          <div className="flex items-center gap-2 text-emerald-400 mb-1.5">
            <Sparkles className="h-4 w-4 flex-shrink-0" />
            <span className="text-xs font-semibold">AI Readiness Engine</span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-400">
            Deterministic Playwright metrics, Schema.org validation, and root-cause fix plans active.
          </p>
        </div>
      </div>

      <div className="border-t border-slate-800/80 pt-4 text-[11px] text-slate-500">
        <p className="text-slate-400 font-semibold">SiteAutoTest QA</p>
        <p className="text-slate-600 mt-0.5">Live & Localhost Architecture</p>
      </div>
    </aside>
  );
};
