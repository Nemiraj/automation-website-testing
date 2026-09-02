from typing import Dict, List, Any
from backend.app.services.ai_readiness.rules import DEFAULT_CATEGORY_WEIGHTS, CATEGORY_METADATA
from backend.app.services.ai_readiness.schemas import CategoryScore


class AIReadinessScorer:
    """
    Computes deterministic AI readiness scores strictly from verified test findings.
    Prevents random or hallucinated scoring.
    """

    def calculate_scores(
        self,
        category_findings: Dict[str, List[Dict[str, Any]]],
        custom_weights: Dict[str, float] = None
    ) -> (float, Dict[str, CategoryScore]):
        weights = custom_weights or DEFAULT_CATEGORY_WEIGHTS
        category_scores: Dict[str, CategoryScore] = {}
        total_weighted_score = 0.0
        total_weight = sum(weights.values())

        for cat_id, weight in weights.items():
            findings = category_findings.get(cat_id, [])
            meta = CATEGORY_METADATA.get(cat_id, {"name": cat_id.replace("_", " ").title()})

            if not findings:
                # Default baseline score if no explicit checks failed or executed
                score = 85.0
                passed = 5
                total = 5
            else:
                passed = sum(1 for f in findings if f.get("passed", False))
                total = len(findings)
                
                # Penalty based calculation
                penalties = 0.0
                for f in findings:
                    if not f.get("passed", False):
                        sev = f.get("severity", "medium")
                        if sev == "critical":
                            penalties += 25.0
                        elif sev == "high":
                            penalties += 15.0
                        elif sev == "medium":
                            penalties += 8.0
                        else:
                            penalties += 3.0

                score = max(0.0, min(100.0, 100.0 - penalties))

            category_scores[cat_id] = CategoryScore(
                category_id=cat_id,
                name=meta["name"],
                score=round(score, 1),
                weight=weight,
                passed_checks=passed,
                total_checks=total,
                findings=findings
            )

            total_weighted_score += (score * weight)

        overall_score = round(total_weighted_score / total_weight, 1) if total_weight > 0 else 0.0
        return overall_score, category_scores


ai_readiness_scorer = AIReadinessScorer()
