import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Loader2, 
  CheckCircle2, 
  AlertOctagon, 
  ArrowRight, 
  ExternalLink, 
  Terminal,
  Clock
} from 'lucide-react';
import { ProgressBar } from '../components/ProgressBar';
import { TestService } from '../services/api';
import { TestRun } from '../types';

export const LiveProgress: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [test, setTest] = useState<TestRun | null>(null);
  const [logs, setLogs] = useState<Array<{ time: string; message: string; stage: string }>>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    // Initial fetch
    TestService.getStatus(id)
      .then((data) => {
        setTest(data);
        if (data.status === 'completed') {
          navigate(`/tests/${id}/report`);
        }
      })
      .catch((err) => setError('Failed to fetch test run details.'));

    // Connect to Server-Sent Events (SSE) stream
    const eventSource = new EventSource(`/api/tests/${id}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setTest(prev => ({
          ...(prev || {}),
          ...data,
          target_url: data.current_page_url || prev?.target_url || '',
          status: data.status,
          progress_percentage: data.progress_percentage,
          current_stage: data.current_stage,
          current_page_url: data.current_page_url,
          error_message: data.error_message,
        } as TestRun));

        setLogs(prev => [
          ...prev,
          {
            time: new Date().toLocaleTimeString(),
            message: data.current_page_url ? `Inspecting ${data.current_page_url}` : data.current_stage,
            stage: data.current_stage
          }
        ]);

        if (data.status === 'completed') {
          eventSource.close();
          setTimeout(() => navigate(`/tests/${id}/report`), 1200);
        } else if (data.status === 'failed') {
          eventSource.close();
          setError(data.error_message || 'Test execution failed.');
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    eventSource.onerror = () => {
      // Fallback to polling every 2.5s if SSE disconnects
      const interval = setInterval(async () => {
        try {
          const updated = await TestService.getStatus(id);
          setTest(updated);
          if (updated.status === 'completed') {
            clearInterval(interval);
            navigate(`/tests/${id}/report`);
          } else if (updated.status === 'failed') {
            clearInterval(interval);
            setError(updated.error_message || 'Test execution failed.');
          }
        } catch (e) {
          console.error(e);
        }
      }, 2500);

      return () => clearInterval(interval);
    };

    return () => {
      eventSource.close();
    };
  }, [id, navigate]);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-ping"></span>
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                Automated Test In Progress
              </span>
            </div>
            <h1 className="text-xl font-extrabold text-white font-mono truncate">
              {test?.target_url || 'Target Website'}
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <span className="rounded-lg bg-slate-800 px-3 py-1.5 text-xs font-mono text-slate-300 border border-slate-700">
              ID: {id?.slice(0, 8)}
            </span>
          </div>
        </div>

        {/* Progress Bar & Stage Grid */}
        <ProgressBar
          percentage={test?.progress_percentage || 0}
          currentStage={test?.current_stage || 'Initializing browser...'}
          currentPageUrl={test?.current_page_url}
          status={test?.status || 'running'}
        />

        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-400 text-xs flex items-center gap-2">
            <AlertOctagon className="h-4 w-4" />
            <span>{error}</span>
          </div>
        )}

        {test?.status === 'completed' && (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold">
              <CheckCircle2 className="h-4 w-4" />
              <span>Test successfully finished! Redirecting to report...</span>
            </div>
            <Link
              to={`/tests/${id}/report`}
              className="flex items-center gap-1 text-xs font-bold text-emerald-400 hover:underline"
            >
              View Report <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        )}
      </div>

      {/* Live Log Stream */}
      <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6 space-y-4 font-mono shadow-inner">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <Terminal className="h-4 w-4 text-emerald-400" />
            <span>Real-Time Execution Logs</span>
          </div>
          <span className="text-[11px] text-slate-400 flex items-center gap-1">
            <Clock className="h-3 w-3" /> Live
          </span>
        </div>

        <div className="space-y-2 max-h-64 overflow-y-auto text-xs">
          {logs.length === 0 ? (
            <p className="text-slate-400 italic">Initializing Playwright Chromium headless engine...</p>
          ) : (
            logs.slice(-15).map((log, idx) => (
              <div key={idx} className="flex items-start gap-3 text-slate-300">
                <span className="text-slate-400 text-[10px] select-none">{log.time}</span>
                <span className="text-emerald-400 font-semibold select-none">[{log.stage}]</span>
                <span className="text-slate-200 truncate">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
