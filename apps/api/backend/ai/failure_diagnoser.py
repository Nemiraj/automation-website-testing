from typing import Optional, List
from ..models import (
    AiFailureAnalysis,
    ConsoleEvent,
    NetworkEvent,
    PriorityLevel,
    SeverityLevel,
    StepExecutionResult
)
from .business_impact import calculate_business_impact


def diagnose_failure(
    test_id: str,
    test_name: str,
    journey_name: Optional[str],
    category: str,
    priority: PriorityLevel,
    severity: SeverityLevel,
    failed_step_index: int,
    total_steps: int,
    failed_step: StepExecutionResult,
    network_events: List[NetworkEvent],
    console_events: List[ConsoleEvent]
) -> AiFailureAnalysis:
    confirmed_facts: List[str] = []
    ai_estimated_causes: List[str] = []
    recommended_investigation: List[str] = []

    # 1. Analyze network events for errors
    failed_api = next(
        (n for n in network_events if n.status >= 500 or n.status in (400, 401, 403, 404) or n.isFailed),
        None
    )
    js_errors = [c for c in console_events if c.type == 'error']

    # Fact collection
    confirmed_facts.append(f'User attempted action: "{failed_step.action.upper()}" on target "{failed_step.targetDescription}".')
    confirmed_facts.append(f'Expected outcome: "{failed_step.expectedResult}".')
    actual_obs = failed_step.actualResult or (failed_step.error.message if failed_step.error else "Action did not yield expected state")
    confirmed_facts.append(f'Actual observation: "{actual_obs}".')

    if failed_api:
        confirmed_facts.append(f'HTTP {failed_api.method} {failed_api.url} responded with status {failed_api.status} ({failed_api.durationMs}ms).')

    if js_errors:
        first_err_snippet = js_errors[0].text[:120]
        confirmed_facts.append(f'Browser recorded {len(js_errors)} JavaScript console error(s): "{first_err_snippet}".')

    likely_cause = ""
    confidence = "Medium"
    confidence_score = 0.82
    user_impact = ""
    suggested_fix = None

    has_api_5xx = (failed_api.status >= 500) if failed_api else False
    has_js_crash = len(js_errors) > 0

    if has_api_5xx and failed_api:
        likely_cause = f'Backend server returned HTTP {failed_api.status} on endpoint {failed_api.url}.'
        confidence = "High"
        confidence_score = 0.94
        user_impact = f'Users attempting this step trigger a server error and are unable to complete the {journey_name or test_name} workflow.'
        ai_estimated_causes.append(f'The backend handler for {failed_api.url} crashed or returned an unhandled 5xx exception during execution.')
        ai_estimated_causes.append('The frontend appropriately submitted payload but was blocked by an upstream API failure.')
        recommended_investigation.append(f'Inspect backend logs for endpoint: {failed_api.url}')
        recommended_investigation.append('Verify database connectivity, payment gateway credentials, or upstream third-party service health.')
        suggested_fix = f'Fix error handling in backend controller for {failed_api.url} and ensure robust fallback response with informative error messages.'
    elif failed_api and failed_api.status in (401, 403):
        likely_cause = f'Authentication or authorization denied on API call ({failed_api.status} {failed_api.url}).'
        confidence = "High"
        confidence_score = 0.92
        user_impact = 'User session is unauthorized or authorization token was missing/expired during the journey.'
        ai_estimated_causes.append('The API rejected request due to missing auth cookies or expired session state.')
        recommended_investigation.append(f'Check session cookie persistence and authentication headers on {failed_api.url}')
        suggested_fix = 'Verify auth middleware token validation and ensure client refreshes authentication state properly.'
    elif failed_api and failed_api.status == 404:
        likely_cause = f'API or asset endpoint not found (HTTP 404 on {failed_api.url}).'
        confidence = "High"
        confidence_score = 0.90
        user_impact = 'Requested resource is missing, preventing page logic from retrieving essential data.'
        ai_estimated_causes.append(f'The target URL {failed_api.url} does not exist or has been renamed/moved.')
        recommended_investigation.append(f'Verify URL route mapping for {failed_api.url}')
        suggested_fix = f'Update API endpoint route or fix client-side URL construction.'
    elif has_js_crash:
        likely_cause = f'Client-side JavaScript runtime exception prevented interaction: {js_errors[0].text[:80]}'
        confidence = "Medium"
        confidence_score = 0.85
        user_impact = 'The user interface became unresponsive or failed to handle DOM event handlers.'
        ai_estimated_causes.append('An unhandled exception in the client JavaScript bundle crashed the component rendering tree.')
        recommended_investigation.append(f'Review browser console stack trace at {js_errors[0].location or "client bundle"}')
        suggested_fix = 'Add proper null-safety checks and React/UI error boundaries around interactive buttons and form handlers.'
    elif (failed_step.error and 'timeout' in failed_step.error.message.lower()) or ('timeout' in failed_step.actualResult.lower()):
        likely_cause = 'Element interaction timed out waiting for selector or navigation change.'
        confidence = "Medium"
        confidence_score = 0.75
        user_impact = 'The application did not respond within the expected threshold, leading to a stalled user experience.'
        ai_estimated_causes.append('The UI element was either not rendered in time, hidden behind a modal/overlay, or navigation was blocked.')
        recommended_investigation.append('Check rendering performance, network waterfall latency, and CSS visibility states.')
        suggested_fix = 'Ensure loading spinners indicate progress and that async DOM updates resolve within acceptable thresholds.'
    else:
        likely_cause = 'State assertion mismatch: UI state did not reflect expected outcome after user action.'
        confidence = "Medium"
        confidence_score = 0.70
        user_impact = f'User completed action "{failed_step.targetDescription}", but the interface did not progress as expected.'
        ai_estimated_causes.append('Form validation might have silently blocked submission without visible feedback.')
        ai_estimated_causes.append('Client routing or state update was skipped or failed silently.')
        recommended_investigation.append('Inspect client form validation schemas and event handlers on the target element.')
        suggested_fix = 'Ensure proper user-visible validation feedback is displayed whenever submission criteria are unmet.'

    impact_calc = calculate_business_impact(
        journey_name=journey_name,
        category=category,
        severity=severity,
        priority=priority,
        is_blocking=True,
        failed_step_index=failed_step_index,
        total_steps=total_steps,
        has_api_5xx_error=has_api_5xx,
        has_js_exception=has_js_crash
    )

    summary = f'{journey_name or test_name} failed at Step {failed_step_index + 1}/{total_steps} ("{failed_step.targetDescription}"). {likely_cause}'

    return AiFailureAnalysis(
        id=f'AI-ANALYSIS-{test_id}',
        testId=test_id,
        summary=summary,
        confirmedFacts=confirmed_facts,
        aiEstimatedCauses=ai_estimated_causes,
        likelyCause=likely_cause,
        confidence=confidence,
        confidenceScore=confidence_score,
        userImpact=user_impact,
        businessImpactScore=impact_calc['score'],
        businessImpactFactors=impact_calc['factors'],
        recommendedInvestigation=recommended_investigation,
        suggestedFix=suggested_fix
    )
