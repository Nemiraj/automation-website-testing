import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  PlayCircle, 
  Settings, 
  Smartphone, 
  Monitor, 
  Tablet, 
  Check, 
  Layers, 
  Sparkles,
  ShieldAlert,
  HelpCircle 
} from 'lucide-react';
import { TestService, ProjectService } from '../services/api';
import { Project } from '../types';

export const NewTest: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [targetUrl, setTargetUrl] = useState(searchParams.get('url') || '');
  const [projectId, setProjectId] = useState(searchParams.get('projectId') || '');
  const [projects, setProjects] = useState<Project[]>([]);
  const [maxPages, setMaxPages] = useState<number>(10);
  const [timeoutMs, setTimeoutMs] = useState<number>(30000);
  
  // Selected Viewports
  const [selectedViewports, setSelectedViewports] = useState<string[]>([
    'desktop_large',
    'tablet',
    'mobile_large'
  ]);

  // Feature switches
  const [features, setFeatures] = useState({
    enable_ui: true,
    enable_responsive: true,
    enable_links: true,
    enable_images: true,
    enable_javascript: true,
    enable_forms: true,
    enable_accessibility: true,
    enable_performance: true,
    enable_screenshots: true,
    enable_ai: true,
    form_submission_mode: 'validation_only' as 'validation_only' | 'synthetic_submit'
  });

  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await ProjectService.list();
        setProjects(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchProjects();
  }, []);

  const toggleViewport = (vp: string) => {
    if (selectedViewports.includes(vp)) {
      if (selectedViewports.length > 1) {
        setSelectedViewports(selectedViewports.filter(v => v !== vp));
      }
    } else {
      setSelectedViewports([...selectedViewports, vp]);
    }
  };

  const toggleFeature = (key: keyof typeof features) => {
    if (key === 'form_submission_mode') return;
    setFeatures(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl.trim()) return;

    setSubmitting(true);
    try {
      const payload = {
        target_url: targetUrl.trim(),
        project_id: projectId || undefined,
        config: {
          max_pages: maxPages,
          timeout_ms: timeoutMs,
          viewports: selectedViewports,
          ...features
        }
      };

      const test = await TestService.create(payload);
      navigate(`/tests/${test.id}/progress`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start automated test');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Configure Automated Test</h1>
        <p className="text-xs text-slate-400 mt-1">
          Customize crawl boundaries, multi-device viewports, diagnostic engines, and safety rules.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Target URL & Project */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs">1</span>
            Target Website
          </h2>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Website URL *
              </label>
              <input
                type="text"
                required
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 font-mono"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Link to Project (Optional)
                </label>
                <select
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="">No Project (Ad-hoc Scan)</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} ({p.base_url})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Max Pages to Crawl
                </label>
                <select
                  value={maxPages}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none font-mono"
                >
                  <option value={1}>1 Page (Single URL)</option>
                  <option value={5}>5 Pages</option>
                  <option value={10}>10 Pages (Recommended)</option>
                  <option value={25}>25 Pages</option>
                  <option value={50}>50 Pages</option>
                  <option value={100}>100 Pages</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Viewport Selection */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs">2</span>
            Responsive Viewports
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              { id: 'desktop_large', label: 'Desktop Large', res: '1920 × 1080', icon: Monitor },
              { id: 'desktop_standard', label: 'Desktop Standard', res: '1366 × 768', icon: Monitor },
              { id: 'tablet', label: 'Tablet Portrait', res: '768 × 1024', icon: Tablet },
              { id: 'mobile_large', label: 'Mobile Large', res: '390 × 844', icon: Smartphone },
              { id: 'mobile_standard', label: 'Mobile Standard', res: '375 × 812', icon: Smartphone },
            ].map((vp) => {
              const active = selectedViewports.includes(vp.id);
              const Icon = vp.icon;
              return (
                <button
                  type="button"
                  key={vp.id}
                  onClick={() => toggleViewport(vp.id)}
                  className={`flex items-center justify-between rounded-xl border p-3.5 text-left transition-all ${
                    active
                      ? 'border-emerald-500 bg-emerald-500/10 text-white'
                      : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`h-4 w-4 ${active ? 'text-emerald-400' : 'text-slate-500'}`} />
                    <div>
                      <p className="text-xs font-semibold text-slate-200">{vp.label}</p>
                      <p className="text-[11px] font-mono text-slate-400">{vp.res}</p>
                    </div>
                  </div>
                  <div className={`flex h-4 w-4 items-center justify-center rounded border ${
                    active ? 'border-emerald-500 bg-emerald-500 text-slate-950' : 'border-slate-700'
                  }`}>
                    {active && <Check className="h-3 w-3" />}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Diagnostic Feature Toggles */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs">3</span>
            Auditing Modules
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { key: 'enable_ui', title: 'UI & Layout Overflow', desc: 'Detects horizontal overflow, small click targets, heading order' },
              { key: 'enable_responsive', title: 'Responsive Testing', desc: 'Runs page across selected device viewports' },
              { key: 'enable_links', title: 'Broken Link Testing', desc: 'Identifies 404, 403, 500 status codes and loops' },
              { key: 'enable_images', title: 'Broken Image Diagnostics', desc: 'Checks 0-size images, missing alt tags, and CLS dimensions' },
              { key: 'enable_javascript', title: 'JavaScript & Console Errors', desc: 'Captures uncaught runtime crashes and console.error logs' },
              { key: 'enable_forms', title: 'Form Discovery & Validation', desc: 'Discovers inputs, email types, required validation' },
              { key: 'enable_accessibility', title: 'Accessibility Compliance', desc: 'Audits lang tags, empty buttons, ARIA labels, duplicate IDs' },
              { key: 'enable_performance', title: 'Performance Metrics', desc: 'Measures Navigation Timing, FCP, and large asset sizes' },
              { key: 'enable_screenshots', title: 'Screenshot Capture', desc: 'Captures full-page and viewport screenshots' },
              { key: 'enable_ai', title: 'AI Diagnosis & Priority Fixes', desc: 'Synthesizes structured findings into technical recommendations' },
            ].map((mod) => {
              const k = mod.key as keyof typeof features;
              const isEnabled = features[k];

              return (
                <div
                  key={mod.key}
                  onClick={() => toggleFeature(k)}
                  className={`flex items-start justify-between rounded-xl border p-3.5 cursor-pointer transition-all ${
                    isEnabled
                      ? 'border-emerald-500/30 bg-slate-950 text-white'
                      : 'border-slate-800/80 bg-slate-950/40 text-slate-500'
                  }`}
                >
                  <div className="space-y-1 pr-3">
                    <p className="text-xs font-bold text-slate-200">{mod.title}</p>
                    <p className="text-[11px] text-slate-400 leading-snug">{mod.desc}</p>
                  </div>
                  <div className={`mt-0.5 flex h-4 w-4 items-center justify-center rounded border flex-shrink-0 ${
                    isEnabled ? 'border-emerald-500 bg-emerald-500 text-slate-950' : 'border-slate-700'
                  }`}>
                    {isEnabled && <Check className="h-3 w-3" />}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Submit button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center gap-2 rounded-xl bg-emerald-500 px-8 py-3.5 text-sm font-bold text-slate-950 hover:bg-emerald-400 active:scale-95 transition-all shadow-xl shadow-emerald-950/50 disabled:opacity-50"
          >
            <PlayCircle className="h-5 w-5" />
            <span>{submitting ? 'Launching Test Pipeline...' : 'Start Automated Test'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
