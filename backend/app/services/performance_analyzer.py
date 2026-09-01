from typing import List, Dict, Any, Tuple
from playwright.async_api import Page
from backend.app.core.logging import logger


class PerformanceAnalyzer:
    async def analyze_performance(self, page: Page, page_url: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Gathers deterministic browser navigation timing and resource size metrics.
        Returns (metrics_dict, issues_list).
        """
        metrics: Dict[str, Any] = {
            "load_time_ms": 0.0,
            "dom_content_loaded_ms": 0.0,
            "first_contentful_paint_ms": 0.0,
            "transfer_size_bytes": 0,
            "resource_counts": {},
            "heavy_resources": []
        }
        issues: List[Dict[str, Any]] = []

        try:
            perf_data = await page.evaluate("""
                () => {
                    const nav = performance.getEntriesByType('navigation')[0] || {};
                    const paintEntries = performance.getEntriesByType('paint');
                    const fcpEntry = paintEntries.find(e => e.name === 'first-contentful-paint');
                    
                    const resources = performance.getEntriesByType('resource');
                    let totalTransfer = 0;
                    const resourceCounts = { js: 0, css: 0, img: 0, font: 0, other: 0 };
                    const heavy = [];

                    resources.forEach(r => {
                        const size = r.transferSize || r.encodedBodySize || 0;
                        totalTransfer += size;
                        
                        const initType = r.initiatorType;
                        if (initType === 'script') resourceCounts.js++;
                        else if (initType === 'link' || initType === 'css') resourceCounts.css++;
                        else if (initType === 'img' || initType === 'image') resourceCounts.img++;
                        else if (initType === 'font') resourceCounts.font++;
                        else resourceCounts.other++;

                        if (size > 1000000) { // > 1MB
                            heavy.push({
                                name: r.name.slice(0, 100),
                                sizeKb: Math.round(size / 1024),
                                type: initType,
                                durationMs: Math.round(r.duration)
                            });
                        }
                    });

                    const loadTime = nav.loadEventEnd ? (nav.loadEventEnd - nav.startTime) : (nav.duration || 0);
                    const dcl = nav.domContentLoadedEventEnd ? (nav.domContentLoadedEventEnd - nav.startTime) : 0;
                    const fcp = fcpEntry ? fcpEntry.startTime : 0;

                    return {
                        loadTime: Math.round(loadTime),
                        dcl: Math.round(dcl),
                        fcp: Math.round(fcp),
                        totalTransfer: totalTransfer,
                        resourceCounts: resourceCounts,
                        heavyResources: heavy
                    };
                }
            """)

            metrics["load_time_ms"] = float(perf_data.get("loadTime", 0))
            metrics["dom_content_loaded_ms"] = float(perf_data.get("dcl", 0))
            metrics["first_contentful_paint_ms"] = float(perf_data.get("fcp", 0))
            metrics["transfer_size_bytes"] = int(perf_data.get("totalTransfer", 0))
            metrics["resource_counts"] = perf_data.get("resourceCounts", {})
            metrics["heavy_resources"] = perf_data.get("heavyResources", [])

            # 1. Slow Page Load Time (> 3.5s)
            if metrics["load_time_ms"] > 3500:
                issues.append({
                    "category": "performance",
                    "severity": "high" if metrics["load_time_ms"] > 6000 else "medium",
                    "page_url": page_url,
                    "title": f"Slow Page Load Time ({metrics['load_time_ms']}ms)",
                    "description": f"Page took {metrics['load_time_ms']}ms to complete loading (recommended < 2500ms).",
                    "why_it_matters": "Slow page loads dramatically increase bounce rates and negatively affect Google search rankings.",
                    "recommendation": "Enable server compression (Gzip/Brotli), optimize assets, and leverage CDN caching.",
                    "suggested_fix": "Audit bundle size and defer non-critical scripts.",
                    "selector": "window",
                    "evidence": {"load_time_ms": metrics["load_time_ms"]}
                })

            # 2. Slow First Contentful Paint (> 2.0s)
            if metrics["first_contentful_paint_ms"] > 2000:
                issues.append({
                    "category": "performance",
                    "severity": "medium",
                    "page_url": page_url,
                    "title": f"Delayed First Contentful Paint ({metrics['first_contentful_paint_ms']}ms)",
                    "description": f"Users wait {metrics['first_contentful_paint_ms']}ms before any text or image content renders on screen.",
                    "why_it_matters": "FCP represents perceived loading speed. Delays make the website feel sluggish.",
                    "recommendation": "Eliminate render-blocking CSS and fonts.",
                    "suggested_fix": "Preload key fonts and critical CSS.",
                    "selector": "head",
                    "evidence": {"fcp_ms": metrics["first_contentful_paint_ms"]}
                })

            # 3. Oversized individual assets (> 1MB)
            for heavy in metrics["heavy_resources"]:
                issues.append({
                    "category": "performance",
                    "severity": "medium",
                    "page_url": page_url,
                    "title": f"Oversized Asset Payload ({heavy['sizeKb']} KB)",
                    "description": f"Resource '{heavy['name']}' is {heavy['sizeKb']} KB in size.",
                    "why_it_matters": "Large payloads consume user data bandwidth and stall thread execution on mobile devices.",
                    "recommendation": "Compress image assets using WebP/AVIF format or minify JavaScript bundles.",
                    "suggested_fix": f"Compress or lazy-load {heavy['name']}.",
                    "selector": "head",
                    "evidence": heavy
                })

        except Exception as e:
            logger.warning(f"Error analyzing performance on {page_url}: {e}")

        return metrics, issues
