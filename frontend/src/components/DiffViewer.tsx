import React, { useState } from 'react';
import { Columns, Eye, Layers } from 'lucide-react';

interface DiffViewerProps {
  currentUrl: string;
  previousUrl: string;
  diffMaskUrl?: string;
  diffPercentage?: number;
  viewport?: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({
  currentUrl,
  previousUrl,
  diffMaskUrl,
  diffPercentage,
  viewport
}) => {
  const [viewMode, setViewMode] = useState<'side-by-side' | 'diff-mask' | 'slider'>('side-by-side');
  const [sliderPos, setSliderPos] = useState<number>(50);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 overflow-hidden space-y-4 p-5">
      {/* Control bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            Visual Regression Inspection {viewport && <span className="text-xs font-normal text-slate-400 font-mono">({viewport})</span>}
          </h4>
          {diffPercentage !== undefined && (
            <p className="text-xs text-amber-400 font-medium mt-0.5">
              Visual delta: {diffPercentage}% difference detected
            </p>
          )}
        </div>

        <div className="flex items-center gap-1 rounded-lg bg-slate-950 p-1 border border-slate-800">
          <button
            onClick={() => setViewMode('side-by-side')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              viewMode === 'side-by-side' ? 'bg-emerald-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Columns className="h-3.5 w-3.5" /> Side-by-Side
          </button>
          {diffMaskUrl && (
            <button
              onClick={() => setViewMode('diff-mask')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                viewMode === 'diff-mask' ? 'bg-emerald-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Layers className="h-3.5 w-3.5" /> Highlight Diff
            </button>
          )}
          <button
            onClick={() => setViewMode('slider')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              viewMode === 'slider' ? 'bg-emerald-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Eye className="h-3.5 w-3.5" /> Split Slider
          </button>
        </div>
      </div>

      {/* Views */}
      {viewMode === 'side-by-side' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Previous Baseline
            </span>
            <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden flex items-center justify-center p-2">
              <img src={previousUrl} alt="Previous Test Screenshot" className="max-h-96 w-full object-contain rounded-lg" />
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider block">
              Current Test Run
            </span>
            <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden flex items-center justify-center p-2">
              <img src={currentUrl} alt="Current Test Screenshot" className="max-h-96 w-full object-contain rounded-lg" />
            </div>
          </div>
        </div>
      )}

      {viewMode === 'diff-mask' && diffMaskUrl && (
        <div className="space-y-2">
          <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider block">
            Visual Difference Mask (Red highlights represent altered pixels)
          </span>
          <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden flex items-center justify-center p-2">
            <img src={diffMaskUrl} alt="Visual Difference Mask" className="max-h-96 w-full object-contain rounded-lg" />
          </div>
        </div>
      )}

      {viewMode === 'slider' && (
        <div className="space-y-3">
          <div className="relative h-96 w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-950 select-none">
            {/* Background current image */}
            <img src={currentUrl} alt="Current" className="absolute inset-0 h-full w-full object-contain" />
            
            {/* Foreground previous image with clip */}
            <div 
              className="absolute inset-0 overflow-hidden" 
              style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
            >
              <img src={previousUrl} alt="Previous" className="absolute inset-0 h-full w-full object-contain" />
            </div>

            {/* Slider bar line */}
            <div 
              className="absolute top-0 bottom-0 w-0.5 bg-emerald-400 shadow-[0_0_10px_#10b981]"
              style={{ left: `${sliderPos}%` }}
            />
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400">Previous</span>
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(Number(e.target.value))}
              className="w-full accent-emerald-500 cursor-pointer"
            />
            <span className="text-xs text-emerald-400 font-semibold">Current</span>
          </div>
        </div>
      )}
    </div>
  );
};
