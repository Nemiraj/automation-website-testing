from typing import List, Dict, Any
from backend.app.core.config import settings


SEVERITY_DEDUCTIONS = {
    "critical": 25.0,
    "high": 12.0,
    "medium": 5.0,
    "low": 2.0,
    "info": 0.0
}


def calculate_category_score(issues: List[Dict[str, Any]]) -> float:
    """Calculate score for a category starting from 100 and deducting based on issue severity."""
    score = 100.0
    for issue in issues:
        sev = (issue.get("severity") or "low").lower()
        score -= SEVERITY_DEDUCTIONS.get(sev, 2.0)
    return round(max(0.0, min(100.0, score)), 1)


def calculate_test_scores(all_issues: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Computes deterministic category scores and overall weighted website score.
    """
    # Group issues by category
    ui_issues = [i for i in all_issues if i.get("category") in ("ui", "UI")]
    responsive_issues = [i for i in all_issues if i.get("category") in ("responsive", "Responsive")]
    functional_issues = [i for i in all_issues if i.get("category") in ("functional", "Functional", "javascript", "network")]
    forms_issues = [i for i in all_issues if i.get("category") in ("forms", "Forms")]
    a11y_issues = [i for i in all_issues if i.get("category") in ("accessibility", "Accessibility")]
    perf_issues = [i for i in all_issues if i.get("category") in ("performance", "Performance")]

    ui_score = calculate_category_score(ui_issues)
    responsive_score = calculate_category_score(responsive_issues)
    functional_score = calculate_category_score(functional_issues)
    forms_score = calculate_category_score(forms_issues)
    accessibility_score = calculate_category_score(a11y_issues)
    performance_score = calculate_category_score(perf_issues)

    weights = settings.SCORE_WEIGHTS
    overall_score = (
        ui_score * weights["ui"] +
        responsive_score * weights["responsive"] +
        functional_score * weights["functional"] +
        forms_score * weights["forms"] +
        accessibility_score * weights["accessibility"] +
        performance_score * weights["performance"]
    )
    overall_score = round(max(0.0, min(100.0, overall_score)), 1)

    return {
        "overall": overall_score,
        "ui": ui_score,
        "responsive": responsive_score,
        "functional": functional_score,
        "forms": forms_score,
        "accessibility": accessibility_score,
        "performance": performance_score
    }
