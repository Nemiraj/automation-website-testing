from typing import List, Dict, Any, Optional
from backend.app.services.ai_readiness.schemas import AIReadinessRecommendation


class AIReadinessRecommender:
    """
    Generates concrete, evidence-backed improvements and code fixes
    for AI / LLM machine readability and agent accessibility.
    """

    def generate_recommendations(
        self,
        category_findings: Dict[str, List[Dict[str, Any]]],
        entity_info: Dict[str, Any],
        structured_data_info: Dict[str, Any]
    ) -> List[AIReadinessRecommendation]:
        recommendations: List[AIReadinessRecommendation] = []

        # 1. Structured Data Recommendations
        if not structured_data_info.get("found", False):
            site_name = entity_info.get("detected_names", ["My Website"])[0] if entity_info.get("detected_names") else "My Business"
            json_sample = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{site_name}",
  "url": "https://example.com",
  "description": "Comprehensive services and products.",
  "contactPoint": {{
    "@type": "ContactPoint",
    "contactType": "Customer Support",
    "telephone": "{entity_info.get('contact_phone') or '+1-800-555-0199'}"
  }}
}}
</script>"""
            recommendations.append(AIReadinessRecommendation(
                priority="high",
                category="structured_data",
                title="Add Organization Schema (JSON-LD)",
                evidence="No valid JSON-LD structured data or Schema.org microdata was found in rendered pages.",
                why_it_matters="AI search agents and LLMs rely on JSON-LD to understand core business entities, contact points, and offerings without ambiguity.",
                action="Inject an Organization or LocalBusiness JSON-LD block into the `<head>` of your main template.",
                code_fix=json_sample
            ))

        # 2. Semantic Landmark Recommendations
        semantic_findings = category_findings.get("semantic_html", [])
        for f in semantic_findings:
            if not f.get("passed", False) and "main" in f.get("name", "").lower():
                recommendations.append(AIReadinessRecommendation(
                    priority="high",
                    category="semantic_html",
                    title="Wrap Core Page Content in `<main>` Landmark",
                    evidence=f.get("message", "Document lacks a primary <main> content landmark."),
                    why_it_matters="Web agents and parsers use the `<main>` landmark to isolate core content from repetitive headers, navigation bars, and footers.",
                    action="Replace wrapper `<div>` tags containing page body with `<main role='main'>`.",
                    code_fix="""<!-- Before -->
<div class="content-wrapper">...</div>

<!-- After -->
<main id="main-content" role="main">
  ...
</main>"""
                ))

        # 3. Entity Consistency Recommendations
        inconsistencies = entity_info.get("inconsistencies", [])
        if inconsistencies:
            recommendations.append(AIReadinessRecommendation(
                priority="medium",
                category="machine_readability",
                title="Standardize Business Entity Name Across Pages",
                evidence=f"Different entity names detected across pages: {', '.join(inconsistencies[:3])}",
                why_it_matters="Inconsistent brand names (e.g. 'ABC Corp' on Home vs 'ABC Tech Solutions' in Footer) reduce AI confidence during entity resolution.",
                action="Align company name and branding across headers, footers, meta titles, and about pages.",
                code_fix=None
            ))

        # 4. Content Clarity & Descriptive Links
        clarity_findings = category_findings.get("content_clarity", [])
        for f in clarity_findings:
            if not f.get("passed", False) and "generic" in f.get("name", "").lower():
                recommendations.append(AIReadinessRecommendation(
                    priority="medium",
                    category="content_clarity",
                    title="Replace Non-Descriptive 'Click Here' Link Anchors",
                    evidence=f.get("message", "Found generic anchor links like 'Click Here' or 'Read More' without contextual text."),
                    why_it_matters="AI crawlers and screen readers cannot discern destination context when anchor texts are generic.",
                    action="Use explicit anchor phrases describing the target destination.",
                    code_fix="""<!-- Before -->
<a href="/pricing">Click here</a> to view plans.

<!-- After -->
<a href="/pricing">View subscription plans and pricing</a>."""
                ))

        # 5. Metadata Recommendations
        meta_findings = category_findings.get("metadata", [])
        for f in meta_findings:
            if not f.get("passed", False):
                recommendations.append(AIReadinessRecommendation(
                    priority="medium",
                    category="metadata",
                    title="Improve Open Graph and Machine-Readable Meta Tags",
                    evidence=f.get("message", "Missing or weak OpenGraph and description tags."),
                    why_it_matters="Rich social and machine metadata provides a deterministic summary for retrieval-augmented generation (RAG) and crawler previews.",
                    action="Include comprehensive OpenGraph meta tags in the document `<head>`.",
                    code_fix="""<meta property="og:title" content="Your Page Title" />
<meta property="og:description" content="Clear, concise summary of page contents (50-160 characters)." />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://example.com/page" />"""
                ))
                break

        return recommendations


ai_readiness_recommender = AIReadinessRecommender()
