import math
from typing import List, Dict, Any, Tuple
from playwright.async_api import Page
from backend.app.core.logging import logger


class CompleteDOMInspector:
    """
    Performs full-page scroll rendering and deep structural DOM inspection.
    Detects overflows, element overlaps, sizing anomalies, negative positioning,
    and classifies elements into semantic page sections.
    """

    async def scroll_and_render_full_page(self, page: Page) -> None:
        """
        Smoothly scrolls through the entire rendered page to trigger lazy-loaded
        images, intersection observers, and client-side hydration, then returns to top.
        """
        try:
            await page.evaluate("""
                async () => {
                    const scrollStep = 400;
                    const scrollDelay = 100;
                    const docHeight = Math.max(
                        document.body.scrollHeight,
                        document.documentElement.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.offsetHeight,
                        document.body.clientHeight,
                        document.documentElement.clientHeight
                    );

                    let currentScroll = 0;
                    while (currentScroll < docHeight) {
                        window.scrollBy(0, scrollStep);
                        currentScroll += scrollStep;
                        await new Promise(r => setTimeout(r, scrollDelay));
                    }

                    // Wait briefly at the bottom for any final lazy items
                    await new Promise(r => setTimeout(r, 200));

                    // Scroll back to top
                    window.scrollTo(0, 0);
                    await new Promise(r => setTimeout(r, 100));
                }
            """)
        except Exception as e:
            logger.warning(f"Error during full page scroll rendering: {e}")

    async def inspect_page_layout_and_sections(
        self,
        page: Page,
        page_url: str,
        viewport_name: str = "desktop_standard"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes complete DOM and layout inspection across the full document.
        Returns (issues, section_overview).
        """
        issues: List[Dict[str, Any]] = []

        try:
            dom_data = await page.evaluate("""
                () => {
                    const docEl = document.documentElement;
                    const body = document.body;
                    const docWidth = docEl.clientWidth;
                    const docHeight = docEl.clientHeight;
                    const fullHeight = Math.max(docEl.scrollHeight, body ? body.scrollHeight : 0);
                    const fullWidth = Math.max(docEl.scrollWidth, body ? body.scrollWidth : 0);

                    // 1. Identify Semantic Sections
                    const sections = [];
                    const sectionCandidates = document.querySelectorAll(
                        'header, nav, [role="banner"], [role="navigation"], ' +
                        'main, section, article, aside, footer, [role="contentinfo"], ' +
                        '.hero, #hero, .navbar, #navbar, .footer, #footer, .header, #header'
                    );

                    sectionCandidates.forEach((el, idx) => {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        if (rect.width > 0 && rect.height > 20 && style.display !== 'none' && style.visibility !== 'hidden') {
                            let name = el.tagName.toLowerCase();
                            if (el.id) name = '#' + el.id;
                            else if (el.className && typeof el.className === 'string') {
                                const c = el.className.split(' ').filter(x => x.trim())[0];
                                if (c) name = '.' + c;
                            }
                            if (name.includes('nav') || el.tagName.toLowerCase() === 'nav') name = 'Navbar';
                            else if (name.includes('hero')) name = 'Hero';
                            else if (name.includes('header') || el.tagName.toLowerCase() === 'header') name = 'Header';
                            else if (name.includes('footer') || el.tagName.toLowerCase() === 'footer') name = 'Footer';
                            else name = name.charAt(0).toUpperCase() + name.slice(1);

                            sections.push({
                                name: name,
                                selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '')),
                                top: Math.round(rect.top + window.scrollY),
                                height: Math.round(rect.height),
                                width: Math.round(rect.width)
                            });
                        }
                    });

                    // 2. Meaningful UI Elements for Inspection
                    const interestingElements = [];
                    const targetEls = document.querySelectorAll(
                        'h1, h2, h3, h4, h5, h6, p, a, button, input, textarea, select, img, table, form, ' +
                        '.card, .container, .row, .col, .btn, .nav-item, .product-card'
                    );

                    const overlaps = [];
                    const overflowElements = [];
                    const sizingIssues = [];
                    const negativePositionElements = [];

                    const visibleNodes = [];

                    targetEls.forEach((el, idx) => {
                        if (visibleNodes.length >= 250) return;
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);

                        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                            return;
                        }

                        // Determine clean selector
                        let selector = el.tagName.toLowerCase();
                        if (el.id) selector += '#' + el.id;
                        else if (el.className && typeof el.className === 'string') {
                            const classes = el.className.split(' ').filter(c => c.trim() && !c.includes(':')).slice(0, 2);
                            if (classes.length) selector += '.' + classes.join('.');
                        }
                        if (selector === el.tagName.toLowerCase()) {
                            selector = `${selector}:nth-of-type(${idx + 1})`;
                        }

                        const absoluteTop = Math.round(rect.top + window.scrollY);
                        const absoluteLeft = Math.round(rect.left + window.scrollX);

                        // Find Section for this element
                        let sectionName = 'Content';
                        for (let sec of sections) {
                            if (absoluteTop >= sec.top - 20 && absoluteTop <= sec.top + sec.height + 20) {
                                sectionName = sec.name;
                                break;
                            }
                        }

                        const nodeData = {
                            tag: el.tagName.toLowerCase(),
                            selector: selector,
                            section: sectionName,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            absX: absoluteLeft,
                            absY: absoluteTop,
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            right: Math.round(rect.right),
                            bottom: Math.round(rect.bottom),
                            position: style.position,
                            zIndex: style.zIndex,
                            widthStyle: style.width,
                            maxWidthStyle: style.maxWidth,
                            overflow: style.overflow,
                            text: (el.innerText || '').slice(0, 40).trim()
                        };

                        visibleNodes.push(nodeData);

                        // Check Horizontal Overflow
                        if (rect.right > (docWidth + 4) && rect.width > 15) {
                            overflowElements.push(nodeData);
                        }

                        // Check Negative Positioning
                        if (rect.left < -5 || rect.top < -5) {
                            if (style.position === 'absolute' || style.position === 'relative') {
                                negativePositionElements.push(nodeData);
                            }
                        }

                        // Sizing Anomalies: tiny buttons or zero-height visible elements with children
                        if (['button', 'a'].includes(el.tagName.toLowerCase()) && rect.width > 0 && rect.height > 0) {
                            if (rect.width < 24 || rect.height < 24) {
                                sizingIssues.push(nodeData);
                            }
                        }
                    });

                    // 3. Detect Unintended Element Overlaps
                    // Check button/heading/interactive overlapping another interactive/text element
                    for (let i = 0; i < visibleNodes.length && overlaps.length < 5; i++) {
                        const a = visibleNodes[i];
                        if (['button', 'a', 'input', 'h1', 'h2', 'h3'].includes(a.tag)) {
                            for (let j = i + 1; j < visibleNodes.length && overlaps.length < 5; j++) {
                                const b = visibleNodes[j];
                                if (['button', 'a', 'h1', 'h2', 'p'].includes(b.tag)) {
                                    // Check bounding collision on screen
                                    if (
                                        a.absX < b.absX + b.width - 4 &&
                                        a.absX + a.width - 4 > b.absX &&
                                        a.absY < b.absY + b.height - 4 &&
                                        a.absY + a.height - 4 > b.absY
                                    ) {
                                        // Overlap detected!
                                        if (a.selector !== b.selector && Math.abs(a.width - b.width) > 5) {
                                            overlaps.push({
                                                elementA: a,
                                                elementB: b
                                            });
                                        }
                                    }
                                }
                            }
                        }
                    }

                    return {
                        docWidth,
                        docHeight,
                        fullWidth,
                        fullHeight,
                        sections,
                        overflowElements,
                        overlaps,
                        sizingIssues,
                        negativePositionElements
                    };
                }
            """)

            doc_w = dom_data.get("docWidth", 1280)

            # A. Horizontal Overflow Issues
            for over in dom_data.get("overflowElements", [])[:5]:
                diff_px = over["right"] - doc_w
                issues.append({
                    "category": "responsive" if "mobile" in viewport_name or "tablet" in viewport_name else "ui",
                    "severity": "high",
                    "page_url": page_url,
                    "section": over.get("section", "Layout"),
                    "viewport": viewport_name,
                    "title": f"Element Horizontal Overflow ({over['selector']})",
                    "description": f"Element '{over['selector']}' ({over['width']}px wide) exceeds viewport width ({doc_w}px) by {diff_px}px.",
                    "why_it_matters": "Content extending beyond the viewport causes horizontal scrollbars and breaks mobile responsive reading flow.",
                    "recommendation": f"Change fixed width (`{over.get('widthStyle', 'auto')}`) on `{over['selector']}` to `max-width: 100%; width: auto;`.",
                    "suggested_fix": f"{over['selector']} {{\n  max-width: 100% !important;\n  box-sizing: border-box;\n}}",
                    "selector": over["selector"],
                    "coordinates": {
                        "x": over["x"],
                        "y": over["y"],
                        "width": over["width"],
                        "height": over["height"],
                        "tag": over["tag"]
                    },
                    "marker_type": "rectangle",
                    "fix_confidence": "high",
                    "fix_reasoning": f"Element computed width is {over['width']}px with fixed styling {over.get('widthStyle')}, exceeding viewport {doc_w}px.",
                    "evidence": over
                })

            # B. Element Overlap Issues
            for lap in dom_data.get("overlaps", [])[:3]:
                el_a = lap["elementA"]
                el_b = lap["elementB"]
                issues.append({
                    "category": "ui",
                    "severity": "high",
                    "page_url": page_url,
                    "section": el_a.get("section", "Content"),
                    "viewport": viewport_name,
                    "title": f"Element Overlap: {el_a['selector']} overlaps {el_b['selector']}",
                    "description": f"Interactive or text element '{el_a['selector']}' collides with '{el_b['selector']}'.",
                    "why_it_matters": "Overlapping elements obscure critical text and can prevent buttons or links from receiving click events.",
                    "recommendation": f"Review CSS positioning (`position: {el_a.get('position')}` / `position: {el_b.get('position')}`) and margins between these components.",
                    "suggested_fix": f"{el_a['selector']} {{\n  position: relative;\n  margin-bottom: 1rem;\n}}",
                    "selector": el_a["selector"],
                    "coordinates": {
                        "x": el_a["x"],
                        "y": el_a["y"],
                        "width": el_a["width"],
                        "height": el_a["height"],
                        "tag": el_a["tag"]
                    },
                    "marker_type": "arrow",
                    "fix_confidence": "high",
                    "fix_reasoning": f"Bounding box collision detected between {el_a['selector']} and {el_b['selector']} in {viewport_name}.",
                    "evidence": lap
                })

            # C. Sizing & Clickability Anomalies
            for sz in dom_data.get("sizingIssues", [])[:3]:
                issues.append({
                    "category": "ui",
                    "severity": "medium",
                    "page_url": page_url,
                    "section": sz.get("section", "Navigation"),
                    "viewport": viewport_name,
                    "title": f"Undersized Interactive Element ({sz['selector']})",
                    "description": f"Target '{sz['selector']}' is rendered at {sz['width']}×{sz['height']}px, below the recommended minimum 32×32px.",
                    "why_it_matters": "Tiny interactive elements lead to missed clicks and poor mobile usability.",
                    "recommendation": f"Add padding or minimum dimensions to `{sz['selector']}`.",
                    "suggested_fix": f"{sz['selector']} {{\n  min-width: 36px;\n  min-height: 36px;\n  padding: 8px 12px;\n}}",
                    "selector": sz["selector"],
                    "coordinates": {
                        "x": sz["x"],
                        "y": sz["y"],
                        "width": sz["width"],
                        "height": sz["height"],
                        "tag": sz["tag"]
                    },
                    "marker_type": "arrow",
                    "fix_confidence": "high",
                    "fix_reasoning": f"Interactive {sz['tag']} element bounding box is only {sz['width']}x{sz['height']}px.",
                    "evidence": sz
                })

            # D. Negative Positioning Layout Faults
            for np in dom_data.get("negativePositionElements", [])[:2]:
                issues.append({
                    "category": "ui",
                    "severity": "medium",
                    "page_url": page_url,
                    "section": np.get("section", "Layout"),
                    "viewport": viewport_name,
                    "title": f"Negative Off-Screen Positioning ({np['selector']})",
                    "description": f"Element '{np['selector']}' has negative coordinates (X: {np['x']}px, Y: {np['y']}px), pushing content outside the visible container.",
                    "why_it_matters": "Negative offsets can accidentally clip content or cause unexpected scrollbars across different screen resolutions.",
                    "recommendation": f"Ensure `{np['selector']}` uses standard flex/grid alignment instead of negative margins or coordinates.",
                    "suggested_fix": f"{np['selector']} {{\n  left: 0;\n  top: 0;\n  margin: 0 auto;\n}}",
                    "selector": np["selector"],
                    "coordinates": {
                        "x": max(0, np["x"]),
                        "y": max(0, np["y"]),
                        "width": np["width"],
                        "height": np["height"],
                        "tag": np["tag"]
                    },
                    "marker_type": "rectangle",
                    "fix_confidence": "medium",
                    "fix_reasoning": "Negative position coordinate detected in CSS layout.",
                    "evidence": np
                })

            section_overview = {
                "sections": dom_data.get("sections", []),
                "full_width": dom_data.get("fullWidth", doc_w),
                "full_height": dom_data.get("fullHeight", 800)
            }

            return issues, section_overview

        except Exception as e:
            logger.warning(f"Error during deep DOM inspection on {page_url}: {e}")
            return [], {}


dom_inspector = CompleteDOMInspector()
