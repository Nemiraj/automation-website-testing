import os
import pytest
from backend.app.services.source_inspector import source_inspector


def test_source_inspector_search_css(tmp_path):
    # Create dummy project source directory with CSS and PHP
    project_dir = tmp_path / "my_project"
    project_dir.mkdir()
    css_dir = project_dir / "css"
    css_dir.mkdir()

    css_file = css_dir / "style.css"
    css_file.write_text("""
/* Main Stylesheet */
.navbar {
    display: flex;
    background: #333;
}

.hero-title {
    font-size: 2.5rem;
    width: 800px;
}
    """, encoding="utf-8")

    # Search for .hero-title
    res = source_inspector.inspect_selector_source(".hero-title", str(project_dir))
    assert res["confidence"] == "confirmed"
    assert "style.css" in res["source_file"]
    assert res["line_number"] == 8
    assert "width: 800px" in res["snippet"]


def test_source_inspector_search_php(tmp_path):
    project_dir = tmp_path / "my_php_project"
    project_dir.mkdir()

    php_file = project_dir / "header.php"
    php_file.write_text("""
<?php
// Header component
?>
<div class="custom-cta-button">
    <button type="submit">Get Started</button>
</div>
    """, encoding="utf-8")

    res = source_inspector.inspect_selector_source(".custom-cta-button", str(project_dir))
    assert res["confidence"] in ("confirmed", "likely")
    assert "header.php" in res["source_file"]
    assert "custom-cta-button" in res["snippet"]


def test_source_inspector_no_local_dir():
    # When no local directory is given, provide search guidance without fake files
    res = source_inspector.inspect_selector_source(".product-card", None)
    assert res["confidence"] == "inferred"
    assert res["source_file"] is None
    assert ".product-card" in res["search_hint"]
