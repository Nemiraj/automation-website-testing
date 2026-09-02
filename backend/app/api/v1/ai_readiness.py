import asyncio
import uuid
import concurrent.futures
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.app.services.browser import BrowserSession
from backend.app.services.ai_readiness.analyzer import ai_readiness_analyzer
from backend.app.core.security import validate_target_url
from backend.app.core.logging import logger

router = APIRouter()


class AIReadinessScanRequest(BaseModel):
    url: str
    target_type: Optional[str] = "live"  # "live" | "localhost"
    max_pages: Optional[int] = 3


class AIReadinessScanResponse(BaseModel):
    id: str
    target_url: str
    target_type: str
    ai_readiness_score: float
    ai_readiness_data: Dict[str, Any]
    pages_scanned: List[Dict[str, Any]]
    created_at: str


# In-memory store for standalone AI readiness scans
standalone_scans: List[Dict[str, Any]] = []


def _sync_crawl_and_analyze(url: str, is_localhost: bool, max_pages: int) -> Dict[str, Any]:
    """
    Executes Playwright crawling and AI readiness analysis in a dedicated thread
    with WindowsProactorEventLoopPolicy to prevent NotImplementedError on Windows.
    """
    import sys
    if sys.platform == "win32":
        loop = asyncio.WindowsProactorEventLoopPolicy().new_event_loop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _internal_scrape():
        browser_session = await BrowserSession.create()
        pages_data = []
        try:
            context = await browser_session.new_context(viewport_name="desktop_standard")
            page = await context.new_page()

            visited_urls = set()
            queue = [url]
            parsed_base = urlparse(url)

            while queue and len(visited_urls) < max_pages:
                current_url = queue.pop(0)
                if current_url in visited_urls:
                    continue

                try:
                    response = await page.goto(current_url, wait_until="domcontentloaded", timeout=25000)
                    await asyncio.sleep(0.5)
                    visited_urls.add(current_url)

                    title = await page.title()
                    html_content = await page.content()

                    meta_desc = ""
                    try:
                        meta_el = await page.query_selector('meta[name="description"]')
                        if meta_el:
                            meta_desc = (await meta_el.get_attribute("content")) or ""
                    except Exception:
                        pass

                    pages_data.append({
                        "url": current_url,
                        "title": title,
                        "meta_description": meta_desc,
                        "html": html_content,
                        "status_code": response.status if response else 200
                    })

                    # Discover more internal links if under max_pages
                    if len(visited_urls) < max_pages:
                        links = await page.evaluate("""
                            () => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
                        """)
                        for link in links:
                            p_link = urlparse(link)
                            if p_link.netloc == parsed_base.netloc and link not in visited_urls and link not in queue:
                                if not any(link.endswith(ext) for ext in ['.jpg', '.png', '.pdf', '.css', '.js']):
                                    queue.append(link)

                except Exception as e:
                    logger.warning(f"AI Readiness scan could not fetch page {current_url}: {e}")

            await context.close()
        finally:
            await browser_session.close()

        if not pages_data:
            raise ValueError(f"Could not connect to target URL: {url}. Please verify that the server is active.")

        analysis_res = ai_readiness_analyzer.analyze_readiness(
            pages_data=pages_data,
            all_issues=[],
            is_localhost=is_localhost
        )

        return {
            "analysis_res": analysis_res,
            "pages_scanned": [{"url": p["url"], "title": p["title"], "status_code": p["status_code"]} for p in pages_data]
        }

    try:
        return loop.run_until_complete(_internal_scrape())
    finally:
        loop.close()


@router.post("/scan", response_model=AIReadinessScanResponse)
async def scan_ai_readiness(payload: AIReadinessScanRequest):
    url = payload.url.strip()
    target_type = payload.target_type or ("localhost" if "localhost" in url or "127.0.0.1" in url else "live")
    is_localhost = target_type == "localhost" or "localhost" in url or "127.0.0.1" in url

    # Security check and normalization
    is_valid, validated_url_or_err = validate_target_url(url, target_type=target_type)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validated_url_or_err)
    url = validated_url_or_err

    max_p = min(payload.max_pages or 3, 5)

    try:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            scan_result = await loop.run_in_executor(
                pool,
                _sync_crawl_and_analyze,
                url,
                is_localhost,
                max_p
            )

        analysis_res = scan_result["analysis_res"]
        pages_scanned = scan_result["pages_scanned"]

        scan_record = {
            "id": f"ai-scan-{uuid.uuid4().hex[:8]}",
            "target_url": url,
            "target_type": target_type,
            "ai_readiness_score": analysis_res.get("overall_score", 85.0),
            "ai_readiness_data": analysis_res,
            "pages_scanned": pages_scanned,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        # Save to history list
        standalone_scans.insert(0, scan_record)
        if len(standalone_scans) > 20:
            standalone_scans.pop()

        return scan_record

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"AI readiness scan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI readiness scan failed: {str(e)}"
        )


@router.get("/history", response_model=List[AIReadinessScanResponse])
async def get_ai_readiness_history():
    return standalone_scans
