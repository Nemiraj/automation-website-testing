import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, NavItem } from './components/Sidebar';
import { FormTestingView } from './components/FormTestingView';
import { DashboardView } from './components/DashboardView';
import { UserJourneysView } from './components/UserJourneysView';
import { SiteMapPagesView } from './components/SiteMapPagesView';
import { NetworkConsoleView } from './components/NetworkConsoleView';
import { TestRunsView } from './components/TestRunsView';
import { TestCasesView } from './components/TestCasesView';
import { FailureInvestigationModal } from './components/FailureInvestigationModal';
import { BrowserType, EnvironmentType, FailureInvestigation, ScanResult, TestCase, TestRun } from './types';
import { Sparkles, AlertOctagon, CheckCircle2, Bell, Cpu, ShieldCheck } from 'lucide-react';

export default function App() {
  const [activeNav, setActiveNav] = useState<NavItem>('dashboard');
  const [websiteUrl, setWebsiteUrl] = useState('http://localhost:3001');
  const [environment, setEnvironment] = useState<EnvironmentType>('local');
  const [browser, setBrowser] = useState<BrowserType>('chromium');

  const [currentRun, setCurrentRun] = useState<TestRun | null>(null);
  const [runsHistory, setRunsHistory] = useState<TestRun[]>([]);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [activeInvestigation, setActiveInvestigation] = useState<FailureInvestigation | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [isRunning, setIsRunning] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [progressData, setProgressData] = useState<{ currentTest: number; totalTests: number; testName: string; status: string; completedPercentage: number } | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const runsRes = await fetch('/api/test-runs');
      if (runsRes.ok) {
        const runs: TestRun[] = await runsRes.json();
        setRunsHistory(runs);
        if (runs.length > 0) setCurrentRun(runs[0]);
      }

      const scanRes = await fetch('/api/websites/WEB-DEMO-01/scan');
      if (scanRes.ok) {
        const scan = await scanRes.json();
        setScanResult(scan);
      }

      const testsRes = await fetch('/api/websites/WEB-DEMO-01/tests');
      if (testsRes.ok) {
        const tests = await testsRes.json();
        setTestCases(tests);
      }
    } catch (e) {
      console.error('Initial data fetch notice:', e);
    }
  };

  const handleScanWebsite = async () => {
    setIsScanning(true);
    showToast('Autonomous crawler scanning website structure...');
    try {
      const res = await fetch('/api/websites/WEB-DEMO-01/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: websiteUrl, maxPages: 10, maxDepth: 3 })
      });
      if (res.ok) {
        const data = await res.json();
        setScanResult(data.scanResult);
        if (data.tests) setTestCases(data.tests);
        setActiveNav('pages');
        showToast(`Scan complete: ${data.scanResult.totalPages} pages discovered.`);
      }
    } catch (err) {
      console.error('Scan error:', err);
    } finally {
      setIsScanning(false);
    }
  };

  const handleRunTests = async () => {
    setIsRunning(true);
    setProgressData({
      currentTest: 1,
      totalTests: testCases.length || 5,
      testName: 'Launching Python Playwright Engine...',
      status: 'running',
      completedPercentage: 10
    });

    try {
      const res = await fetch('/api/websites/WEB-DEMO-01/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: websiteUrl, browserType: browser })
      });

      if (res.ok) {
        const data = await res.json();
        const run: TestRun = data.testRun;
        setCurrentRun(run);
        setRunsHistory(prev => [run, ...prev]);
        setActiveNav('dashboard');
        showToast(`Test Run Finished: ${run.passedTests} passed, ${run.failedTests} failed.`);
      }
    } catch (err) {
      console.error('Execution error:', err);
    } finally {
      setIsRunning(false);
      setProgressData(null);
    }
  };

  const criticalFailuresCount = currentRun?.criticalFailures || 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased selection:bg-blue-600 selection:text-white">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-8 z-50 p-4 bg-slate-900/90 backdrop-blur-xl border border-blue-500/40 text-cyan-300 rounded-2xl shadow-2xl flex items-center gap-3 animate-fade-in text-xs font-bold font-mono">
          <Sparkles className="w-4 h-4 text-cyan-400 animate-spin" />
          <span>{toastMessage}</span>
        </div>
      )}

      <Header
        websiteUrl={websiteUrl}
        setWebsiteUrl={setWebsiteUrl}
        environment={environment}
        setEnvironment={setEnvironment}
        browser={browser}
        setBrowser={setBrowser}
        isRunning={isRunning}
        isScanning={isScanning}
        onScan={handleScanWebsite}
        onRunTests={handleRunTests}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activeNav={activeNav}
          setActiveNav={setActiveNav}
          criticalCount={criticalFailuresCount}
        />

        <main className="flex-1 overflow-y-auto p-8 bg-gradient-to-b from-slate-950 via-slate-900/40 to-slate-950">
          {activeNav === 'dashboard' && (
            <DashboardView
              testRun={currentRun}
              isRunning={isRunning}
              progressData={progressData}
              onOpenInvestigation={(inv) => setActiveInvestigation(inv)}
              onRunTests={handleRunTests}
            />
          )}

          {activeNav === 'forms' && (
            <FormTestingView
              scanResult={scanResult}
              testRun={currentRun}
              testCases={testCases}
              onRunFormTests={handleRunTests}
              isRunning={isRunning}
            />
          )}

          {activeNav === 'journeys' && (
            <UserJourneysView journeys={currentRun?.userJourneys || []} />
          )}

          {activeNav === 'pages' && (
            <SiteMapPagesView
              scanResult={scanResult}
              onScanWebsite={handleScanWebsite}
              isScanning={isScanning}
            />
          )}

          {(activeNav === 'network' || activeNav === 'console') && (
            <NetworkConsoleView
              networkEvents={currentRun?.networkEvents || []}
              consoleEvents={currentRun?.consoleEvents || []}
            />
          )}

          {activeNav === 'runs' && (
            <TestRunsView
              runs={runsHistory}
              onSelectRun={(run) => {
                setCurrentRun(run);
                setActiveNav('dashboard');
              }}
            />
          )}

          {activeNav === 'tests' && (
            <TestCasesView testCases={testCases} />
          )}

          {activeNav === 'failures' && (
            <div className="space-y-6 max-w-7xl mx-auto pb-12">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20">
                  <AlertOctagon className="w-4 h-4" />
                </span>
                <h2 className="text-2xl font-black text-white tracking-tight">
                  Critical & High-Severity Breakdown Catalog
                </h2>
              </div>

              <div className="space-y-4">
                {currentRun?.results.filter(r => r.status === 'failed').map(r => (
                  <div key={r.id} className="p-6 bg-surface/90 backdrop-blur-md border border-red-500/40 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
                    <div className="space-y-1.5">
                      <span className="px-2.5 py-0.5 rounded-md text-[10px] font-black bg-red-500 text-white uppercase">{r.severity}</span>
                      <h3 className="text-lg font-black text-white">{r.testName}</h3>
                      <p className="text-xs text-slate-300">{r.failureInvestigation?.businessImpactSummary}</p>
                    </div>
                    {r.failureInvestigation && (
                      <button
                        onClick={() => setActiveInvestigation(r.failureInvestigation!)}
                        className="px-5 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-2xl text-xs font-bold transition shadow-lg shadow-red-600/30"
                      >
                        Investigate Breakdown
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeNav === 'reports' && (
            <TestRunsView
              runs={runsHistory}
              onSelectRun={(run) => {
                setCurrentRun(run);
                setActiveNav('dashboard');
              }}
            />
          )}

          {(activeNav === 'performance' || activeNav === 'ai' || activeNav === 'settings') && (
            <div className="p-16 text-center max-w-lg mx-auto bg-surface/90 backdrop-blur-md border border-border/80 rounded-3xl space-y-4 shadow-2xl">
              <div className="w-14 h-14 rounded-2xl bg-blue-500/10 text-cyan-400 flex items-center justify-center mx-auto border border-blue-500/20">
                <Cpu className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-extrabold text-white capitalize">{activeNav} Workspace</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Python FastAPI Engine Telemetry is actively recording metrics, memory utilization, and real-time Playwright execution steps.
              </p>
            </div>
          )}
        </main>
      </div>

      <FailureInvestigationModal
        investigation={activeInvestigation}
        onClose={() => setActiveInvestigation(null)}
      />
    </div>
  );
}
