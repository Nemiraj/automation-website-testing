import os
import sys
from urllib.parse import urlparse
from typing import Optional, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from backend.models import (
        AiFailureAnalysis,
        ConsoleEvent,
        NetworkEvent,
        PriorityLevel,
        SeverityLevel,
        StepExecutionResult
    )
    from backend.ai.business_impact import calculate_business_impact
except ImportError:
    try:
        from models import (
            AiFailureAnalysis,
            ConsoleEvent,
            NetworkEvent,
            PriorityLevel,
            SeverityLevel,
            StepExecutionResult
        )
        from ai.business_impact import calculate_business_impact
    except ImportError:
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

    failed_api = next(
        (n for n in network_events if n.status >= 500 or n.status in (400, 401, 403, 404) or n.isFailed),
        None
    )
    js_errors = [c for c in console_events if c.type == 'error']

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
    confidence = "High"
    confidence_score = 0.92
    user_impact = ""
    suggested_fix = None
    where_to_fix = None
    what_to_fix = None
    code_snippet_fix = None

    has_api_5xx = (failed_api.status >= 500) if failed_api else False
    has_api_404 = (failed_api.status == 404) if failed_api else ('404' in actual_obs.lower())
    has_js_crash = len(js_errors) > 0

    parsed_url = urlparse(failed_api.url if failed_api else "")
    endpoint_path = parsed_url.path or "/"
    file_guess = endpoint_path.strip("/").split("/")[-1] or "index.php"

    if has_api_404:
        likely_cause = f'Dead Link or Missing Route: Target resource "{endpoint_path or failed_step.targetDescription}" returned HTTP 404 Not Found.'
        confidence = "High"
        confidence_score = 0.95
        user_impact = f'Clicking this link leads users to a broken 404 page, terminating their journey.'
        ai_estimated_causes.append(f'The route "{endpoint_path}" is not registered in the application\'s router/server, or the link points to a stale/renamed path.')
        ai_estimated_causes.append('A reverse proxy, static file server, or URL-rewrite configuration in front of the app is not forwarding this path correctly.')
        recommended_investigation.append(f'Inspect where this link/href is generated in the frontend and confirm the target path is correct.')
        recommended_investigation.append(f'Verify that a matching route/handler for "{endpoint_path}" is registered in your backend (router, controller, or static file map).')

        where_to_fix = f'Frontend link/navigation source, and the backend route table for "{endpoint_path}"'
        what_to_fix = f'Update the link to point at a valid, currently-registered route, or add/restore the missing "{endpoint_path}" route on the server.'
        code_snippet_fix = f"""# The exact fix depends on your stack. General checklist:
# 1. Grep your frontend source for the literal href/URL string "{endpoint_path}"
#    and confirm it matches a route your backend actually serves.
# 2. Confirm your router (Express/FastAPI/Django/Rails/Next.js/etc.) has a
#    handler registered for "{endpoint_path}" (or the dynamic pattern it maps to).
# 3. If this should be a static asset or rewritten URL, check your web
#    server / reverse proxy config (nginx, Apache, CDN rules) for a rule
#    covering "{endpoint_path}"."""

    elif has_api_5xx and failed_api:
        likely_cause = f'Backend Server Exception: HTTP {failed_api.status} on endpoint "{endpoint_path}".'
        confidence = "High"
        confidence_score = 0.94
        user_impact = f'Server processing failed while handling this action, preventing completion of the {journey_name or test_name} flow.'
        ai_estimated_causes.append(f'The handler for "{endpoint_path}" raised an unhandled exception, hit a database/upstream-service error, or received a payload it did not expect.')
        recommended_investigation.append(f'Check your backend/application server logs for a stack trace around the time of this request to "{endpoint_path}".')
        recommended_investigation.append(f'Verify database connectivity, required environment variables, and the request payload shape expected by "{endpoint_path}".')

        where_to_fix = f'Backend handler/controller for "{endpoint_path}"'
        what_to_fix = f'Add error handling around the logic in the "{endpoint_path}" handler, validate required request parameters before processing, and return a structured error response instead of letting the exception propagate as a 500.'
        code_snippet_fix = f"""# Illustrative — adapt to your actual language/framework:
# try:
#     validate_required_fields(request)   # e.g. required params for "{endpoint_path}"
#     result = handle_request(request)
#     return json_response(result, status=200)
# except ValidationError as e:
#     log.warning(f"Bad request to {endpoint_path}: {{e}}")
#     return json_response({{"error": str(e)}}, status=400)
# except Exception as e:
#     log.exception(f"Unhandled error in {endpoint_path}")
#     return json_response({{"error": "Internal Server Error"}}, status=500)"""

    elif has_js_crash:
        err_msg = js_errors[0].text[:80]
        likely_cause = f'JavaScript Client Runtime Error: "{err_msg}".'
        confidence = "High"
        confidence_score = 0.90
        user_impact = 'A JavaScript error halted client-side execution, rendering buttons or dropdowns unresponsive.'
        ai_estimated_causes.append('A script attempted to access properties of `undefined` or a referenced DOM element was not found.')
        recommended_investigation.append(f'Review browser script at {js_errors[0].location or "JS bundle"}')

        where_to_fix = f'{js_errors[0].location or "custom.js / main.js script"}'
        what_to_fix = 'Wrap DOM element lookups in null checks (e.g. `if (element) { ... }`) to ensure elements exist before attaching event listeners.'
        code_snippet_fix = """// In your JavaScript file:
document.addEventListener('DOMContentLoaded', function() {
    const targetBtn = document.querySelector('.btn-submit');
    if (targetBtn) {
        targetBtn.addEventListener('click', function(e) {
            // Safe handler execution
        });
    }
});"""

    elif (failed_step.error and 'timeout' in failed_step.error.message.lower()) or ('timeout' in actual_obs.lower()):
        likely_cause = f'Selector / Interaction Timeout: Could not find or interact with "{failed_step.targetDescription}".'
        confidence = "Medium"
        confidence_score = 0.80
        user_impact = 'The interface did not render the expected element within the allotted timeout.'
        ai_estimated_causes.append('The element class, ID, or text attribute was changed or is conditionally rendered after an async delay.')
        recommended_investigation.append('Inspect the rendered DOM to verify class names and IDs on the interactive element.')

        where_to_fix = f'Template file for page: {endpoint_path}'
        what_to_fix = f'Ensure the target element has a unique, stable ID or data-testid attribute for reliable interaction.'
        code_snippet_fix = f"""<!-- Add stable ID to element: -->
<button type="submit" id="submit-btn" class="btn-style-one">
    Submit
</button>"""

    else:
        likely_cause = f'Form Validation / Assertion Mismatch: "{failed_step.targetDescription}".'
        confidence = "Medium"
        confidence_score = 0.75
        user_impact = f'User completed action "{failed_step.targetDescription}", but state did not advance.'
        ai_estimated_causes.append('Form submission may lack a valid `action` URL, or required field validation was blocked.')
        recommended_investigation.append('Check form `<form method="POST" action="...">` attributes and submit button type.')

        where_to_fix = f'Form HTML markup on {endpoint_path}'
        what_to_fix = 'Ensure the `<form>` tag has a valid `action` attribute pointing to an active PHP endpoint and input fields have `name` attributes.'
        code_snippet_fix = """<!-- In your form: -->
<form method="POST" action="process-form.php">
    <input type="text" name="name" required placeholder="Your Name">
    <input type="email" name="email" required placeholder="Your Email">
    <button type="submit" class="btn-style-one">Submit</button>
</form>"""

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
        suggestedFix=suggested_fix or what_to_fix,
        whereToFix=where_to_fix,
        whatToFix=what_to_fix,
        codeSnippetFix=code_snippet_fix
    )
