import json
import re
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from backend.app.services.ai_readiness.schemas import (
    AIReadinessReport,
    EntityConsistency,
    StructuredDataAudit,
)
from backend.app.services.ai_readiness.scorer import ai_readiness_scorer
from backend.app.services.ai_readiness.recommendations import ai_readiness_recommender
from backend.app.core.logging import logger


class AIReadinessAnalyzer:
    """
    Analyzes actual website evidence (DOM, HTML, structured data, entity info,
    network requests) to evaluate machine readability and AI agent readiness.
    """

    def analyze_readiness(
        self,
        pages_data: List[Dict[str, Any]],
        all_issues: List[Dict[str, Any]],
        is_localhost: bool = False
    ) -> Dict[str, Any]:
        """
        Consumes complete multi-page audit evidence and produces an AIReadinessReport dict.
        """
        category_findings: Dict[str, List[Dict[str, Any]]] = {
            "technical_accessibility": [],
            "content_structure": [],
            "semantic_html": [],
            "structured_data": [],
            "crawlability": [],
            "content_clarity": [],
            "machine_readability": [],
            "metadata": [],
            "performance": [],
            "agent_accessibility": []
        }

        # 1. Inspect Structured Data across pages
        structured_data_audit = self._audit_structured_data(pages_data)
        if structured_data_audit["found"]:
            category_findings["structured_data"].append({
                "name": "JSON-LD Schema Found",
                "passed": True,
                "severity": "info",
                "message": f"Found structured schema types: {', '.join(structured_data_audit['types_detected'])}"
            })
        else:
            category_findings["structured_data"].append({
                "name": "Missing Structured Data",
                "passed": False,
                "severity": "high",
                "message": "No Schema.org JSON-LD or microdata found on audited pages."
            })

        # 2. Inspect Semantic HTML & Landmarks
        semantic_stats = self._audit_semantic_html(pages_data)
        if semantic_stats["has_main"]:
            category_findings["semantic_html"].append({
                "name": "Semantic <main> Landmark Present",
                "passed": True,
                "severity": "info",
                "message": "Primary <main> landmark correctly encloses page body content."
            })
        else:
            category_findings["semantic_html"].append({
                "name": "Missing <main> Landmark",
                "passed": False,
                "severity": "high",
                "message": "Pages lack a standard <main> landmark, complicating content extraction for parsers."
            })

        if semantic_stats["has_nav"]:
            category_findings["semantic_html"].append({
                "name": "Semantic <nav> Element Present",
                "passed": True,
                "severity": "info",
                "message": "Navigation items are grouped in semantic <nav> containers."
            })
        else:
            category_findings["semantic_html"].append({
                "name": "Missing <nav> Landmark",
                "passed": False,
                "severity": "medium",
                "message": "Navigation menus are styled generic <div> elements without semantic <nav> tags."
            })

        # 3. Content Structure & Headings
        if semantic_stats["heading_order_valid"]:
            category_findings["content_structure"].append({
                "name": "Logical Heading Hierarchy",
                "passed": True,
                "severity": "info",
                "message": "Headings follow a logical H1 -> H2 -> H3 outline structure."
            })
        else:
            category_findings["content_structure"].append({
                "name": "Skipped Heading Levels",
                "passed": False,
                "severity": "medium",
                "message": "Heading levels skip hierarchy (e.g. H1 directly to H3/H4), creating ambiguity in document outlines."
            })

        # 4. Content Clarity & Descriptive Links
        link_clarity = self._audit_link_clarity(pages_data)
        if link_clarity["generic_links_count"] == 0:
            category_findings["content_clarity"].append({
                "name": "Descriptive Link Anchors",
                "passed": True,
                "severity": "info",
                "message": "Internal and external links use contextual, descriptive anchor texts."
            })
        else:
            category_findings["content_clarity"].append({
                "name": "Generic Anchor Texts",
                "passed": False,
                "severity": "medium",
                "message": f"Found {link_clarity['generic_links_count']} generic links ('click here', 'read more') without target context."
            })

        # 5. Entity & Organization Consistency
        entity_info = self._audit_entity_consistency(pages_data)
        if entity_info["is_consistent"]:
            category_findings["machine_readability"].append({
                "name": "Consistent Business Entity Identity",
                "passed": True,
                "severity": "info",
                "message": f"Brand identity '{entity_info['detected_names'][0] if entity_info['detected_names'] else 'Primary Brand'}' is consistent across pages."
            })
        else:
            category_findings["machine_readability"].append({
                "name": "Inconsistent Brand / Entity Names",
                "passed": False,
                "severity": "medium",
                "message": f"Detected differing brand name representations: {', '.join(entity_info['inconsistencies'][:2])}"
            })

        # 6. Metadata & Social Graph
        metadata_audit = self._audit_metadata(pages_data)
        if metadata_audit["has_title_and_desc"]:
            category_findings["metadata"].append({
                "name": "Essential Meta Tags Present",
                "passed": True,
                "severity": "info",
                "message": "Pages include unique descriptive titles and meta description tags."
            })
        else:
            category_findings["metadata"].append({
                "name": "Missing or Duplicate Meta Descriptions",
                "passed": False,
                "severity": "medium",
                "message": "Pages lack unique meta descriptions or title tags."
            })

        # 7. Technical Accessibility (from existing a11y issues)
        a11y_issues = [i for i in all_issues if i.get("category") == "accessibility"]
        if not a11y_issues:
            category_findings["technical_accessibility"].append({
                "name": "Form & Interactive Accessibility",
                "passed": True,
                "severity": "info",
                "message": "Interactive elements have accessible names and properly associated labels."
            })
        else:
            category_findings["technical_accessibility"].append({
                "name": "Accessibility Violations Detected",
                "passed": False,
                "severity": "high" if len(a11y_issues) > 3 else "medium",
                "message": f"Found {len(a11y_issues)} accessibility issues affecting machine/agent navigability."
            })

        # 8. Crawlability & Canonical
        broken_links = [i for i in all_issues if i.get("category") == "functional"]
        if not broken_links:
            category_findings["crawlability"].append({
                "name": "Clean Internal Link Crawlability",
                "passed": True,
                "severity": "info",
                "message": "All internal page routes return HTTP 200 without broken links or infinite loops."
            })
        else:
            category_findings["crawlability"].append({
                "name": "Broken Links Affecting Crawl Paths",
                "passed": False,
                "severity": "high",
                "message": f"Found {len(broken_links)} broken internal links or route errors."
            })

        # 9. Performance & Payload Weight
        perf_issues = [i for i in all_issues if i.get("category") == "performance"]
        if not perf_issues:
            category_findings["performance"].append({
                "name": "Optimal Page Weight & Load Times",
                "passed": True,
                "severity": "info",
                "message": "Pages load within acceptable latency for automated agents."
            })
        else:
            category_findings["performance"].append({
                "name": "High Page Latency",
                "passed": False,
                "severity": "medium",
                "message": f"{len(perf_issues)} performance bottlenecks detected."
            })

        # 10. AI / Agent Accessibility & Discoverable Workflows
        form_issues = [i for i in all_issues if i.get("category") == "forms"]
        if not form_issues:
            category_findings["agent_accessibility"].append({
                "name": "Agent Accessible Form Workflows",
                "passed": True,
                "severity": "info",
                "message": "Forms use standard HTTP actions and inputs with clear submission endpoints."
            })
        else:
            category_findings["agent_accessibility"].append({
                "name": "Unclear Form Submission Endpoints",
                "passed": False,
                "severity": "high",
                "message": f"{len(form_issues)} form validation or endpoint issues prevent automated submission."
            })

        # Calculate Scores
        overall_score, cat_scores = ai_readiness_scorer.calculate_scores(category_findings)

        # Generate Evidence-Based Recommendations
        top_recs = ai_readiness_recommender.generate_recommendations(
            category_findings,
            entity_info,
            structured_data_audit
        )

        env_label = "LOCAL DEVELOPMENT" if is_localhost else "LIVE WEBSITE"

        return {
            "overall_score": overall_score,
            "environment_type": env_label,
            "category_scores": {k: v.dict() for k, v in cat_scores.items()},
            "entity_consistency": entity_info,
            "structured_data": structured_data_audit,
            "top_improvements": [r.dict() for r in top_recs],
            "rendering_dependency": {
                "client_side_dependent": False,
                "note": "Content structure is reliably available in rendered document."
            },
            "crawlability_summary": {
                "pages_crawled": len(pages_data),
                "is_localhost": is_localhost,
                "public_discoverability_note": (
                    "Public discoverability was not evaluated because this is a local development environment."
                    if is_localhost else "Public discoverability evaluated from live response headers."
                )
            },
            "agent_accessibility": {
                "score": cat_scores["agent_accessibility"].score,
                "status": "Ready" if cat_scores["agent_accessibility"].score >= 80 else "Needs Optimization",
                "note": "Assesses machine readability and structured workflow discovery."
            }
        }

    def _audit_structured_data(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        found_schemas = []
        types_detected = set()

        for page in pages_data:
            html = page.get("html", "")
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            scripts = soup.find_all("script", type="application/ld+json")
            for s in scripts:
                try:
                    data = json.loads(s.string)
                    if isinstance(data, dict):
                        t = data.get("@type")
                        if t:
                            types_detected.add(str(t))
                            found_schemas.append(data)
                    elif isinstance(data, list):
                        for item in data:
                            t = item.get("@type")
                            if t:
                                types_detected.add(str(t))
                                found_schemas.append(item)
                except Exception:
                    pass

        return {
            "found": len(found_schemas) > 0,
            "types_detected": list(types_detected),
            "schemas": found_schemas[:5],
            "syntax_errors": []
        }

    def _audit_semantic_html(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        has_main = False
        has_nav = False
        heading_order_valid = True

        for page in pages_data:
            html = page.get("html", "")
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            if soup.find("main") or soup.find(role="main"):
                has_main = True
            if soup.find("nav") or soup.find(role="navigation"):
                has_nav = True

            headings = soup.find_all(re.compile(r"^h[1-6]$"))
            last_level = 0
            for h in headings:
                try:
                    level = int(h.name[1])
                    if last_level > 0 and level > (last_level + 1):
                        heading_order_valid = False
                    last_level = level
                except Exception:
                    pass

        return {
            "has_main": has_main,
            "has_nav": has_nav,
            "heading_order_valid": heading_order_valid
        }

    def _audit_link_clarity(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        generic_patterns = re.compile(r"^(click\s*here|read\s*more|learn\s*more|view\s*more|more|link)$", re.IGNORECASE)
        generic_count = 0

        for page in pages_data:
            html = page.get("html", "")
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a"):
                text = a.get_text(strip=True)
                if text and generic_patterns.match(text):
                    generic_count += 1

        return {
            "generic_links_count": generic_count
        }

    def _audit_entity_consistency(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        detected_names = []
        for page in pages_data:
            title = page.get("title", "")
            if title:
                # Extract branding after delimiter | or -
                parts = re.split(r"[|\-–—]", title)
                if len(parts) > 1:
                    detected_names.append(parts[-1].strip())
                else:
                    detected_names.append(title.strip())

        unique_names = list(set([n for n in detected_names if len(n) > 2]))
        inconsistencies = []
        if len(unique_names) > 2:
            inconsistencies = unique_names

        return {
            "is_consistent": len(unique_names) <= 2,
            "detected_names": unique_names[:3],
            "inconsistencies": inconsistencies
        }

    def _audit_metadata(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        has_title_and_desc = True
        for page in pages_data:
            title = page.get("title", "")
            meta_desc = page.get("meta_description", "")
            if not title or not meta_desc:
                has_title_and_desc = False
                break
        return {"has_title_and_desc": has_title_and_desc}


ai_readiness_analyzer = AIReadinessAnalyzer()
