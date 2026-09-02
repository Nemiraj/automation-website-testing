import pytest
from backend.app.services.ai_readiness.analyzer import ai_readiness_analyzer
from backend.app.services.ai_readiness.scorer import ai_readiness_scorer
from backend.app.services.solution_engine import solution_engine


def test_ai_readiness_scorer_deterministic():
    # Test deterministic scoring calculation
    category_findings = {
        "structured_data": [
            {"name": "Missing Schema", "passed": False, "severity": "high", "message": "No JSON-LD found"}
        ],
        "semantic_html": [
            {"name": "Main Landmark", "passed": True, "severity": "info", "message": "Main landmark present"},
            {"name": "Nav Landmark", "passed": True, "severity": "info", "message": "Nav landmark present"}
        ]
    }
    overall_score, cat_scores = ai_readiness_scorer.calculate_scores(category_findings)
    assert isinstance(overall_score, float)
    assert 0 <= overall_score <= 100
    assert "structured_data" in cat_scores
    assert cat_scores["structured_data"].score < 100  # Penalty for missing schema
    assert cat_scores["semantic_html"].score == 100   # Perfect score for semantic HTML


def test_ai_readiness_analyzer_with_pages():
    mock_pages = [
        {
            "url": "http://localhost/mywebsite/",
            "html": """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <title>Acme Corp | Official Dealership</title>
                <meta name="description" content="Leading automotive dealership in city center.">
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "Organization",
                    "name": "Acme Corp",
                    "url": "http://localhost/mywebsite"
                }
                </script>
            </head>
            <body>
                <header><nav><a href="/">Home</a><a href="/about">About Acme</a></nav></header>
                <main>
                    <h1>Welcome to Acme Corp</h1>
                    <p>Explore our automotive models.</p>
                </main>
                <footer><p>© 2026 Acme Corp</p></footer>
            </body>
            </html>
            """,
            "title": "Acme Corp | Official Dealership",
            "meta_description": "Leading automotive dealership in city center."
        }
    ]

    mock_issues = [
        {
            "category": "responsive",
            "severity": "high",
            "title": "Mobile nav overflow",
            "description": "Navigation overflows on 390px viewport",
            "selector": ".nav-menu",
            "page_url": "http://localhost/mywebsite/"
        }
    ]

    res = ai_readiness_analyzer.analyze_readiness(
        pages_data=mock_pages,
        all_issues=mock_issues,
        is_localhost=True
    )

    assert "overall_score" in res
    assert res["environment_type"] == "LOCAL DEVELOPMENT"
    assert res["structured_data"]["found"] is True
    assert "Organization" in res["structured_data"]["types_detected"]
    assert res["entity_consistency"]["is_consistent"] is True


def test_solution_engine_dependency_ordering():
    mock_issues = [
        {
            "id": "iss_1",
            "category": "server",
            "severity": "critical",
            "title": "PHP MySQL Database Connection Failed",
            "description": "Access denied for user root@localhost",
            "page_url": "http://localhost/mywebsite/contact.php"
        },
        {
            "id": "iss_2",
            "category": "forms",
            "severity": "high",
            "title": "Contact Form Returns HTTP 500",
            "description": "Form submission failed with internal server error",
            "page_url": "http://localhost/mywebsite/contact.php",
            "selector": "form#contactForm"
        },
        {
            "id": "iss_3",
            "category": "responsive",
            "severity": "high",
            "title": "Navbar Overflow on Mobile",
            "description": "Element exceeds 390px viewport width",
            "page_url": "http://localhost/mywebsite/",
            "selector": ".navbar"
        }
    ]

    ai_readiness_data = {
        "top_improvements": [
            {
                "priority": "high",
                "title": "Add Organization Schema (JSON-LD)",
                "evidence": "No JSON-LD structured data found.",
                "why_it_matters": "Enhances AI agent parsing.",
                "action": "Inject Organization schema block.",
                "code_fix": "<script type='application/ld+json'>{...}</script>"
            }
        ]
    }

    solution_res = solution_engine.generate_solution_plan(
        test_id="test-123",
        target_url="http://localhost/mywebsite/",
        all_issues=mock_issues,
        ai_readiness_data=ai_readiness_data
    )

    assert "solutions" in solution_res
    solutions = solution_res["solutions"]
    assert len(solutions) >= 3

    # Verify that the critical database issue is prioritized first
    assert solutions[0]["priority"] == "critical"
    assert "Server Error" in solutions[0]["title"]
    assert solutions[0]["fix_first_dependency"] is not None

    # Verify the form issue mentions dependency on database/server
    assert "Forms" in solutions[1]["category"]
    assert solutions[1]["fix_first_dependency"] is not None
