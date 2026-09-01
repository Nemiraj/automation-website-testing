import React from 'react';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface Stage {
  key: string;
  label: string;
  minPercent: number;
}

const STAGES: Stage[] = [
  { key: 'connect', label: 'Website Connected', minPercent: 10 },
  { key: 'crawl', label: 'Crawling Pages', minPercent: 20 },
  { key: 'pages', label: 'Testing Pages', minPercent: 35 },
  { key: 'responsive', label: 'Responsive & Viewports', minPercent: 65 },
  { key: 'forms', label: 'Form Validation', minPercent: 75 },
  { key: 'a11y_perf', label: 'Accessibility & Perf', minPercent: 85 },
  { key: 'ai', label: 'AI Diagnosis', minPercent: 95 },
  { key: 'done', label: 'Final Report', minPercent: 100 },
];

interface ProgressBarProps {
  percentage: number;
  currentStage: string;
  currentPageUrl?: string;
  status: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  percentage,
  currentStage,
  currentPageUrl,
  status
}) => {
  return (
    <div className="space-y-6">
      {/* Progress Line */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            {status === 'running' && <Loader2 className="h-4 w-4 animate-spin text-emerald-400" />}
            <span className="font-semibold text-white">{currentStage || 'Processing scan...'}</span>
          </div>
          <span className="font-mono font-bold text-emerald-400">{percentage}%</span>
        </div>

        <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500 rounded-full"
            style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
          />
        </div>

        {currentPageUrl && (
          <p className="text-[11px] text-slate-400 font-mono truncate">
            Current Page: <span className="text-slate-300">{currentPageUrl}</span>
          </p>
        )}
      </div>

      {/* Stage Checklist */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 pt-2">
        {STAGES.map((s) => {
          const isDone = percentage >= s.minPercent;
          const isCurrent = percentage < s.minPercent && (percentage >= (s.minPercent - 15));

          return (
            <div
              key={s.key}
              className={`flex items-center gap-2.5 rounded-lg border p-2.5 text-xs transition-all ${
                isDone
                  ? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-300 font-medium'
                  : isCurrent
                  ? 'border-brand-500/50 bg-slate-900 text-white font-semibold ring-1 ring-emerald-500/20'
                  : 'border-slate-800/80 bg-slate-950/40 text-slate-400'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="h-4 w-4 text-emerald-400 animate-spin flex-shrink-0" />
              ) : (
                <Circle className="h-4 w-4 text-slate-400 flex-shrink-0" />
              )}
              <span className="truncate">{s.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
