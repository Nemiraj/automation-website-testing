import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  PlayCircle, 
  Smartphone, 
  Monitor, 
  Tablet, 
  Check, 
  Globe, 
  Server, 
  Code2, 
  Lock, 
  Cpu,
  Layers,
  ChevronDown,
  ChevronUp,
  Terminal,
  Database,
  Info
} from 'lucide-react';
import { TestService, ProjectService } from '../services/api';
import { Project } from '../types';

export const NewTest: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Target Mode: 'live' | 'localhost'
  const initialUrl = searchParams.get('url') || '';
  const isInitiallyLocalhost = initialUrl.includes('localhost') || initialUrl.includes('127.0.0.1');
  const [targetType, setTargetType] = useState<'live' | 'localhost'>(isInitiallyLocalhost ? 'localhost' : 'live');

  const [targetUrl, setTargetUrl] = useState(initialUrl || (isInitiallyLocalhost ? 'http://localhost/mywebsite/' : ''));
  const [port, setPort] = useState<number>(80);
  const [technology, setTechnology] = useState<string>('auto');
  
  // Auth state
  const [showAuth, setShowAuth] = useState(false);
  const [authLoginUrl, setAuthLoginUrl] = useState('');
  const [authUsername, setAuthUsername] = useState('');
  const [authPassword, setAuthPassword] = useState('');

  // Local Source Analysis state
  const [enableSourceAnalysis, setEnableSourceAnalysis] = useState(false);
  const [localSourceDir, setLocalSourceDir] = useState('');

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
    form_submission_mode: 'validation_only' as const
  });

  const [loadingProjects, setLoadingProjects] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoadingProjects(true);
        const data = await ProjectService.list();
        setProjects(data);
      } catch (err) {
        console.error('Failed to load projects', err);
      } finally {
        setLoadingProjects(false);
      }
    };
    fetchProjects();
  }, []);

  const handleModeSwitch = (mode: 'live' | 'localhost') => {
    setTargetType(mode);
    if (mode === 'localhost') {
      if (!targetUrl || !targetUrl.includes('localhost')) {
        setTargetUrl('http://localhost/mywebsite/');
      }
      setPort(80);
    } else {
      if (targetUrl.includes('localhost') || targetUrl.includes('127.0.0.1')) {
        setTargetUrl('');
      }
    }
  };

  const handleUrlChange = (url: string) => {
    setTargetUrl(url);
    try {
      if (url.startsWith('http://') || url.startsWith('https://')) {
        const parsed = new URL(url);
        if (parsed.port) {
          setPort(parseInt(parsed.port, 10));
        } else if (parsed.protocol === 'https:') {
          setPort(443);
        } else {
          setPort(80);
        }
      }
    } catch {
      // url parsing in progress
    }
  };

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
        target_type: targetType,
        project_id: projectId || undefined,
        config: {
          max_pages: maxPages,
          timeout_ms: timeoutMs,
          viewports: selectedViewports,
          technology: technology,
          port: port,
          auth_login_url: authLoginUrl.trim() || undefined,
          auth_username: authUsername.trim() || undefined,
          auth_password: authPassword.trim() || undefined,
          local_source_dir: enableSourceAnalysis && localSourceDir.trim() ? localSourceDir.trim() : undefined,
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
        <h1 className="text-2xl font-bold text-white tracking-tight">Configure Website Test</h1>
        <p className="text-xs text-slate-400 mt-1">
          Select target mode, customize crawl boundaries, viewports, diagnostic engines, and safety rules.
        </p>
      </div>

      {/* Target Type Selector Tabs */}
      <div className="grid grid-cols-2 gap-3 p-1.5 bg-slate-950/80 rounded-2xl border border-slate-800">
        <button
          type="button"
          onClick={() => handleTargetTypeChange('live')}
          className={`flex items-center justify-center gap-3 py-3 px-4 rounded-xl font-semibold text-xs sm:text-sm transition-all ${
            targetType === 'live'
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/20 font-bold'
              : 'text-slate-400 hover:text-white hover:bg-slate-900/50'
          }`}
        >
          <Globe className="h-4 w-4" />
          <span>Live Website</span>
        </button>

        <button
          type="button"
          onClick={() => handleTargetTypeChange('localhost')}
          className={`flex items-center justify-center gap-3 py-3 px-4 rounded-xl font-semibold text-xs sm:text-sm transition-all ${
            targetType === 'localhost'
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/20 font-bold'
              : 'text-slate-400 hover:text-white hover:bg-slate-900/50'
          }`}
        >
          <Server className="h-4 w-4" />
          <span>Localhost / XAMPP Website</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Target URL & Parameters */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs">1</span>
              {targetType === 'localhost' ? 'Localhost Target & Technology' : 'Target Website'}
            </h2>
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase font-bold border ${
              targetType === 'localhost' ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            }`}>
              {targetType === 'localhost' ? 'Localhost Mode' : 'Live Mode'}
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                {targetType === 'localhost' ? 'Localhost Website URL *' : 'Website URL *'}
              </label>
              <input
                type="text"
                required
                value={targetUrl}
                onChange={(e) => handleUrlChange(e.target.value)}
                placeholder={targetType === 'localhost' ? 'http://localhost/mywebsite/' : 'https://example.com'}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 font-mono"
              />
              {targetType === 'localhost' && (
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <span className="text-[11px] text-slate-500 font-medium">Quick examples:</span>
                  {[
                    'http://localhost/mywebsite/',
                    'http://localhost:8080/mywebsite/',
                    'http://127.0.0.1/testsite/',
                    'http://127.0.0.1:8080/myproject/'
                  ].map((ex) => (
                    <button
                      key={ex}
                      type="button"
                      onClick={() => handleUrlChange(ex)}
                      className="rounded-md bg-slate-800/60 hover:bg-slate-800 border border-slate-700 px-2 py-0.5 text-[11px] font-mono text-slate-300 transition-colors"
                    >
                      {ex}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Localhost Specific Port & Technology Options */}
            {targetType === 'localhost' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Port
                  </label>
                  <input
                    type="number"
                    value={port}
                    onChange={(e) => setPort(Number(e.target.value))}
                    min={1}
                    max={65535}
                    placeholder="80"
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Technology Stack
                  </label>
                  <select
                    value={technology}
                    onChange={(e) => setTechnology(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="auto">Auto Detect (Recommended)</option>
                    <option value="php">PHP / Apache / XAMPP</option>
                    <option value="html">HTML / Static</option>
                    <option value="react">React</option>
                    <option value="vue">Vue.js</option>
                    <option value="angular">Angular</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
            )}

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

            {/* Optional Authentication for Local Development */}
            {targetType === 'localhost' && (
              <div className="border-t border-slate-800/80 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAuth(!showAuth)}
                  className="flex items-center justify-between w-full text-xs font-semibold text-slate-300 hover:text-white transition-colors py-1"
                >
                  <div className="flex items-center gap-2">
                    <Lock className="h-3.5 w-3.5 text-slate-400" />
                    <span>Authenticated Testing / Local Login (Optional)</span>
                  </div>
                  {showAuth ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>

                {showAuth && (
                  <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3 p-3 bg-slate-950/60 rounded-xl border border-slate-800">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-400 mb-1">
                        Login URL
                      </label>
                      <input
                        type="text"
                        value={authLoginUrl}
                        onChange={(e) => setAuthLoginUrl(e.target.value)}
                        placeholder="http://localhost/mywebsite/login.php"
                        className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-400 mb-1">
                        Username / Email
                      </label>
                      <input
                        type="text"
                        value={authUsername}
                        onChange={(e) => setAuthUsername(e.target.value)}
                        placeholder="admin"
                        className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-400 mb-1">
                        Password
                      </label>
                      <input
                        type="password"
                        value={authPassword}
                        onChange={(e) => setAuthPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                      />
                    </div>
                    <p className="sm:col-span-3 text-[10px] text-slate-500 flex items-center gap-1.5">
                      <Info className="h-3 w-3 flex-shrink-0" />
                      Credentials are kept in memory during the execution session only and never logged or stored in reports.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Local Project Source Code Analysis (Optional) */}
            {targetType === 'localhost' && (
              <div className="border-t border-slate-800/80 pt-3">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-white flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={enableSourceAnalysis}
                      onChange={(e) => setEnableSourceAnalysis(e.target.checked)}
                      className="rounded border-slate-700 bg-slate-950 text-emerald-500 focus:ring-emerald-500/20"
                    />
                    <span>Enable Local Project Source Analysis</span>
                  </label>
                  <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded font-mono">
                    Exact Fix Guidance
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5 ml-6">
                  Maps rendered DOM issues directly to file names and line numbers in your local PHP, HTML, and CSS files.
                </p>

                {enableSourceAnalysis && (
                  <div className="mt-3 p-3 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
                    <label className="block text-[11px] font-medium text-slate-400">
                      Local Project Directory Path
                    </label>
                    <input
                      type="text"
                      value={localSourceDir}
                      onChange={(e) => setLocalSourceDir(e.target.value)}
                      placeholder="e.g. C:\xampp\htdocs\mywebsite"
                      className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none font-mono"
                    />
                    <p className="text-[10px] text-slate-500">
                      If left blank, the system will auto-detect the project directory inside <code>C:\xampp\htdocs</code> based on the URL path.
                    </p>
                  </div>
                )}
              </div>
            )}
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
            Auditing & Testing Modules
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { key: 'enable_ui', title: 'UI & Layout Overflow', desc: 'Detects horizontal overflow, small click targets, clipping' },
              { key: 'enable_responsive', title: 'Responsive Testing', desc: 'Runs page across selected device viewports' },
              { key: 'enable_links', title: 'Link & PHP Relative Link Testing', desc: 'Identifies 404, 403, 500 status codes, loops, broken .php routes' },
              { key: 'enable_images', title: 'Image & Asset Diagnostics', desc: 'Checks 0-size images, missing alt tags, and missing CSS/JS' },
              { key: 'enable_javascript', title: 'JavaScript & PHP/Server Errors', desc: 'Captures PHP warnings/notices/fatal errors, MySQL connection errors, JS crashes' },
              { key: 'enable_forms', title: 'Form Discovery & Validation', desc: 'Discovers GET/POST forms, required fields, and email validation' },
              { key: 'enable_accessibility', title: 'Accessibility Compliance', desc: 'Audits lang tags, empty buttons, ARIA labels, duplicate IDs' },
              { key: 'enable_performance', title: 'Performance Metrics', desc: 'Measures Navigation Timing, FCP, and asset transfer sizes' },
              { key: 'enable_screenshots', title: 'Screenshot Capture', desc: 'Captures full-page and multi-viewport screenshots' },
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
            <span>
              {submitting
                ? 'Launching Test Pipeline...'
                : targetType === 'localhost'
                ? 'Start Localhost Test'
                : 'Start Automated Test'}
            </span>
          </button>
        </div>
      </form>
    </div>
  );
};
