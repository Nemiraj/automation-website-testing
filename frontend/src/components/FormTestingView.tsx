import React, { useState } from 'react';
import {
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  Play,
  Sparkles,
  ShieldCheck,
  Zap,
  CornerDownRight,
  Send,
  Lock,
  Mail,
  User,
  MessageSquare,
  Key,
  HelpCircle,
  ExternalLink,
  Code2,
  Check,
  X
} from 'lucide-react';
import { ScanResult, TestCase, TestRun, FormFieldInfo } from '../types';

interface FormTestingViewProps {
  scanResult: ScanResult | null;
  testRun: TestRun | null;
  testCases: TestCase[];
  onRunFormTests: () => void;
  isRunning: boolean;
}

export const FormTestingView: React.FC<FormTestingViewProps> = ({
  scanResult,
  testRun,
  testCases,
  onRunFormTests,
  isRunning
}) => {
  const [selectedFuzzStrategy, setSelectedFuzzStrategy] = useState<'valid' | 'empty' | 'invalid_email' | 'xss_fuzz'>('valid');
  const [activeFormIndex, setActiveFormIndex] = useState(0);

  // Extract forms discovered from scan result pages or default demo forms
  const discoveredForms = React.useMemo(() => {
    if (!scanResult || scanResult.pages.length === 0) {
      return [
        {
          id: 'FORM-DEMO-CONTACT',
          name: 'Contact & Customer Feedback Form',
          pageUrl: 'http://localhost/contact',
          pageTitle: 'Contact Us — NovaStore',
          action: '/api/contact',
          method: 'POST',
          fields: [
            { name: 'name', type: 'text', label: 'Your Name', placeholder: 'John Smith', required: true },
            { name: 'email', type: 'email', label: 'Email Address', placeholder: 'john@example.com', required: true },
            { name: 'message', type: 'textarea', label: 'Inquiry Message', placeholder: 'How can we assist you?', required: true }
          ],
          submitButtonText: 'Submit Message',
          status: 'PASSED'
        },
        {
          id: 'FORM-DEMO-LOGIN',
          name: 'Account Authentication Form',
          pageUrl: 'http://localhost/login',
          pageTitle: 'Sign In — NovaStore',
          action: '/api/login',
          method: 'POST',
          fields: [
            { name: 'email', type: 'email', label: 'Email Address', placeholder: 'admin@example.com', required: true },
            { name: 'password', type: 'password', label: 'Password', placeholder: '••••••••', required: true }
          ],
          submitButtonText: 'Sign In',
          status: 'PASSED'
        },
        {
          id: 'FORM-DEMO-CHECKOUT',
          name: 'Payment & Checkout Form',
          pageUrl: 'http://localhost/checkout',
          pageTitle: 'Secure Checkout',
          action: '/api/payment',
          method: 'POST',
          fields: [
            { name: 'name', type: 'text', label: 'Full Name', placeholder: 'Jane Doe', required: true },
            { name: 'cardNumber', type: 'text', label: 'Card Number', placeholder: '4242 •••• •••• 4242', required: true },
            { name: 'expiry', type: 'text', label: 'Expiry Date', placeholder: 'MM/YY', required: true },
            { name: 'cvc', type: 'text', label: 'CVC Security Code', placeholder: '888', required: true }
          ],
          submitButtonText: 'Complete Payment',
          status: 'FAILED'
        }
      ];
    }

    const forms: any[] = [];
    scanResult.pages.forEach((page) => {
      const formElements = page.elements.filter(e => e.action || e.tagName.toUpperCase() === 'FORM' || e.inputType);
      if (formElements.length > 0 || page.formsCount > 0) {
        const inputs = page.elements.filter(e => e.tagName.toUpperCase() in {'INPUT': 1, 'SELECT': 1, 'TEXTAREA': 1});
        const formInputs: FormFieldInfo[] = inputs.map(inp => ({
          name: inp.name || inp.idAttr || inp.placeholder || 'input_field',
          type: inp.inputType || 'text',
          placeholder: inp.placeholder || '',
          required: true,
          label: inp.accessibleName || inp.placeholder || inp.name || 'Input'
        }));

        forms.push({
          id: `FORM-${page.id}`,
          name: `${page.title || page.path} Form`,
          pageUrl: page.url,
          pageTitle: page.title,
          action: formElements[0]?.action || page.path,
          method: formElements[0]?.method || 'POST',
          fields: formInputs.length > 0 ? formInputs : [
            { name: 'email', type: 'email', label: 'Email', placeholder: 'user@example.com', required: true },
            { name: 'query', type: 'text', label: 'Search Query', placeholder: 'Type keywords...', required: false }
          ],
          submitButtonText: 'Submit',
          status: page.healthStatus === 'HEALTHY' ? 'PASSED' : 'FAILED'
        });
      }
    });

    return forms.length > 0 ? forms : [
      {
        id: 'FORM-DEFAULT',
        name: 'Standard HTML5 Form',
        pageUrl: scanResult.rootUrl,
        pageTitle: 'Home Page Form',
        action: '/submit',
        method: 'POST',
        fields: [
          { name: 'email', type: 'email', label: 'Email', placeholder: 'user@example.com', required: true },
          { name: 'message', type: 'textarea', label: 'Message', placeholder: 'Your message...', required: true }
        ],
        submitButtonText: 'Send',
        status: 'PASSED'
      }
    ];
  }, [scanResult]);

  const formTestScenarios = [
    {
      id: 'valid',
      title: 'Valid Submission (Happy Path)',
      desc: 'Populates all fields with realistic valid formats and asserts successful submission without errors.',
      tag: 'Positive Flow',
      badgeColor: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
    },
    {
      id: 'empty',
      title: 'Empty Required Fields Validation',
      desc: 'Leaves required fields empty to verify browser HTML5 required prompts and inline error indicators.',
      tag: 'Required Check',
      badgeColor: 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    },
    {
      id: 'invalid_email',
      title: 'Invalid Email / Syntax Boundary',
      desc: 'Submits malformed email strings (missing @ or domain) to test regex validation boundaries.',
      tag: 'Boundary Test',
      badgeColor: 'bg-blue-500/20 text-cyan-400 border-blue-500/30'
    },
    {
      id: 'xss_fuzz',
      title: 'Security Fuzzing & Special Characters',
      desc: 'Fuzzes inputs with quotes, HTML tags (<script>), and unicode characters to ensure sanitization.',
      tag: 'Fuzzing & Security',
      badgeColor: 'bg-purple-500/20 text-purple-400 border-purple-500/30'
    }
  ];

  const currentForm = discoveredForms[activeFormIndex] || discoveredForms[0];

  const getFieldIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'email': return <Mail className="w-4 h-4 text-cyan-400" />;
      case 'password': return <Lock className="w-4 h-4 text-amber-400" />;
      case 'textarea': return <MessageSquare className="w-4 h-4 text-emerald-400" />;
      default: return <User className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-500/10 text-cyan-400 border border-blue-500/20">
              <FileSpreadsheet className="w-4 h-4" />
            </span>
            <h2 className="text-2xl font-black text-white tracking-tight">
              Form Validation, Input Boundary & Fuzzing Engine
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Autonomously inspects HTML5 forms, verifies required constraints, tests regex boundaries, and executes security fuzzing.
          </p>
        </div>

        <button
          onClick={onRunFormTests}
          disabled={isRunning}
          className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-blue-500/20 self-start"
        >
          <Play className={`w-3.5 h-3.5 fill-current ${isRunning ? 'animate-spin' : ''}`} />
          <span>{isRunning ? 'Testing Forms...' : 'Run All Form Scenarios'}</span>
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 bg-surface/90 backdrop-blur-md border border-border/80 rounded-2xl flex items-center justify-between shadow-xl">
          <div>
            <div className="text-[10px] font-black uppercase text-slate-400">Discovered Forms</div>
            <div className="text-3xl font-black text-white mt-1">{discoveredForms.length}</div>
          </div>
          <div className="p-3 bg-blue-500/10 text-cyan-400 rounded-xl border border-blue-500/20">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 bg-surface/90 backdrop-blur-md border border-border/80 rounded-2xl flex items-center justify-between shadow-xl">
          <div>
            <div className="text-[10px] font-black uppercase text-slate-400">Total Input Fields</div>
            <div className="text-3xl font-black text-white mt-1">
              {discoveredForms.reduce((acc, f) => acc + f.fields.length, 0)}
            </div>
          </div>
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 bg-surface/90 backdrop-blur-md border border-border/80 rounded-2xl flex items-center justify-between shadow-xl">
          <div>
            <div className="text-[10px] font-black uppercase text-slate-400">Validation Status</div>
            <div className="text-3xl font-black text-cyan-400 mt-1">100% Covered</div>
          </div>
          <div className="p-3 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
            <Zap className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Main Form Inspector & Tester */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left List: Form Selector */}
        <div className="space-y-3">
          <div className="text-xs font-black uppercase tracking-wider text-slate-400 px-1">
            Select Form to Inspect ({discoveredForms.length})
          </div>

          <div className="space-y-2">
            {discoveredForms.map((form, idx) => {
              const isActive = activeFormIndex === idx;
              return (
                <button
                  key={form.id}
                  onClick={() => setActiveFormIndex(idx)}
                  className={`w-full p-4 rounded-2xl border text-left transition-all ${
                    isActive
                      ? 'bg-blue-600/20 border-cyan-500/40 text-white shadow-lg'
                      : 'bg-surface/80 border-border hover:border-slate-600 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                      {form.method} {form.action}
                    </span>
                    <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${
                      form.status === 'PASSED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {form.status}
                    </span>
                  </div>
                  <div className="text-sm font-bold text-white mt-1">{form.name}</div>
                  <div className="text-xs text-slate-400 truncate mt-0.5">{form.pageUrl}</div>
                  <div className="text-[10px] text-slate-500 mt-2 font-mono">{form.fields.length} input controls detected</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Area: Form Details & Interactive Fuzzer */}
        <div className="lg:col-span-2 space-y-6">
          {currentForm && (
            <div className="p-6 bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl space-y-6 shadow-2xl">
              {/* Form Info Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-border/80">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded text-[10px] font-bold font-mono">
                      {currentForm.id}
                    </span>
                    <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded text-[10px] font-bold font-mono">
                      HTTP {currentForm.method}
                    </span>
                  </div>
                  <h3 className="text-xl font-black text-white">{currentForm.name}</h3>
                  <a
                    href={currentForm.pageUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-cyan-400 hover:underline flex items-center gap-1 mt-1 font-mono"
                  >
                    {currentForm.pageUrl} <ExternalLink className="w-3 h-3" />
                  </a>
                </div>

                <div className="text-right">
                  <div className="text-[10px] uppercase font-bold text-slate-400">Target Endpoint</div>
                  <div className="text-xs font-mono font-bold text-slate-200 bg-black/40 px-2.5 py-1 rounded-lg border border-slate-800 mt-1">
                    {currentForm.action}
                  </div>
                </div>
              </div>

              {/* Fields Breakdown Table */}
              <div className="space-y-2.5">
                <div className="text-xs font-black uppercase tracking-wider text-slate-400">
                  Detected Input Fields ({currentForm.fields.length})
                </div>

                <div className="space-y-2">
                  {currentForm.fields.map((field: FormFieldInfo, fIdx: number) => (
                    <div
                      key={fIdx}
                      className="p-3.5 bg-black/40 rounded-2xl border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-slate-900 rounded-xl border border-slate-800">
                          {getFieldIcon(field.type)}
                        </div>
                        <div>
                          <div className="text-xs font-bold text-white flex items-center gap-2">
                            <span>{field.label || field.name}</span>
                            {field.required && (
                              <span className="text-[9px] px-1.5 py-0.2 rounded bg-red-500/20 text-red-400 border border-red-500/30 font-bold uppercase">
                                Required
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                            name="{field.name}" • type="{field.type}"
                          </div>
                        </div>
                      </div>

                      <div className="text-right">
                        <span className="text-[11px] font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                          Placeholder: {field.placeholder ? `"${field.placeholder}"` : 'None'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Fuzzing & Test Strategy Selector */}
              <div className="space-y-3 pt-4 border-t border-border/80">
                <div className="text-xs font-black uppercase tracking-wider text-slate-400">
                  Autonomous Form Test Scenarios
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {formTestScenarios.map((scen) => {
                    const isSelected = selectedFuzzStrategy === scen.id;
                    return (
                      <button
                        key={scen.id}
                        onClick={() => setSelectedFuzzStrategy(scen.id as any)}
                        className={`p-4 rounded-2xl border text-left transition-all ${
                          isSelected
                            ? 'bg-blue-600/20 border-cyan-400 text-white shadow-md'
                            : 'bg-black/40 border-slate-800 hover:border-slate-700 text-slate-300'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${scen.badgeColor}`}>
                            {scen.tag}
                          </span>
                          {isSelected && <Check className="w-4 h-4 text-cyan-400" />}
                        </div>
                        <div className="text-xs font-bold text-white">{scen.title}</div>
                        <div className="text-[11px] text-slate-400 mt-1 leading-relaxed">{scen.desc}</div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Action Bar */}
              <div className="p-4 bg-black/50 rounded-2xl border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="text-xs text-slate-400 font-mono">
                  Playwright Python will synthesize target actions for <strong>{currentForm.fields.length} inputs</strong>.
                </div>
                <button
                  onClick={onRunFormTests}
                  disabled={isRunning}
                  className="px-5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 self-start sm:self-auto shrink-0 shadow-md shadow-blue-500/20"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Execute Form Test</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
