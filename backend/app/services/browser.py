import asyncio
from typing import Optional, Dict, Any, List, Callable
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from backend.app.core.logging import logger
from backend.app.core.config import settings


class BrowserSession:
    def __init__(self, playwright: Playwright, browser: Browser):
        self.playwright = playwright
        self.browser = browser

    @classmethod
    async def create(cls) -> "BrowserSession":
        import sys
        if sys.platform == "win32":
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            except Exception:
                pass
        try:
            pw = await async_playwright().start()
            browser = await pw.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--font-render-hinting=none"
                ]
            )
            return cls(pw, browser)
        except Exception as e:
            err_str = str(e)
            if "Executable doesn't exist" in err_str or "playwright install" in err_str:
                logger.info("Chromium browser binary not found. Downloading Chromium automatically...")
                import subprocess
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                pw = await async_playwright().start()
                browser = await pw.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--font-render-hinting=none"
                    ]
                )
                return cls(pw, browser)
            raise e

    async def new_context(
        self,
        viewport_name: str = "desktop_standard",
        custom_viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None
    ) -> BrowserContext:
        vp = custom_viewport
        if not vp:
            vp_def = settings.VIEWPORTS.get(viewport_name, settings.VIEWPORTS["desktop_standard"])
            vp = {"width": vp_def["width"], "height": vp_def["height"]}

        is_mobile = "mobile" in viewport_name.lower()
        ua = user_agent or (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            if is_mobile else
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 WebsiteTesterBot/1.0"
        )

        context = await self.browser.new_context(
            viewport=vp,
            user_agent=ua,
            is_mobile=is_mobile,
            has_touch=is_mobile,
            ignore_https_errors=True
        )
        return context

    async def close(self):
        try:
            await self.browser.close()
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
        try:
            await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error stopping playwright: {e}")


class PageEventManager:
    def __init__(self, page: Page):
        self.page = page
        self.console_messages: List[Dict[str, Any]] = []
        self.page_errors: List[Dict[str, Any]] = []
        self.failed_requests: List[Dict[str, Any]] = []
        self.network_events: List[Dict[str, Any]] = []
        self._attach_listeners()

    def _attach_listeners(self):
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_page_error)
        self.page.on("requestfailed", self._handle_request_failed)
        self.page.on("response", self._handle_response)

    def _handle_console(self, msg):
        try:
            entry = {
                "type": msg.type,
                "text": msg.text,
                "location": msg.location
            }
            self.console_messages.append(entry)
        except Exception:
            pass

    def _handle_page_error(self, err):
        try:
            entry = {
                "message": str(err),
                "name": getattr(err, "name", "PageError")
            }
            self.page_errors.append(entry)
        except Exception:
            pass

    def _handle_request_failed(self, req):
        try:
            entry = {
                "url": req.url,
                "method": req.method,
                "resource_type": req.resource_type,
                "failure": req.failure.error_text if req.failure else "Unknown network error"
            }
            self.failed_requests.append(entry)
        except Exception:
            pass

    def _handle_response(self, resp):
        try:
            if resp.status >= 400:
                self.network_events.append({
                    "url": resp.url,
                    "status": resp.status,
                    "status_text": resp.status_text,
                    "resource_type": resp.request.resource_type
                })
        except Exception:
            pass
