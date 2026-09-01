import pytest
from backend.app.services.scoring import calculate_category_score, calculate_test_scores


def test_calculate_category_score_clean():
    # No issues should result in 100
    assert calculate_category_score([]) == 100.0


def test_calculate_category_score_deductions():
    issues = [
        {"severity": "critical"},  # -25
        {"severity": "high"},      # -12
        {"severity": "medium"},    # -5
        {"severity": "low"}        # -2
    ]
    # 100 - (25 + 12 + 5 + 2) = 56.0
    assert calculate_category_score(issues) == 56.0


def test_calculate_test_scores_weighted():
    all_issues = [
        {"category": "ui", "severity": "high"},          # UI: 88
        {"category": "responsive", "severity": "critical"}, # Resp: 75
        {"category": "functional", "severity": "medium"},   # Func: 95
        {"category": "forms", "severity": "low"},          # Forms: 98
        {"category": "accessibility", "severity": "high"},  # A11y: 88
        {"category": "performance", "severity": "medium"}   # Perf: 95
    ]
    scores = calculate_test_scores(all_issues)
    assert scores["ui"] == 88.0
    assert scores["responsive"] == 75.0
    assert 0 <= scores["overall"] <= 100.0
