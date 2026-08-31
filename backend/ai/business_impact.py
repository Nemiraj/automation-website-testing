import os
import sys
from typing import Optional, List, Dict, Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from backend.models import SeverityLevel, PriorityLevel, BusinessImpactFactor
except ImportError:
    try:
        from models import SeverityLevel, PriorityLevel, BusinessImpactFactor
    except ImportError:
        from ..models import SeverityLevel, PriorityLevel, BusinessImpactFactor


def calculate_business_impact(
    journey_name: Optional[str] = None,
    category: str = "",
    severity: SeverityLevel = "HIGH",
    priority: PriorityLevel = "P1",
    is_blocking: bool = True,
    failed_step_index: int = 0,
    total_steps: int = 1,
    has_api_5xx_error: bool = False,
    has_js_exception: bool = False
) -> Dict[str, Any]:
    factors: List[BusinessImpactFactor] = []
    base_score = 20

    lower_journey = (journey_name or category or "").lower()
    if any(k in lower_journey for k in ['checkout', 'payment', 'purchase', 'subscription', 'stream', 'play', 'movie']):
        base_score += 35
        factors.append(BusinessImpactFactor(
            factor='Core Revenue & Media Consumption Journey',
            weight=35,
            description='Blocks checkout, payment processing, or media playback, directly halting transactions and critical customer experience.'
        ))
    elif any(k in lower_journey for k in ['login', 'auth', 'register', 'signin', 'signup']):
        base_score += 30
        factors.append(BusinessImpactFactor(
            factor='Authentication & Account Access',
            weight=30,
            description='Blocks user authentication or registration, preventing user entry into protected features.'
        ))
    elif any(k in lower_journey for k in ['cart', 'search', 'order', 'catalog', 'browse']):
        base_score += 20
        factors.append(BusinessImpactFactor(
            factor='Primary Conversion Funnel',
            weight=20,
            description='Affects product/content discovery, cart manipulation, or search catalog workflows.'
        ))
    else:
        base_score += 10
        factors.append(BusinessImpactFactor(
            factor='Standard User Interaction',
            weight=10,
            description='Affects standard informational or contact workflows.'
        ))

    # Priority & Severity
    if priority == 'P0' or severity == 'CRITICAL':
        base_score += 25
        factors.append(BusinessImpactFactor(
            factor='Critical Severity (P0)',
            weight=25,
            description='Application unusable or major business-critical workflow is completely severed.'
        ))
    elif priority == 'P1' or severity == 'HIGH':
        base_score += 15
        factors.append(BusinessImpactFactor(
            factor='High Priority (P1)',
            weight=15,
            description='Major feature broken with no obvious user workaround.'
        ))
    elif severity == 'MEDIUM':
        base_score += 5
        factors.append(BusinessImpactFactor(
            factor='Medium Priority (P2)',
            weight=5,
            description='Feature impairment or validation failure under specific conditions.'
        ))

    # Blocking nature & late funnel step
    if is_blocking:
        base_score += 10
        factors.append(BusinessImpactFactor(
            factor='Hard Blocker',
            weight=10,
            description='User cannot proceed to subsequent steps in the journey.'
        ))

    if total_steps > 1 and failed_step_index >= int(total_steps * 0.6):
        base_score += 5
        factors.append(BusinessImpactFactor(
            factor='Deep Funnel Dropoff',
            weight=5,
            description=f'Failed at step {failed_step_index + 1} of {total_steps}, after user already invested high engagement.'
        ))

    # Server-side failure vs client error
    if has_api_5xx_error:
        base_score += 5
        factors.append(BusinessImpactFactor(
            factor='Backend Server Failure',
            weight=5,
            description='Server returned HTTP 5xx error, indicating backend infrastructure failure rather than client validation.'
        ))
    elif has_js_exception:
        base_score += 3
        factors.append(BusinessImpactFactor(
            factor='Uncaught Script Exception',
            weight=3,
            description='JavaScript runtime crash occurred during client execution.'
        ))

    final_score = min(100, max(1, base_score))

    if final_score >= 85:
        summary = 'Critical business interruption: Directly blocks customer revenue or access for all affected users.'
    elif final_score >= 65:
        summary = 'High operational impact: Disrupts key user journeys and likely degrades conversion rates.'
    elif final_score >= 40:
        summary = 'Moderate impact: Causes friction in standard workflows but secondary paths may exist.'
    else:
        summary = 'Low impact: Cosmetic or minor defect with minimal interruption to business operations.'

    return {
        'score': final_score,
        'factors': factors,
        'summary': summary
    }
