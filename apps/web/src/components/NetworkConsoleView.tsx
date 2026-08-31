import React, { useState } from 'react';
import { Network, Terminal, Filter, CheckCircle2, AlertTriangle, XCircle, Search, Server } from 'lucide-react';
import { ConsoleEvent, NetworkEvent } from '@webtest/shared';

interface NetworkConsoleViewProps {
  networkEvents: NetworkEvent[];
  consoleEvents: ConsoleEvent[];
}

export const NetworkConsoleView: React.FC<NetworkConsoleViewProps> = ({ networkEvents, consoleEvents }) => {
  const [tab, setTab] = useState<'network' | 'console'>('network');
  const [filter, setFilter] = useState<'all' | 'errors'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredNetwork = networkEvents
    .filter(n => filter === 'all' ? true : (n.status >= 400 || n.isFailed))
    .filter(n => searchQuery ? n.url.toLowerCase().includes(searchQuery.toLowerCase()) : true);

  const filteredConsole = consoleEvents
    .filter(c => filter === 'all' ? true : c.type === 'error')
    .filter(c => searchQuery ? c.text.toLowerCase().includes(searchQuery.toLowerCase()) : true);

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-500/10 text-cyan-400 border border-blue-500/20">
              {tab === 'network' ? <Network className="w-4 h-4" /> : <Terminal className="w-4 h-4" />}
            </span>
            <h2 className="text-2xl font-black text-white tracking-tight">
              {tab === 'network' ? 'Network Waterfall & API Telemetry' : 'Browser Runtime Console & Exception Logs'}
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time telemetry intercepted directly from the Python Playwright execution session.
          </p>
        </div>

        {/* Tab Switcher & Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex bg-black/40 border border-border/80 rounded-xl p-1">
            <button
              onClick={() => setTab('network')}
              className={`px-3.5 py-1.5 text-xs font-bold rounded-lg transition ${
                tab === 'network' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              Network ({networkEvents.length})
            </button>
            <button
              onClick={() => setTab('console')}
              className={`px-3.5 py-1.5 text-xs font-bold rounded-lg transition ${
                tab === 'console' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              Console ({consoleEvents.length})
            </button>
          </div>

          <button
            onClick={() => setFilter(filter === 'all' ? 'errors' : 'all')}
            className={`px-3.5 py-1.5 text-xs font-bold rounded-xl border flex items-center gap-1.5 transition ${
              filter === 'errors'
                ? 'bg-red-500/20 text-red-400 border-red-500/40'
                : 'bg-surface hover:bg-slate-800 text-slate-300 border-slate-700'
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            {filter === 'errors' ? 'Errors Only' : 'Show All'}
          </button>
        </div>
      </div>

      {tab === 'network' ? (
        <div className="bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950/80 text-slate-400 border-b border-border/80 uppercase">
                <tr>
                  <th className="p-4">Method</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Target API URL</th>
                  <th className="p-4">Type</th>
                  <th className="p-4">Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filteredNetwork.map((net) => {
                  const isErr = net.status >= 400 || net.isFailed;
                  return (
                    <tr key={net.id} className={`hover:bg-slate-800/40 transition ${isErr ? 'bg-red-950/20' : ''}`}>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded-md font-bold text-[10px] ${
                          net.method === 'POST' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        }`}>
                          {net.method}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded-md font-bold text-[10px] ${
                          isErr ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        }`}>
                          HTTP {net.status || 'FAILED'}
                        </span>
                      </td>
                      <td className="p-4 text-slate-200 truncate max-w-md font-medium">{net.url}</td>
                      <td className="p-4 text-slate-400 capitalize">{net.resourceType}</td>
                      <td className="p-4 text-slate-400">{net.durationMs}ms</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl p-6 space-y-3 shadow-xl">
          {filteredConsole.map((c) => {
            const isErr = c.type === 'error';
            return (
              <div
                key={c.id}
                className={`p-4 rounded-2xl font-mono text-xs border ${
                  isErr ? 'bg-red-950/20 border-red-500/40 text-red-200' : 'bg-slate-900/60 border-slate-800 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] text-slate-500 mb-1.5">
                  <span className="font-extrabold uppercase px-2 py-0.5 rounded bg-black/40">{c.type}</span>
                  <span>{c.timestamp.split('T')[1]?.slice(0, 8)}</span>
                </div>
                <div className="leading-relaxed">{c.text}</div>
                {c.location && <div className="text-[10px] text-slate-500 mt-1.5 underline">{c.location}</div>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
