from typing import List, Dict, Any, Optional
from backend.app.core.logging import logger


class ReportSolutionEngine:
    """
    Analyzes the complete multi-module audit report and generates a prioritized,
    dependency-aware developer action plan with root-cause diagnoses and concrete code diffs.
    """

    def generate_solution_plan(
        self,
        test_id: str,
        target_url: str,
        all_issues: List[Dict[str, Any]],
        ai_readiness_data: Dict[str, Any],
        local_source_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes all findings into a structured Action Plan.
        """
        action_plan: List[Dict[str, Any]] = []

        # 1. Identify Cascading Dependencies (e.g. Database / Server Error -> Form Failure)
        server_issues = [i for i in all_issues if "database" in i.get("title", "").lower() or "php" in i.get("title", "").lower() or i.get("severity") == "critical"]
        form_issues = [i for i in all_issues if i.get("category") == "forms"]

        has_server_db_error = len(server_issues) > 0

        # Step 1: Server / PHP / DB Errors (Highest Dependency)
        for s_iss in server_issues:
            action_plan.append({
                "id": f"sol_{len(action_plan) + 1}",
                "priority": "critical",
                "category": "Backend & Server",
                "title": f"Resolve Server Error: {s_iss.get('title')}",
                "problem": s_iss.get("description", "Server-level exception detected during page execution."),
                "evidence": {
                    "page_url": s_iss.get("page_url"),
                    "selector": s_iss.get("selector"),
                    "screenshot_url": s_iss.get("screenshot_url"),
                    "annotated_screenshot_url": s_iss.get("annotated_screenshot_url")
                },
                "root_cause": "PHP runtime exception or MySQL database authentication/connection failure.",
                "root_cause_confidence": "HIGH",
                "fix_first_dependency": "This is a primary root cause. Fix this before re-testing forms or user journeys.",
                "recommended_solution": [
                    "Verify MySQL/Apache service is running in XAMPP or hosting environment.",
                    "Check database credentials in server configuration (e.g. `dbcon.php` or `.env`).",
                    "Ensure target tables and permissions are properly granted."
                ],
                "implementation_guidance": s_iss.get("suggested_fix") or "Check server logs and database connection parameters.",
                "expected_benefit": "Prevents HTTP 500 errors and unblocks critical user journeys and form submissions.",
                "verification_method": "Run automated test again and verify zero PHP warnings or HTTP 500 statuses."
            })

        # Step 2: Form & Conversion Failures
        for f_iss in form_issues:
            dep_note = "Fix database / server connection first." if has_server_db_error else None
            action_plan.append({
                "id": f"sol_{len(action_plan) + 1}",
                "priority": "high",
                "category": "Forms & Functional",
                "title": f"Fix Form Workflow: {f_iss.get('title')}",
                "problem": f_iss.get("description"),
                "evidence": {
                    "page_url": f_iss.get("page_url"),
                    "selector": f_iss.get("selector"),
                    "coordinates": f_iss.get("coordinates"),
                    "screenshot_url": f_iss.get("screenshot_url"),
                    "annotated_screenshot_url": f_iss.get("annotated_screenshot_url")
                },
                "root_cause": "Form input lacks valid action endpoint, label association, or submit handler.",
                "root_cause_confidence": "HIGH",
                "fix_first_dependency": dep_note,
                "recommended_solution": [
                    f_iss.get("recommendation", "Ensure form has a valid action and method."),
                    "Verify form CSRF tokens and required fields."
                ],
                "implementation_guidance": f_iss.get("suggested_fix") or "<form action='process.php' method='POST'>\n  <button type='submit'>Submit</button>\n</form>",
                "expected_benefit": "Ensures visitors can reliably submit leads, inquiries, or authentication credentials.",
                "verification_method": "Submit form in browser or automated re-test to confirm successful response."
            })

        # Step 3: Responsive & Layout Overflows
        resp_issues = [i for i in all_issues if i.get("category") in ("responsive", "ui") and i.get("severity") in ("critical", "high")]
        for r_iss in resp_issues[:4]:
            source_loc = r_iss.get("source_location") or {}
            action_plan.append({
                "id": f"sol_{len(action_plan) + 1}",
                "priority": "high",
                "category": "Responsive & Layout",
                "title": f"Fix Layout Defect: {r_iss.get('title')}",
                "problem": r_iss.get("description"),
                "evidence": {
                    "page_url": r_iss.get("page_url"),
                    "selector": r_iss.get("selector"),
                    "section": r_iss.get("section", "Layout"),
                    "viewport": r_iss.get("viewport"),
                    "coordinates": r_iss.get("coordinates"),
                    "screenshot_url": r_iss.get("screenshot_url"),
                    "annotated_screenshot_url": r_iss.get("annotated_screenshot_url"),
                    "source_file": source_loc.get("source_file"),
                    "line_number": source_loc.get("line_number")
                },
                "root_cause": r_iss.get("fix_reasoning") or "Fixed width styling or collision exceeding viewport boundary.",
                "root_cause_confidence": "HIGH" if source_loc.get("confidence") == "confirmed" else "MEDIUM",
                "fix_first_dependency": None,
                "recommended_solution": [
                    r_iss.get("recommendation", "Replace fixed width with max-width: 100%."),
                    "Test across mobile (390px) and tablet viewports."
                ],
                "implementation_guidance": r_iss.get("suggested_fix") or f"{r_iss.get('selector', '.container')} {{\n  max-width: 100% !important;\n  box-sizing: border-box;\n}}",
                "expected_benefit": "Eliminates horizontal scrolling and visual overlap on mobile and tablet devices.",
                "verification_method": "Automated re-test across all 5 responsive viewports."
            })

        # Step 4: AI Readiness & Structured Data Solutions
        ai_top_recs = ai_readiness_data.get("top_improvements", [])
        for ai_rec in ai_top_recs[:3]:
            action_plan.append({
                "id": f"sol_{len(action_plan) + 1}",
                "priority": ai_rec.get("priority", "medium"),
                "category": "AI Readiness & Semantic Structure",
                "title": ai_rec.get("title"),
                "problem": ai_rec.get("evidence"),
                "evidence": {
                    "why_it_matters": ai_rec.get("why_it_matters")
                },
                "root_cause": "Absence of structured machine metadata or semantic landmarks.",
                "root_cause_confidence": "HIGH",
                "fix_first_dependency": None,
                "recommended_solution": [
                    ai_rec.get("action", "Add structured JSON-LD data."),
                    "Validate with Schema.org parser."
                ],
                "implementation_guidance": ai_rec.get("code_fix"),
                "expected_benefit": "Enables accurate entity resolution by search crawlers, LLMs, and automated agents.",
                "verification_method": "Re-run AI Readiness audit to confirm schema detection and score boost."
            })

        # Executive Summary of Solution Plan
        summary = {
            "total_solutions": len(action_plan),
            "critical_solutions_count": sum(1 for s in action_plan if s["priority"] == "critical"),
            "high_solutions_count": sum(1 for s in action_plan if s["priority"] == "high"),
            "medium_solutions_count": sum(1 for s in action_plan if s["priority"] == "medium"),
            "recommended_order": [s["title"] for s in action_plan[:5]]
        }

        return {
            "summary": summary,
            "solutions": action_plan
        }


solution_engine = ReportSolutionEngine()
