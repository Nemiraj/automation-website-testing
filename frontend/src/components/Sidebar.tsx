import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderKanban, 
  PlayCircle, 
  AlertTriangle, 
  Settings as SettingsIcon,
  Sparkles
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Start Test', href: '/new-test', icon: PlayCircle },
  { name: 'Settings', href: '/settings', icon: SettingsIcon },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-slate-800/80 bg-slate-950 p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Navigation
          </p>
          <nav className="mt-2 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-slate-900 text-emerald-400 border border-slate-800'
                        : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-gradient-to-b from-slate-900/90 to-slate-950 p-3.5">
          <div className="flex items-center gap-2 text-emerald-400 mb-1.5">
            <Sparkles className="h-4 w-4" />
            <span className="text-xs font-semibold">AI Auditor Active</span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-400">
            Deterministic Playwright metrics are synthesized into actionable developer fixes with root-cause explanations.
          </p>
        </div>
      </div>

      <div className="border-t border-slate-800/80 pt-4 text-[11px] text-slate-400">
        <p>SiteAutoTest Platform v1.0</p>
        <p className="text-slate-400 mt-0.5">Automated Multi-Device QA</p>
      </div>
    </aside>
  );
};
