from typing import List, Dict, Any
from playwright.async_api import Page
from backend.app.core.logging import logger


class ImageAnalyzer:
    async def analyze_images(self, page: Page, page_url: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []

        try:
            # Evaluate all images on the live page DOM
            images_data = await page.evaluate("""
                () => {
                    const results = [];
                    const imgs = document.querySelectorAll('img');
                    imgs.forEach((img, idx) => {
                        const rect = img.getBoundingClientRect();
                        const isVisible = rect.width > 0 && rect.height > 0 && 
                                          window.getComputedStyle(img).display !== 'none' &&
                                          window.getComputedStyle(img).visibility !== 'hidden';
                        
                        results.push({
                            src: img.currentSrc || img.src || '',
                            alt: img.getAttribute('alt'),
                            hasAlt: img.hasAttribute('alt'),
                            naturalWidth: img.naturalWidth,
                            naturalHeight: img.naturalHeight,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            displayedWidth: Math.round(rect.width),
                            displayedHeight: Math.round(rect.height),
                            loading: img.getAttribute('loading'),
                            hasDimensions: img.hasAttribute('width') && img.hasAttribute('height'),
                            complete: img.complete,
                            isVisible: isVisible,
                            id: img.id,
                            className: img.className
                        });
                    });
                    return results;
                }
            """)

            for idx, img in enumerate(images_data):
                src = img.get("src") or f"inline-img-{idx}"
                short_src = src.split("/")[-1].split("?")[0] or src[:40]
                selector = f"img[src*='{short_src[:25]}']" if src.startswith("http") else f"img:nth-of-type({idx+1})"
                coords = {
                    "x": img.get("x", 0),
                    "y": img.get("y", 0),
                    "width": img.get("displayedWidth", 50),
                    "height": img.get("displayedHeight", 50),
                    "tag": "img"
                }

                # 1. Broken image check
                if img.get("complete") and (img.get("naturalWidth") == 0 or img.get("naturalHeight") == 0):
                    issues.append({
                        "category": "functional",
                        "severity": "high",
                        "page_url": page_url,
                        "title": f"Broken Image ({short_src})",
                        "description": f"Image '{src}' failed to load or has 0 natural dimensions.",
                        "why_it_matters": "Broken images create an unprofessional look and ruin the visual experience.",
                        "recommendation": f"Verify that the asset exists at '{src}' and returns a 200 HTTP status.",
                        "suggested_fix": f"Check the file path or CDN URL for {selector}.",
                        "selector": selector,
                        "coordinates": coords,
                        "marker_type": "rectangle",
                        "evidence": {
                            "src": src,
                            "natural_width": img.get("naturalWidth"),
                            "natural_height": img.get("naturalHeight")
                        }
                    })

                # 2. Missing Alt Attribute
                if not img.get("hasAlt"):
                    issues.append({
                        "category": "accessibility",
                        "severity": "medium",
                        "page_url": page_url,
                        "title": f"Image Missing Alt Attribute ({short_src})",
                        "description": f"The image '{short_src}' does not have an alt attribute.",
                        "why_it_matters": "Screen readers cannot describe this image to visually impaired users, and search engines cannot index its content properly.",
                        "recommendation": "Add a descriptive alt attribute (e.g. alt='Company Logo') or alt='' if purely decorative.",
                        "suggested_fix": f"Add alt='...' attribute to {selector}.",
                        "selector": selector,
                        "coordinates": coords,
                        "marker_type": "rectangle",
                        "evidence": {"src": src}
                    })

                # 3. Missing dimensions causing Cumulative Layout Shift (CLS)
                if not img.get("hasDimensions") and img.get("isVisible"):
                    issues.append({
                        "category": "performance",
                        "severity": "low",
                        "page_url": page_url,
                        "title": f"Image Missing Explicit Width/Height ({short_src})",
                        "description": f"The image '{short_src}' lacks explicit HTML width and height attributes.",
                        "why_it_matters": "Browsers cannot reserve space before the image loads, causing layout shifts that hurt Google Core Web Vitals (CLS).",
                        "recommendation": f"Set width='{img.get('displayedWidth')}' height='{img.get('displayedHeight')}' on the image element or define aspect-ratio in CSS.",
                        "suggested_fix": f"Add width and height attributes to {selector}.",
                        "selector": selector,
                        "coordinates": coords,
                        "marker_type": "rectangle",
                        "evidence": {
                            "src": src,
                            "displayed_width": img.get("displayedWidth"),
                            "displayed_height": img.get("displayedHeight")
                        }
                    })

        except Exception as e:
            logger.warning(f"Error analyzing images on {page_url}: {e}")

        return issues
