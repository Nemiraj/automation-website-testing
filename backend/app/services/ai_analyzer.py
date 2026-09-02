import json
import httpx
from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.core.logging import logger


class AIAnalyzer:
    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        self.base_url = settings.AI_BASE_URL

    def _generate_heuristic_synthesis(
        self,
        target_url: str,
        issues: List[Dict[str, Any]],
        scores: Dict[str, float],
        target_type: str = "live",
        environment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fallback expert synthesizer that generates structured recommendations based strictly
        on deterministic evidence when external AI API is unavailable.
        """
        critical_count = sum(1 for i in issues if i.get("severity") == "critical")
        high_count = sum(1 for i in issues if i.get("severity") == "high")
        env = environment or {}
        
        # Determine priority actions
        priority_actions = []
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_issues = sorted(issues, key=lambda x: sev_order.get(x.get("severity", "low"), 5))

        seen_action_titles = set()
        for iss in sorted_issues:
            if len(priority_actions) >= 5:
                break
            rec = iss.get("recommendation") or iss.get("title")
            if rec and rec not in seen_action_titles:
                seen_action_titles.add(rec)
                priority_actions.append(f"{iss.get('title')}: {rec}")

        if not priority_actions:
            priority_actions.append("Website passed all standard automated tests with high compliance.")

        env_str = f" [{env.get('environment', 'Localhost')}: {env.get('server', '')} / {env.get('technology', '')}]" if target_type == "localhost" else ""
        summary = (
            f"Automated scan completed for {target_url}{env_str} with an overall health score of {scores.get('overall', 100)}/100. "
            f"Identified {len(issues)} total findings ({critical_count} critical, {high_count} high priority). "
            f"The primary areas requiring attention are {', '.join([k for k, v in scores.items() if k != 'overall' and v < 85]) or 'general maintenance'}."
        )

        issues_analysis = []
        for iss in sorted_issues[:15]:
            issues_analysis.append({
                "title": iss.get("title"),
                "severity": iss.get("severity"),
                "category": iss.get("category"),
                "why": iss.get("why_it_matters") or "Impacts user experience and application stability.",
                "recommendation": iss.get("recommendation") or "Review and resolve this finding in source code or server configuration.",
                "suggested_fix": iss.get("suggested_fix") or f"Inspect selector {iss.get('selector', 'element')}."
            })

        return {
            "summary": summary,
            "issues": issues_analysis,
            "priority_actions": priority_actions,
            "model_used": "Deterministic Expert Synthesizer"
        }

    async def analyze_test_run(
        self,
        target_url: str,
        issues: List[Dict[str, Any]],
        scores: Dict[str, float],
        pages_count: int,
        target_type: str = "live",
        environment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sends structured test evidence to AI model to generate human-readable recommendations.
        """
        if not self.api_key:
            logger.info("AI_API_KEY not configured. Using deterministic expert synthesizer.")
            return self._generate_heuristic_synthesis(target_url, issues, scores, target_type, environment)

        # Prepare sanitized structured payload
        evidence_payload = {
            "target_url": target_url,
            "target_type": target_type,
            "environment": environment or {},
            "overall_score": scores.get("overall"),
            "category_scores": scores,
            "pages_scanned": pages_count,
            "total_issues": len(issues),
            "issues": [
                {
                    "title": i.get("title"),
                    "category": i.get("category"),
                    "severity": i.get("severity"),
                    "page_url": i.get("page_url"),
                    "selector": i.get("selector"),
                    "viewport": i.get("viewport"),
                    "description": i.get("description"),
                    "evidence": i.get("evidence")
                }
                for i in issues[:25]  # Limit to top 25 issues for token efficiency
            ]
        }

        system_prompt = (
            "You are a Senior QA Automation Architect specializing in web application auditing, "
            "PHP/XAMPP architectures, and UI/UX health. Given structured test findings from a real website test, "
            "provide an executive diagnosis and concrete technical fix recommendations. "
            "IMPORTANT: Do not invent any non-existent selectors, errors, or fake source code lines unless explicitly given in the evidence. "
            "Output MUST be valid JSON with keys: 'summary', 'issues' (list with title, severity, category, why, recommendation, suggested_fix), "
            "and 'priority_actions' (list of top 5 urgent fixes)."
        )

        try:
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            body = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{system_prompt}\n\nStructured Evidence:\n{json.dumps(evidence_payload, indent=2)}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2
                }
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        parsed_json = json.loads(text_content)
                        parsed_json["model_used"] = self.model
                        return parsed_json

            logger.warning(f"AI API request returned status {resp.status_code if 'resp' in locals() else 'error'}. Falling back to synthesizer.")
            return self._generate_heuristic_synthesis(target_url, issues, scores, target_type, environment)

        except Exception as e:
            logger.error(f"Error calling AI Analyzer API: {e}")
            return self._generate_heuristic_synthesis(target_url, issues, scores, target_type, environment)

