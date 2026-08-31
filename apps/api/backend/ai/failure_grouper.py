from urllib.parse import urlparse
from typing import List, Dict, Any
from ..models import FailureGroup, TestResult, SeverityLevel


def group_failures(results: List[TestResult]) -> List[FailureGroup]:
    failed_results = [r for r in results if r.status == 'failed' and r.failureInvestigation]
    if not failed_results:
        return []

    groups_map: Dict[str, Dict[str, Any]] = {}

    for res in failed_results:
        inv = res.failureInvestigation
        if not inv:
            continue

        api_5xx = next((n for n in inv.relatedApiFailures if n.status >= 500), None)
        api_4xx = next((n for n in inv.relatedApiFailures if 400 <= n.status < 500), None)
        js_crash = next((c for c in inv.relatedConsoleErrors if c.type == 'error'), None)

        if api_5xx:
            parsed = urlparse(api_5xx.url)
            path = parsed.path or '/'
            group_key = f'API_5XX_{api_5xx.method}_{path}_{api_5xx.status}'
            title = f'Backend Server Error on {api_5xx.method} {path} ({api_5xx.status})'
            root_cause_type = 'API_5XX'
            primary_evidence = f'{api_5xx.method} {api_5xx.url} returned HTTP {api_5xx.status}'
        elif api_4xx:
            parsed = urlparse(api_4xx.url)
            path = parsed.path or '/'
            group_key = f'API_4XX_{api_4xx.method}_{path}_{api_4xx.status}'
            title = f'API Client/Auth Error on {api_4xx.method} {path} ({api_4xx.status})'
            root_cause_type = 'API_4XX'
            primary_evidence = f'{api_4xx.method} {api_4xx.url} returned HTTP {api_4xx.status}'
        elif js_crash:
            simplified_msg = js_crash.text[:40]
            group_key = f'JS_CRASH_{simplified_msg}'
            title = f'Unhandled JavaScript Crash: "{simplified_msg}..."'
            root_cause_type = 'JS_CRASH'
            primary_evidence = js_crash.text
        elif 'timeout' in inv.actual.lower() or 'waiting for' in inv.actual.lower():
            group_key = f'TIMEOUT_{inv.failedPageUrl}'
            title = f'Navigation or Selector Timeout on {inv.failedPageUrl}'
            root_cause_type = 'TIMEOUT'
            primary_evidence = inv.actual
        else:
            group_key = f'ASSERTION_{inv.failedPageUrl}_{inv.userAction}'
            title = f'Failed Interaction: "{inv.userAction}" on {inv.failedPageUrl}'
            root_cause_type = 'ASSERTION_MISMATCH'
            primary_evidence = f'Expected "{inv.expected}", but got "{inv.actual}"'

        if group_key not in groups_map:
            groups_map[group_key] = {
                'title': title,
                'rootCauseType': root_cause_type,
                'primaryEvidence': primary_evidence,
                'affectedTestIds': [res.testCaseId],
                'affectedTestNames': [res.testName],
                'impactScore': inv.businessImpactScore,
                'severity': inv.severity
            }
        else:
            existing = groups_map[group_key]
            existing['affectedTestIds'].append(res.testCaseId)
            existing['affectedTestNames'].append(res.testName)
            existing['impactScore'] = max(existing['impactScore'], inv.businessImpactScore)
            if inv.severity == 'CRITICAL':
                existing['severity'] = 'CRITICAL'

    groups: List[FailureGroup] = []
    for idx, (key, item) in enumerate(groups_map.items()):
        groups.append(FailureGroup(
            id=f'GRP-{idx + 1}',
            title=item['title'],
            rootCauseType=item['rootCauseType'],
            primaryEvidence=item['primaryEvidence'],
            affectedCount=len(item['affectedTestIds']),
            affectedTestIds=item['affectedTestIds'],
            affectedTestNames=item['affectedTestNames'],
            severity=item['severity'],
            impactScore=item['impactScore']
        ))

    return groups
