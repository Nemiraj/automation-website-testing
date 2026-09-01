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
                        const hasSvg = !!a.querySelector('svg');
                        
                        if (!text && !hasImgAlt) {
                            results.emptyLinks.push({
                                href: a.getAttribute('href') || '',
                                outerHTML: a.outerHTML.slice(0, 100)
                            });
                        }
                    });

                    // 2. Buttons without text or accessible name
                    document.querySelectorAll('button').forEach(btn => {
                        if (results.emptyButtons.length >= 8) return;
                        const text = (btn.innerText || btn.getAttribute('aria-label') || btn.getAttribute('title') || '').trim();
                        const hasImgAlt = Array.from(btn.querySelectorAll('img')).some(i => (i.getAttribute('alt') || '').trim().length > 0);
                        if (!text && !hasImgAlt) {
                            results.emptyButtons.push({
                                outerHTML: btn.outerHTML.slice(0, 100),
                                className: btn.className
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
                    "selector": "a[href]",
                    "evidence": link
                })

            # 3. Empty Buttons
            for btn in a11y_data.get("emptyButtons", []):
                issues.append({
                    "category": "accessibility",
                    "severity": "high",
                    "page_url": page_url,
                    "title": "Button Missing Accessible Name",
                    "description": "A button element contains only an icon without an aria-label or accessible text.",
                    "why_it_matters": "Blind and low-vision users cannot understand the action triggered by an unlabelled button.",
                    "recommendation": "Add `aria-label='Search'` or `<span class='sr-only'>...</span>` inside the button.",
                    "suggested_fix": "Add `aria-label='...'` to the <button> element.",
                    "selector": "button",
                    "evidence": btn
                })

            # 4. Duplicate IDs
            for dup in a11y_data.get("duplicateIds", []):
                issues.append({
                    "category": "accessibility",
                    "severity": "medium",
                    "page_url": page_url,
                    "title": f"Duplicate Element ID Detected (#{dup['id']})",
                    "description": f"The ID '{dup['id']}' is repeated {dup['count']} times in the document.",
                    "why_it_matters": "HTML IDs must be unique. Duplicate IDs break ARIA references (aria-labelledby/aria-describedby) and DOM selectors.",
                    "recommendation": f"Ensure all elements have unique ID attributes or use CSS classes instead.",
                    "suggested_fix": f"Rename duplicate `id='{dup['id']}'` attributes.",
                    "selector": f"#{dup['id']}",
                    "evidence": dup
                })

        except Exception as e:
            logger.warning(f"Error analyzing accessibility on {page_url}: {e}")

        return issues
