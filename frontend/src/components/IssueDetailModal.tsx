import React, { useState } from 'react';
import { IssueItem } from '../types';
import { SeverityBadge, CategoryBadge } from './IssueBadge';
import { 
  X, 
  Copy, 
  Check, 
  HelpCircle, 
  Lightbulb, 
  Wrench, 
  Code, 
  Image as ImageIcon,
  ExternalLink 
} from 'lucide-react';
import { TestService } from '../services/api';

interface IssueDetailModalProps {
  issue: IssueItem | null;
  onClose: () => void;
  onStatusUpdated?: (issue: IssueItem) => void;
}

export const IssueDetailModal: React.FC<IssueDetailModalProps> = ({
  issue,
  onClose,
  onStatusUpdated
}) => {
  const [copied, setCopied] = useState(false);
  const [updating, setUpdating] = useState(false);

  if (!issue) return null;

  const handleCopySelector = () => {
    if (issue.selector) {
      navigator.clipboard.writeText(issue.selector);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleStatusChange = async (newStatus: 'open' | 'resolved' | 'ignored') => {
    setUpdating(true);
    try {
      const updated = await TestService.updateIssueStatus(issue.id, newStatus);
      if (onStatusUpdated) {
        onStatusUpdated(updated);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="relative w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl overflow-hidden my-8 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 p-6 bg-slate-900/60">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <SeverityBadge severity={issue.severity} />
              <CategoryBadge category={issue.category} />
              {issue.viewport && (
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[11px] font-mono text-slate-400 border border-slate-700">
                  {issue.viewport}
                </span>
              )}
            </div>
            <h3 className="text-lg font-bold text-white leading-snug">
              {issue.title}
            </h3>
            <p className="text-xs text-slate-400 flex items-center gap-1.5 font-mono">
              <span className="text-slate-400">Page:</span>
              <a href={issue.page_url} target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:underline flex items-center gap-1">
                {issue.page_url}
                <ExternalLink className="h-3 w-3" />
              </a>
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-5 max-h-[70vh] overflow-y-auto">
          {/* Element Selector */}
          {issue.selector && (
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
                <span className="font-semibold flex items-center gap-1.5">
                  <Code className="h-3.5 w-3.5 text-emerald-400" /> Target DOM Selector
                </span>
                <button
                  onClick={handleCopySelector}
                  className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white transition-colors"
                >
                  {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
              <code className="block font-mono text-xs text-emerald-400 bg-slate-900/90 px-2.5 py-1.5 rounded-lg border border-slate-800 select-all overflow-x-auto">
                {issue.selector}
              </code>
            </div>
          )}

          {/* Description */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Description
            </h4>
            <p className="text-sm text-slate-200 leading-relaxed">
              {issue.description}
            </p>
          </div>

          {/* Why It Matters */}
          {issue.why_it_matters && (
            <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400">
                <HelpCircle className="h-4 w-4" />
                <span>Why this matters</span>
              </div>
              <p className="text-xs leading-relaxed text-slate-300">
                {issue.why_it_matters}
              </p>
            </div>
          )}

          {/* Recommended Solution */}
          {issue.recommendation && (
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
                <Lightbulb className="h-4 w-4" />
                <span>Recommended Solution</span>
              </div>
              <p className="text-xs leading-relaxed text-slate-300">
                {issue.recommendation}
              </p>
            </div>
          )}

          {/* Suggested Fix */}
          {issue.suggested_fix && (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
                <Wrench className="h-4 w-4 text-emerald-400" />
                <span>Suggested Code Fix</span>
              </div>
              <p className="text-xs font-mono text-slate-300 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                {issue.suggested_fix}
              </p>
            </div>
          )}

          {/* Evidence JSON */}
          {issue.evidence && Object.keys(issue.evidence).length > 0 && (
            <div className="space-y-1.5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Diagnostic Evidence
              </h4>
              <pre className="max-h-40 overflow-auto rounded-lg bg-slate-950 p-3 font-mono text-[11px] text-slate-300 border border-slate-800">
                {JSON.stringify(issue.evidence, null, 2)}
              </pre>
            </div>
          )}

          {/* Screenshot Evidence */}
          {issue.screenshot_url && (
            <div className="space-y-1.5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <ImageIcon className="h-3.5 w-3.5" /> Visual Evidence
              </h4>
              <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950">
                <img
                  src={issue.screenshot_url}
                  alt="Visual Evidence"
                  className="w-full h-auto max-h-60 object-contain mx-auto"
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between border-t border-slate-800 bg-slate-950 px-6 py-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Status:</span>
            <span className="rounded bg-slate-800 px-2 py-0.5 text-xs font-semibold text-slate-200 uppercase">
              {issue.status}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {issue.status !== 'resolved' && (
              <button
                disabled={updating}
                onClick={() => handleStatusChange('resolved')}
                className="rounded-lg bg-emerald-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500 transition-colors disabled:opacity-50"
              >
                Mark as Resolved
              </button>
            )}
            {issue.status === 'resolved' && (
              <button
                disabled={updating}
                onClick={() => handleStatusChange('open')}
                className="rounded-lg bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:bg-slate-700 transition-colors disabled:opacity-50"
              >
                Reopen Issue
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
