import os
import sys
from typing import Optional, Dict, Any, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from backend.models import TestRun, TestResult
except ImportError:
    try:
        from models import TestRun, TestResult
    except ImportError:
        from ..models import TestRun, TestResult


def compare_test_runs(current_run: TestRun, previous_run: Optional[TestRun] = None) -> Optional[Dict[str, Any]]:
    if not previous_run:
        return None

    prev_map: Dict[str, TestResult] = {res.testCaseId: res for res in previous_run.results}

    new_failures: List[TestResult] = []
    continuing_failures: List[TestResult] = []
    new_warnings: List[TestResult] = []
    fixed_failures: List[TestResult] = []

    for curr in current_run.results:
        prev = prev_map.get(curr.testCaseId)

        if curr.status == 'failed':
            if not prev or prev.status == 'passed':
                new_failures.append(curr)
            elif prev.status == 'failed':
                continuing_failures.append(curr)
        elif curr.status == 'warning':
            if not prev or prev.status != 'warning':
                new_warnings.append(curr)
        elif curr.status == 'passed':
            if prev and prev.status == 'failed':
                fixed_failures.append(curr)

    prev_perf = previous_run.performanceMetrics.pageLoadTimeMs if previous_run.performanceMetrics else 0
    curr_perf = current_run.performanceMetrics.pageLoadTimeMs if current_run.performanceMetrics else 0
    perf_delta = curr_perf - prev_perf

    return {
        'previousRunId': previous_run.id,
        'previousHealthScore': previous_run.healthScore,
        'currentHealthScore': current_run.healthScore,
        'healthDelta': current_run.healthScore - previous_run.healthScore,
        'newFailures': new_failures,
        'fixedFailures': fixed_failures,
        'continuingFailures': continuing_failures,
        'newWarnings': new_warnings,
        'performanceDeltaMs': perf_delta,
        'summary': {
            'newFailuresCount': len(new_failures),
            'fixedFailuresCount': len(fixed_failures),
            'continuingFailuresCount': len(continuing_failures),
            'newWarningsCount': len(new_warnings)
        }
    }
