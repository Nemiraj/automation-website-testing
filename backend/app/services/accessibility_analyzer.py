from typing import List, Dict, Any
from playwright.async_api import Page
from backend.app.core.logging import logger


class AccessibilityAnalyzer:
    async def analyze_accessibility(self, page: Page, page_url: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []

        try:
            # Perform comprehensive browser-evaluated accessibility audit
            a11y_data = await page.evaluate("""
                () => {
                    const results = {
                        missingDocLang: !document.documentElement.getAttribute('lang'),
                        emptyLinks: [],
                        emptyButtons: [],
                        duplicateIds: [],
                        lowContrastElements: []
                    };

                    // 1. Links without text or accessible name
                    document.querySelectorAll('a[href]').forEach(a => {
                        if (results.emptyLinks.length >= 8) return;
                        const text = (a.innerText || a.getAttribute('aria-label') || a.getAttribute('title') || '').trim();
                        const hasImgAlt = Array.from(a.querySelectorAll('img')).some(i => (i.getAttribute('alt') || '').trim().length > 0);
                        
                        if (!text && !hasImgAlt) {
                            const rect = a.getBoundingClientRect();
                            results.emptyLinks.push({
                                href: a.getAttribute('href') || '',
                                outerHTML: a.outerHTML.slice(0, 100),
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            });
                        }
                    });

                    // 2. Buttons without text or accessible name
                    document.querySelectorAll('button').forEach(btn => {
                        if (results.emptyButtons.length >= 8) return;
                        const text = (btn.innerText || btn.getAttribute('aria-label') || btn.getAttribute('title') || '').trim();
                        const hasImgAlt = Array.from(btn.querySelectorAll('img')).some(i => (i.getAttribute('alt') || '').trim().length > 0);
                        if (!text && !hasImgAlt) {
                            const rect = btn.getBoundingClientRect();
                            results.emptyButtons.push({
                                outerHTML: btn.outerHTML.slice(0, 100),
                                className: btn.className,
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            });
                        }
                    });

                    // 3. Duplicate IDs
                    const idCounts = {};
                    document.querySelectorAll('[id]').forEach(el => {
                        const id = el.id.trim();
                        if (id) {
                            idCounts[id] = (idCounts[id] || 0) + 1;
                        }
                    });
                    for (const [id, count] of Object.entries(idCounts)) {
                        if (count > 1 && results.duplicateIds.length < 5) {
                            results.duplicateIds.push({ id, count });
                        }
                    }

                    return results;
                }
            """)

            # 1. Missing <html> lang attribute
            if a11y_data.get("missingDocLang"):
                issues.append({
                    "category": "accessibility",
                    "severity": "medium",
                    "page_url": page_url,
                    "title": "Missing <html> Lang Attribute",
                    "description": "The root <html> element does not specify a 'lang' attribute (e.g., lang='en').",
                    "why_it_matters": "Screen readers use the lang attribute to configure appropriate language pronunciation and speech synthesizers.",
                    "recommendation": "Add a lang attribute to the <html> opening tag, such as `<html lang='en'>`.",
                    "suggested_fix": "Add `lang='en'` to <html> tag.",
                    "selector": "html",
                    "evidence": {"missing_attribute": "lang"}
                })

            # 2. Empty Links without Accessible Names
            for link in a11y_data.get("emptyLinks", []):
                issues.append({
                    "category": "accessibility",
                    "severity": "high",
                    "page_url": page_url,
                    "title": f"Link Missing Accessible Name ({link.get('href') or 'icon link'})",
                    "description": f"The link '{link.get('href')}' contains no visible text or aria-label.",
                    "why_it_matters": "Users navigating with screen readers cannot determine the target of links that only contain unlabelled icons.",
                    "recommendation": "Add inner text, an `aria-label`, or an `alt` tag on the enclosed image/icon.",
                    "suggested_fix": "Add `aria-label='...'` to the <a> tag.",
                    "selector": f"a[href='{link.get('href')}']",
                    "coordinates": {
                        "x": link.get("x", 0),
                        "y": link.get("y", 0),
                        "width": link.get("width", 24),
                        "height": link.get("height", 24),
                        "tag": "a"
                    },
                    "marker_type": "arrow",
                    "evidence": link
                })

            # 3. Empty Buttons
            for btn in a11y_data.get("emptyButtons", []):
                issues.append({
                    "category": "accessibility",
                    "severity": "high",
                    "page_url": page_url,
                    "title": "Button Missing Accessible Text Label",
                    "description": "Button element lacks readable text, `aria-label`, or an `alt` tag.",
                    "why_it_matters": "Screen reader users cannot identify the function of empty icon buttons.",
                    "recommendation": "Add descriptive button text or an `aria-label` attribute.",
                    "suggested_fix": "Add `aria-label='Action description'` to the button.",
                    "selector": "button",
                    "coordinates": {
                        "x": btn.get("x", 0),
                        "y": btn.get("y", 0),
                        "width": btn.get("width", 32),
                        "height": btn.get("height", 32),
                        "tag": "button"
                    },
                    "marker_type": "arrow",
                    "evidence": btn
                })

            # 4. Duplicate Element IDs
            for dup in a11y_data.get("duplicateIds", []):
                issues.append({
                    "category": "accessibility",
                    "severity": "high",
                    "page_url": page_url,
                    "title": f"Duplicate Element ID '#{dup['id']}' ({dup['count']} elements)",
                    "description": f"The ID '{dup['id']}' is used {dup['count']} times in the document.",
                    "why_it_matters": "Duplicate IDs break ARIA references (e.g. aria-labelledby, form labels) and script selectors.",
                    "recommendation": "Ensure all `id` attributes are strictly unique within the page.",
                    "suggested_fix": f"Rename duplicate IDs for #{dup['id']}.",
                    "selector": f"#{dup['id']}",
                    "evidence": dup
                })

        except Exception as e:
            logger.warning(f"Error auditing accessibility on {page_url}: {e}")

        return issues
