from typing import Dict, Any

# Configurable category weights summing to 1.0 (100%)
DEFAULT_CATEGORY_WEIGHTS: Dict[str, float] = {
    "technical_accessibility": 0.15,
    "content_structure": 0.15,
    "semantic_html": 0.10,
    "structured_data": 0.15,
    "crawlability": 0.10,
    "content_clarity": 0.10,
    "machine_readability": 0.10,
    "metadata": 0.05,
    "performance": 0.05,
    "agent_accessibility": 0.05
}

CATEGORY_METADATA = {
    "technical_accessibility": {
        "name": "Technical Accessibility",
        "description": "Accessible names, form input associations, keyboard navigation, and ARIA landmarks."
    },
    "content_structure": {
        "name": "Content Structure",
        "description": "Clear heading hierarchy (H1-H6), structured lists, tables, and logical reading flow."
    },
    "semantic_html": {
        "name": "Semantic HTML",
        "description": "Usage of <main>, <header>, <nav>, <section>, <article>, and <footer> tags."
    },
    "structured_data": {
        "name": "Structured Data",
        "description": "JSON-LD schema markups (Organization, LocalBusiness, Product, Service, BreadcrumbList)."
    },
    "crawlability": {
        "name": "Crawlability",
        "description": "HTTP status codes, canonical URL consistency, sitemaps, and internal link paths."
    },
    "content_clarity": {
        "name": "Content Clarity",
        "description": "Descriptive anchor texts avoiding generic 'click here' links, and unambiguous context."
    },
    "machine_readability": {
        "name": "Machine Readability",
        "description": "Consistent business entity identity, machine-parsable contacts, and structured data tables."
    },
    "metadata": {
        "name": "Metadata",
        "description": "Page titles, meta descriptions, Open Graph, Twitter cards, and canonical declarations."
    },
    "performance": {
        "name": "Performance",
        "description": "Page rendering speed, DOM depth, layout stability, and asset payload weights."
    },
    "agent_accessibility": {
        "name": "AI / Agent Accessibility",
        "description": "Discoverability of workflows, form actions, structured endpoints, and interactive targets."
    }
}
