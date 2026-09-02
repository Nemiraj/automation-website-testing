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
            <div className="flex flex-wrap items-center gap-2">
              {issue.issue_number && (
                <span className="rounded-md bg-emerald-500/20 text-emerald-400 px-2 py-0.5 text-xs font-bold font-mono border border-emerald-500/30">
                  Issue #{issue.issue_number}
                </span>
              )}
              <SeverityBadge severity={issue.severity} />
              <CategoryBadge category={issue.category} />
              {issue.viewport && (
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[11px] font-mono text-slate-400 border border-slate-700">
                  {issue.viewport}
                </span>
              )}
              {issue.section && (
                <span className="rounded bg-slate-800/80 px-2 py-0.5 text-[11px] font-medium text-slate-300 border border-slate-700">
                  Section: {issue.section}
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
          {/* Exact Element & Coordinates Location Card */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-4 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold flex items-center gap-1.5 text-white">
                <Code className="h-4 w-4 text-emerald-400" /> Target DOM Element & Location
              </span>
              {issue.selector && (
                <button
                  onClick={handleCopySelector}
                  className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white transition-colors"
                >
                  {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                  {copied ? 'Copied' : 'Copy Selector'}
                </button>
              )}
            </div>

            {issue.selector ? (
              <div className="space-y-2">
                <code className="block font-mono text-xs text-emerald-400 bg-slate-900/90 px-3 py-2 rounded-lg border border-slate-800 select-all overflow-x-auto">
                  {issue.selector}
                </code>
                
                {issue.coordinates && issue.coordinates.width ? (
                  <div className="flex flex-wrap items-center gap-3 pt-1 text-xs text-slate-300 font-mono">
                    <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800">
                      <strong className="text-slate-500 font-sans">Tag:</strong> &lt;{issue.coordinates.tag || 'element'}&gt;
                    </span>
                    <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800">
                      <strong className="text-slate-500 font-sans">Position:</strong> X: {issue.coordinates.x}px, Y: {issue.coordinates.y}px
                    </span>
                    <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800">
                      <strong className="text-slate-500 font-sans">Size:</strong> {issue.coordinates.width} × {issue.coordinates.height}px
                    </span>
                  </div>
                ) : (
                  <div className="text-[11px] text-slate-500 italic">
                    Coordinates extracted from document DOM tree.
                  </div>
                )}
              </div>
            ) : (
              <div className="text-xs text-amber-400 bg-amber-500/10 px-3 py-2 rounded-lg border border-amber-500/20 font-medium">
                Page-level issue (No specific DOM element bounding box).
              </div>
            )}
          </div>

          {/* Description */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Problem Description
            </h4>
            <p className="text-sm text-slate-200 leading-relaxed">
              {issue.description}
            </p>
          </div>

          {/* Visual Evidence (Annotated vs Original Screenshot) */}
          {(issue.annotated_screenshot_url || issue.screenshot_url) && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <ImageIcon className="h-3.5 w-3.5 text-emerald-400" /> Visual Location Evidence
                </h4>
                {issue.annotated_screenshot_url && issue.screenshot_url && (
                  <span className="text-[11px] font-medium text-emerald-400">
                    Exact location marker shown below
                  </span>
                )}
              </div>
              
              <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950 p-2 shadow-inner">
                <img
                  src={issue.annotated_screenshot_url || issue.screenshot_url}
                  alt={issue.title}
                  className="w-full h-auto max-h-96 object-contain mx-auto rounded-lg"
                />
              </div>
              
              {issue.annotated_screenshot_url && issue.screenshot_url && (
                <div className="flex justify-end gap-2 text-xs">
                  <a
                    href={issue.annotated_screenshot_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-emerald-400 hover:underline flex items-center gap-1"
                  >
                    Open Full Annotated Screenshot <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
            </div>
          )}

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

          {/* Likely Source Code Location & Mapping */}
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Code className="h-4 w-4 text-emerald-400" /> Responsible Code Location
              </span>
              {issue.source_location?.confidence && (
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  issue.source_location.confidence === 'confirmed'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : issue.source_location.confidence === 'likely'
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                }`}>
                  {issue.source_location.confidence === 'confirmed' ? 'Confirmed Source' : issue.source_location.confidence === 'likely' ? 'Likely Source' : 'Inferred'}
                </span>
              )}
            </div>

            {issue.source_location?.source_file ? (
              <div className="space-y-2">
                <p className="text-xs font-mono text-emerald-400">
                  📁 {issue.source_location.source_file}:{issue.source_location.line_number}
                </p>
                {issue.source_location.snippet && (
                  <pre className="text-[11px] font-mono text-slate-300 bg-slate-900 p-2.5 rounded-lg border border-slate-800 overflow-x-auto whitespace-pre-wrap">
                    {issue.source_location.snippet}
                  </pre>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-400 font-mono bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                {issue.source_location?.search_hint || `Search your project codebase for: ${issue.selector || 'this element'}`}
              </p>
            )}
          </div>

          {/* Recommended Solution & Exact Fix Guidance */}
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
                <Lightbulb className="h-4 w-4" />
                <span>Exact Fix Guidance</span>
              </div>
              {issue.fix_confidence && (
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  issue.fix_confidence === 'high'
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : issue.fix_confidence === 'medium'
                    ? 'bg-amber-500/20 text-amber-400'
                    : 'bg-slate-800 text-slate-400'
                }`}>
                  Fix Confidence: {issue.fix_confidence}
                </span>
              )}
            </div>

            {issue.recommendation && (
              <p className="text-xs leading-relaxed text-slate-300">
                {issue.recommendation}
              </p>
            )}

            {issue.fix_reasoning && (
              <p className="text-[11px] text-slate-400 italic">
                <strong>Reason:</strong> {issue.fix_reasoning}
              </p>
            )}

            {issue.suggested_fix && (
              <div className="space-y-1.5 pt-1">
                <span className="text-[11px] font-semibold text-emerald-300 flex items-center gap-1">
                  <Wrench className="h-3.5 w-3.5" /> Suggested Code / CSS Solution:
                </span>
                <pre className="text-xs font-mono text-emerald-300 bg-slate-900 p-3 rounded-lg border border-slate-800 overflow-x-auto whitespace-pre-wrap select-all">
                  {issue.suggested_fix}
                </pre>
              </div>
            )}
          </div>

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
