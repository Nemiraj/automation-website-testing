import os
import sys
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from backend.models import TestRun
except ImportError:
    try:
        from models import TestRun
    except ImportError:
        from ..models import TestRun


class HtmlReportGenerator:
    @staticmethod
    def generate(test_run: TestRun) -> str:
        health_color = '#10b981' if test_run.healthScore >= 80 else '#f59e0b' if test_run.healthScore >= 50 else '#ef4444'
        failed_results = [r for r in test_run.results if r.status == 'failed']

        date_str = test_run.completedAt or test_run.startedAt
        try:
            formatted_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime("%b %d, %Y, %I:%M:%S %p UTC")
        except Exception:
            formatted_date = date_str

        failures_html = ""
        if failed_results:
            failures_html = '<h2 class="section-title" style="color: var(--danger);">🚨 Critical Failures & Business Impact</h2>'
            for res in failed_results:
                inv = res.failureInvestigation
                if not inv:
                    continue
                investigations_str = " • ".join(inv.aiAnalysis.recommendedInvestigation)
                failures_html += f"""
                <div class="failure-card">
                  <div class="failure-header">
                    <div>
                      <span class="badge badge-critical">{inv.severity}</span>
                      <span class="badge badge-warning" style="margin-left: 8px;">{inv.priority}</span>
                      <strong style="font-size: 18px; margin-left: 12px;">{res.testName}</strong>
                    </div>
                    <div style="font-weight: 700; color: #f87171;">Impact Score: {inv.businessImpactScore}/100</div>
                  </div>

                  <p style="color: #cbd5e1; margin-bottom: 12px;"><strong>User Impact:</strong> {inv.businessImpactSummary}</p>

                  <div class="expected-actual">
                    <div class="exp-box">
                      <div style="font-size: 12px; color: #60a5fa; font-weight: 700; text-transform: uppercase;">Expected Outcome</div>
                      <div style="margin-top: 6px; font-size: 14px;">{inv.expected}</div>
                    </div>
                    <div class="act-box">
                      <div style="font-size: 12px; color: #f87171; font-weight: 700; text-transform: uppercase;">Actual Failure State</div>
                      <div style="margin-top: 6px; font-size: 14px;">{inv.actual}</div>
                    </div>
                  </div>

                  <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 8px; margin-top: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
                    <div style="font-size: 13px; font-weight: 700; color: #34d399; margin-bottom: 8px;">🛠️ EXACT FIX & SOLUTION GUIDE:</div>
                    {f'<div style="font-size: 12px; color: #38bdf8; margin-bottom: 4px;"><strong>📍 Where to Fix:</strong> <span class="code-pill">{inv.aiAnalysis.whereToFix}</span></div>' if inv.aiAnalysis.whereToFix else ''}
                    {f'<div style="font-size: 13px; color: #f8fafc; margin-bottom: 6px;"><strong>💡 What to Fix:</strong> {inv.aiAnalysis.whatToFix}</div>' if inv.aiAnalysis.whatToFix else ''}
                    {f'<pre style="background: #000; color: #34d399; padding: 10px; border-radius: 6px; font-size: 12px; overflow-x: auto; margin-top: 8px;">{inv.aiAnalysis.codeSnippetFix}</pre>' if inv.aiAnalysis.codeSnippetFix else ''}
                    <div style="font-size: 12px; color: #94a3b8; margin-top: 8px;">Root Cause: {inv.aiAnalysis.likelyCause}</div>
                  </div>
                </div>
                """

        journeys_rows = ""
        for j in test_run.userJourneys:
            badge_cls = "badge-success" if j.status == 'passed' else "badge-critical"
            impact_color = "var(--danger)" if j.businessImpactScore > 70 else "var(--text)"
            steps_html = "".join([
                f'<span class="journey-step {s.status}">{s.name} {"✓" if s.status == "passed" else "✗"}</span>'
                for s in j.steps
            ])
            journeys_rows += f"""
            <tr>
              <td><strong>{j.name}</strong></td>
              <td><span class="code-pill">{j.category}</span></td>
              <td><span class="badge {badge_cls}">{j.status}</span></td>
              <td>{j.completedSteps} / {j.totalSteps}</td>
              <td><strong style="color: {impact_color};">{j.businessImpactScore}/100</strong></td>
              <td>{steps_html}</td>
            </tr>
            """

        results_rows = ""
        for r in test_run.results:
            status_badge = "badge-success" if r.status == 'passed' else "badge-warning" if r.status == 'recovered' else "badge-critical"
            results_rows += f"""
            <tr>
              <td><span class="code-pill">{r.testCaseId}</span></td>
              <td><strong>{r.testName}</strong></td>
              <td><span class="badge badge-warning">{r.priority}</span></td>
              <td><span class="badge {status_badge}">{r.status}</span></td>
              <td>{r.durationMs}ms</td>
              <td><span style="color: var(--text-muted); font-size: 13px;">{r.url}</span></td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QA Executive Report — {test_run.websiteUrl} ({test_run.id})</title>
  <style>
    :root {{
      --bg: #0b0f19;
      --card: #131b2e;
      --card-border: #1e293b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background-color: var(--bg); color: var(--text); padding: 32px 16px; line-height: 1.5; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    .header {{ display: flex; justify-content: space-between; align-items: center; padding-bottom: 24px; border-bottom: 1px solid var(--card-border); margin-bottom: 32px; flex-wrap: wrap; gap: 16px; }}
    .badge {{ display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
    .badge-critical {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }}
    .badge-success {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }}
    .badge-warning {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 32px; }}
    .card {{ background: var(--card); border: 1px solid var(--card-border); border-radius: 12px; padding: 24px; }}
    .metric-value {{ font-size: 36px; font-weight: 700; margin: 8px 0; }}
    .metric-label {{ font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
    .section-title {{ font-size: 20px; font-weight: 700; margin: 32px 0 16px 0; display: flex; align-items: center; gap: 8px; }}
    .failure-card {{ background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
    .failure-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
    .table-container {{ overflow-x: auto; background: var(--card); border: 1px solid var(--card-border); border-radius: 12px; margin-bottom: 32px; }}
    table {{ width: 100%; border-collapse: collapse; text-align: left; }}
    th {{ padding: 14px 18px; border-bottom: 1px solid var(--card-border); color: var(--text-muted); font-size: 13px; text-transform: uppercase; }}
    td {{ padding: 14px 18px; border-bottom: 1px solid var(--card-border); font-size: 14px; }}
    .journey-step {{ display: inline-flex; align-items: center; font-size: 13px; padding: 4px 8px; border-radius: 6px; margin: 2px; }}
    .journey-step.passed {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}
    .journey-step.failed {{ background: rgba(239, 68, 68, 0.2); color: #f87171; font-weight: 600; }}
    .journey-step.recovered {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; }}
    .expected-actual {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0; }}
    .exp-box {{ background: #0f172a; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #3b82f6; }}
    .act-box {{ background: #0f172a; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #ef4444; }}
    .code-pill {{ font-family: monospace; background: #1e293b; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <div style="font-size: 12px; color: var(--primary); font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;">WebTest AI • Autonomous Python QA Platform</div>
        <h1 style="font-size: 28px; font-weight: 800; margin-top: 4px;">Executive QA Test Report</h1>
        <p style="color: var(--text-muted); font-size: 14px; margin-top: 4px;">Tested URL: <a href="{test_run.websiteUrl}" style="color: var(--primary); text-decoration: none;" target="_blank">{test_run.websiteUrl}</a></p>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 12px; color: var(--text-muted);">Run ID: <span class="code-pill">{test_run.id}</span></div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Generated: {formatted_date}</div>
      </div>
    </div>

    <div class="grid">
      <div class="card" style="border-top: 4px solid {health_color};">
        <div class="metric-label">Website Health Score</div>
        <div class="metric-value" style="color: {health_color};">{test_run.healthScore}%</div>
        <div style="font-size: 13px; color: var(--text-muted);">{"Optimal User Flow" if test_run.healthScore >= 80 else "Severe Friction" if test_run.healthScore >= 50 else "Critical Breakdown"}</div>
      </div>

      <div class="card">
        <div class="metric-label">Total Test Cases</div>
        <div class="metric-value">{test_run.totalTests}</div>
        <div style="font-size: 13px; color: var(--text-muted);"><span style="color: var(--success); font-weight: 600;">{test_run.passedTests} Passed</span> • <span style="color: var(--danger); font-weight: 600;">{test_run.failedTests} Failed</span></div>
      </div>

      <div class="card">
        <div class="metric-label">Critical Revenue Blockers</div>
        <div class="metric-value" style="color: {'var(--danger)' if test_run.criticalFailures > 0 else 'var(--success)'};">{test_run.criticalFailures}</div>
        <div style="font-size: 13px; color: var(--text-muted);">{"Urgent Engineering Action Required" if test_run.criticalFailures > 0 else "No Critical Path Blockers"}</div>
      </div>

      <div class="card">
        <div class="metric-label">Total Duration</div>
        <div class="metric-value">{(test_run.durationMs / 1000):.1f}s</div>
        <div style="font-size: 13px; color: var(--text-muted);">Execution completed across Python Playwright engine</div>
      </div>
    </div>

    {failures_html}

    <h2 class="section-title">🧭 Key User Journeys</h2>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>User Journey</th>
            <th>Category</th>
            <th>Status</th>
            <th>Completed Steps</th>
            <th>Business Impact</th>
            <th>Journey Progression</th>
          </tr>
        </thead>
        <tbody>
          {journeys_rows}
        </tbody>
      </table>
    </div>

    <h2 class="section-title">📋 Complete Test Results</h2>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Test Name</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Page URL</th>
          </tr>
        </thead>
        <tbody>
          {results_rows}
        </tbody>
      </table>
    </div>

    <div style="text-align: center; color: var(--text-muted); font-size: 13px; margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--card-border);">
      WebTest AI Python QA Engine • Built for Automated User-Centric Verification
    </div>
  </div>
</body>
</html>"""
        return html
