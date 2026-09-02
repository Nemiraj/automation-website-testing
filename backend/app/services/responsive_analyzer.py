from typing import List, Dict, Any, Tuple
from playwright.async_api import BrowserContext, Page
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.services.browser import BrowserSession
from backend.app.services.storage import storage_service
from backend.app.services.ui_analyzer import UIAnalyzer
from backend.app.services.dom_inspector import dom_inspector


class ResponsiveAnalyzer:
    def __init__(self):
        self.ui_analyzer = UIAnalyzer()
        self.dom_inspector = dom_inspector

    async def test_page_viewports(
        self,
        browser_session: BrowserSession,
        page_url: str,
        test_id: str,
        viewports_to_test: List[str]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Executes complete page test across multiple viewports with full-page scroll rendering.
        Returns (issues, screenshots_metadata).
        """
        issues: List[Dict[str, Any]] = []
        screenshots_metadata: List[Dict[str, Any]] = []

        for vp_key in viewports_to_test:
            vp_config = settings.VIEWPORTS.get(vp_key, settings.VIEWPORTS["desktop_standard"])
            context = await browser_session.new_context(viewport_name=vp_key)

            try:
                page = await context.new_page()
                try:
                    await page.goto(page_url, wait_until="domcontentloaded", timeout=settings.DEFAULT_TIMEOUT_MS)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=3000)
                    except Exception:
                        pass

                    # 1. Full-page scroll rendering (trigger lazy loads and responsive reflows)
                    await self.dom_inspector.scroll_and_render_full_page(page)

                    # 2. UI & Responsive layout checks in this viewport
                    vp_issues = await self.ui_analyzer.analyze_ui(page, page_url, viewport_name=vp_key)
                    issues.extend(vp_issues)

                    # 3. Deep Full-DOM & Section layout analysis (overlap, overflow, positioning)
                    dom_issues, section_info = await self.dom_inspector.inspect_page_layout_and_sections(page, page_url, viewport_name=vp_key)
                    issues.extend(dom_issues)

                    # 4. Capture Viewport Screenshot
                    vp_bytes = await page.screenshot(full_page=False)
                    fpath, upath = storage_service.save_screenshot_bytes(
                        vp_bytes, test_id=test_id, viewport=vp_key, page_name=page_url.split("/")[-1] or "home"
                    )
                    screenshots_metadata.append({
                        "viewport": vp_key,
                        "width": vp_config["width"],
                        "height": vp_config["height"],
                        "file_path": fpath,
                        "url_path": upath,
                        "is_full_page": False,
                        "section_info": section_info
                    })

                except Exception as e:
                    logger.warning(f"Error testing viewport {vp_key} on {page_url}: {e}")
                finally:
                    await page.close()
            finally:
                await context.close()

        return issues, screenshots_metadata
