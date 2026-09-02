from typing import List, Dict, Any
from playwright.async_api import Page
from backend.app.core.logging import logger


class UIAnalyzer:
    async def analyze_ui(self, page: Page, page_url: str, viewport_name: str = "desktop") -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []

        try:
            dom_ui_data = await page.evaluate("""
                () => {
                    const docEl = document.documentElement;
                    const body = document.body;
                    const docWidth = docEl.clientWidth;
                    const docHeight = docEl.clientHeight;
                    const scrollWidth = Math.max(docEl.scrollWidth, body ? body.scrollWidth : 0);
                    
                    // 1. Check Horizontal Overflow on Document
                    const hasHorizontalOverflow = scrollWidth > (docWidth + 3);
                    const overflowAmount = Math.max(0, scrollWidth - docWidth);
                    
                    // 2. Identify Overflowing Elements
                    const overflowingElements = [];
                    const allEls = document.querySelectorAll('body *');
                    
                    for (let el of allEls) {
                        if (overflowingElements.length >= 10) break;
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        
                        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                            continue;
                        }
                        
                        // Element extending to the right outside viewport
                        if (rect.right > (docWidth + 5) && rect.width > 10) {
                            let selector = el.tagName.toLowerCase();
                            if (el.id) selector += '#' + el.id;
                            else if (el.className && typeof el.className === 'string') {
                                const firstClass = el.className.split(' ').filter(c => c.trim().length > 0)[0];
                                if (firstClass) selector += '.' + firstClass;
                            }
                            overflowingElements.push({
                                selector: selector,
                                tagName: el.tagName.toLowerCase(),
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                right: Math.round(rect.right),
                                docWidth: docWidth,
                                rectWidth: Math.round(rect.width)
                            });
                        }
                    }

                    // 3. Small Click Targets (< 24px)
                    const smallClickables = [];
                    const clickables = document.querySelectorAll('button, a, input[type=button], input[type=submit], [role=button]');
                    clickables.forEach(el => {
                        if (smallClickables.length >= 5) return;
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        if (rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden') {
                            if (rect.width < 24 || rect.height < 24) {
                                let sel = el.tagName.toLowerCase();
                                if (el.id) sel += '#' + el.id;
                                else if (el.className && typeof el.className === 'string') {
                                    const c = el.className.split(' ').filter(x => x.trim())[0];
                                    if (c) sel += '.' + c;
                                }
                                smallClickables.push({
                                    selector: sel,
                                    tagName: el.tagName.toLowerCase(),
                                    text: (el.innerText || el.getAttribute('aria-label') || '').slice(0, 30),
                                    x: Math.round(rect.x),
                                    y: Math.round(rect.y),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height)
                                });
                            }
                        }
                    });

                    // 4. Headings Structure
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => {
                        const rect = h.getBoundingClientRect();
                        return {
                            level: parseInt(h.tagName.substring(1)),
                            text: (h.innerText || '').slice(0, 50),
                            selector: h.tagName.toLowerCase(),
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        };
                    });

                    return {
                        hasHorizontalOverflow,
                        overflowAmount,
                        docWidth,
                        scrollWidth,
                        overflowingElements,
                        smallClickables,
                        headings
                    };
                }
            """)

            # Horizontal Overflow Issue
            if dom_ui_data.get("hasHorizontalOverflow"):
                overflow_px = dom_ui_data.get("overflowAmount", 0)
                over_els = dom_ui_data.get("overflowingElements", [])
                top_el = over_els[0] if over_els else None
                top_el_selector = top_el["selector"] if top_el else "body"

                issues.append({
                    "category": "responsive" if "mobile" in viewport_name or "tablet" in viewport_name else "ui",
                    "severity": "high",
                    "page_url": page_url,
                    "viewport": viewport_name,
                    "title": f"Horizontal Layout Overflow Detected ({overflow_px}px)",
                    "description": f"Page content width ({dom_ui_data['scrollWidth']}px) exceeds viewport width ({dom_ui_data['docWidth']}px) by {overflow_px}px, causing unwanted horizontal scrolling.",
                    "why_it_matters": "Horizontal scrolling disrupts reading flow, degrades mobile usability, and fails Google Mobile-Friendly guidelines.",
                    "recommendation": "Review fixed widths, large margins/paddings, or missing `max-w-full` / `overflow-x: hidden` on container elements.",
                    "suggested_fix": f"Inspect {top_el_selector} and apply `max-width: 100%` or `box-sizing: border-box`.",
                    "selector": top_el_selector,
                    "coordinates": {
                        "x": top_el["x"] if top_el else 0,
                        "y": top_el["y"] if top_el else 0,
                        "width": top_el["width"] if top_el else dom_ui_data["docWidth"],
                        "height": top_el["height"] if top_el else 100,
                        "tag": top_el["tagName"] if top_el else "div"
                    } if top_el else {},
                    "marker_type": "rectangle",
                    "evidence": {
                        "viewport": viewport_name,
                        "viewport_width": dom_ui_data["docWidth"],
                        "scroll_width": dom_ui_data["scrollWidth"],
                        "overflow_pixels": overflow_px,
                        "overflowing_elements": over_els
                    }
                })

            # Small Click Targets
            for target in dom_ui_data.get("smallClickables", []):
                issues.append({
                    "category": "ui",
                    "severity": "medium",
                    "page_url": page_url,
                    "viewport": viewport_name,
                    "title": f"Undersized Clickable Target ({target['width']}x{target['height']}px)",
                    "description": f"Interactive element '{target['selector']}' is only {target['width']}x{target['height']}px, smaller than the recommended minimum 24x24px (and 44x44px for mobile).",
                    "why_it_matters": "Tiny buttons lead to misclicks, frustrating users especially on touchscreens.",
                    "recommendation": "Increase the element padding or minimum bounding box to at least 32px (desktop) or 44px (touch devices).",
                    "suggested_fix": f"Add `padding` or `min-width: 32px; min-height: 32px;` to {target['selector']}.",
                    "selector": target["selector"],
                    "coordinates": {
                        "x": target.get("x", 0),
                        "y": target.get("y", 0),
                        "width": target.get("width", 20),
                        "height": target.get("height", 20),
                        "tag": target.get("tagName", "button")
                    },
                    "marker_type": "arrow",
                    "evidence": target
                })

            # Heading Hierarchy Analysis
            headings = dom_ui_data.get("headings", [])
            h1_count = sum(1 for h in headings if h["level"] == 1)
            
            if h1_count == 0:
                issues.append({
                    "category": "accessibility",
                    "severity": "medium",
                    "page_url": page_url,
                    "title": "Missing <h1> Heading",
                    "description": "The page does not contain an <h1> tag to identify the primary page topic.",
                    "why_it_matters": "An <h1> heading is essential for assistive technologies and SEO hierarchy.",
                    "recommendation": "Add a single, descriptive <h1> heading at the top of the main content area.",
                    "suggested_fix": "Wrap main page title with <h1>...</h1>.",
                    "selector": "body",
                    "evidence": {"headings_found": headings[:5]}
                })
            elif h1_count > 1:
                issues.append({
                    "category": "ui",
                    "severity": "low",
                    "page_url": page_url,
                    "title": f"Multiple <h1> Headings Found ({h1_count})",
                    "description": f"The page defines {h1_count} separate <h1> tags.",
                    "why_it_matters": "Having multiple top-level <h1> headings can confuse screen readers and dilute SEO topic focus.",
                    "recommendation": "Reserve <h1> for the primary page title and use <h2>/<h3> for subsections.",
                    "suggested_fix": "Change secondary <h1> elements to <h2>.",
                    "selector": "h1",
                    "evidence": {"h1_count": h1_count}
                })

            # Check for skipped heading levels (e.g. h1 followed directly by h3)
            prev_level = 0
            for h in headings:
                curr_level = h["level"]
                if prev_level > 0 and curr_level > prev_level + 1:
                    issues.append({
                        "category": "accessibility",
                        "severity": "low",
                        "page_url": page_url,
                        "title": f"Skipped Heading Level (h{prev_level} -> h{curr_level})",
                        "description": f"Heading hierarchy jumped from <h{prev_level}> directly to <h{curr_level}> ('{h['text']}').",
                        "why_it_matters": "Skipping levels breaks document outline structure for screen reader users navigating by headings.",
                        "recommendation": f"Use an <h{prev_level + 1}> instead of <h{curr_level}>.",
                        "suggested_fix": f"Change <h{curr_level}> to <h{prev_level + 1}>.",
                        "selector": f"h{curr_level}",
                        "evidence": {"previous_level": prev_level, "current_level": curr_level, "heading_text": h["text"]}
                    })
                    break  # report once per page
                prev_level = curr_level

        except Exception as e:
            logger.warning(f"Error in UI analyzer for {page_url}: {e}")

        return issues
