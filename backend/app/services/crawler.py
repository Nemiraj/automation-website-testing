import asyncio
from urllib.parse import urlparse, urljoin, urldefrag
from typing import List, Dict, Any, Set
from playwright.async_api import Page, BrowserContext
from bs4 import BeautifulSoup
from backend.app.core.logging import logger
from backend.app.services.browser import BrowserSession, PageEventManager


class CrawledPageData:
    def __init__(self, url: str):
        self.url: str = url
        self.status_code: int = 200
        self.title: str = ""
        self.meta_description: str = ""
        self.canonical_url: str = ""
        self.links_count: int = 0
        self.images_count: int = 0
        self.forms_count: int = 0
        self.buttons_count: int = 0
        self.scripts_count: int = 0
        self.stylesheets_count: int = 0
        self.headings: Dict[str, List[str]] = {"h1": [], "h2": [], "h3": []}
        self.extracted_internal_links: List[str] = []
        self.extracted_external_links: List[str] = []
        self.html_content: str = ""
        self.response_headers: Dict[str, str] = {}
        self.cookies: List[Dict[str, Any]] = []


class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 10, timeout_ms: int = 30000):
        self.base_url = base_url
        parsed_base = urlparse(base_url)
        self.base_domain = parsed_base.netloc.lower()
        
        # Scoped path prefix for localhost sub-projects (e.g. /mywebsite/)
        base_path = parsed_base.path
        if base_path and base_path != "/":
            self.base_path_prefix = base_path if base_path.endswith("/") else base_path + "/"
        else:
            self.base_path_prefix = "/"
            
        self.max_pages = max_pages
        self.timeout_ms = timeout_ms
        self.visited_urls: Set[str] = set()
        self.discovered_pages: List[CrawledPageData] = []

    def normalize_url(self, raw_url: str) -> str:
        """Normalize URL by stripping hash fragments and normalizing scheme/host."""
        clean_url, _ = urldefrag(raw_url)
        parsed = urlparse(clean_url)
        
        # Remove trailing slash for path comparison if not root
        path = parsed.path
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]
            
        normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized

    def is_same_domain(self, url: str) -> bool:
        """Check if link is internal and stays within base project scope."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain != self.base_domain and domain != f"www.{self.base_domain}" and self.base_domain != f"www.{domain}":
                return False
                
            # If base URL has a subpath prefix (e.g. /mywebsite/), ensure links stay within this path
            if self.base_path_prefix != "/":
                target_path = parsed.path if parsed.path.endswith("/") else parsed.path + "/"
                if not (target_path.startswith(self.base_path_prefix) or parsed.path == self.base_path_prefix.rstrip("/")):
                    return False
                    
            return True
        except Exception:
            return False

    def is_crawlable_resource(self, url: str) -> bool:
        """Ignore media files, PDFs, downloads, mailto, tel links."""
        url_lower = url.lower()
        if url_lower.startswith(("mailto:", "tel:", "javascript:", "data:")):
            return False
        
        ignored_extensions = (
            ".pdf", ".zip", ".tar", ".gz", ".rar", ".7z",
            ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
            ".mp4", ".mp3", ".wav", ".avi", ".mov",
            ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
        )
        return not any(url_lower.split("?")[0].endswith(ext) for ext in ignored_extensions)

    async def crawl(self, browser_session: BrowserSession) -> List[CrawledPageData]:
        context = await browser_session.new_context("desktop_standard")
        queue: List[str] = [self.normalize_url(self.base_url)]
        
        try:
            while queue and len(self.discovered_pages) < self.max_pages:
                current_url = queue.pop(0)
                if current_url in self.visited_urls:
                    continue
                
                self.visited_urls.add(current_url)
                logger.info(f"Crawling page ({len(self.discovered_pages) + 1}/{self.max_pages}): {current_url}")
                
                page = await context.new_page()
                page_data = CrawledPageData(current_url)

                try:
                    resp = await page.goto(current_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                    if resp:
                        page_data.status_code = resp.status
                        page_data.response_headers = await resp.all_headers()
                    
                    # Wait for network idle briefly or small stabilization
                    try:
                        await page.wait_for_load_state("networkidle", timeout=3000)
                    except Exception:
                        pass

                    try:
                        page_data.cookies = await context.cookies()
                    except Exception:
                        pass

                    page_data.title = (await page.title()) or ""
                    html = await page.content()
                    page_data.html_content = html
                    
                    # Parse DOM with BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Meta description
                    meta_desc = soup.find("meta", attrs={"name": lambda v: v and v.lower() == "description"})
                    if meta_desc and meta_desc.get("content"):
                        page_data.meta_description = meta_desc["content"].strip()
                        
                    # Canonical URL
                    canonical = soup.find("link", rel=lambda v: v and "canonical" in v.lower())
                    if canonical and canonical.get("href"):
                        page_data.canonical_url = canonical["href"].strip()

                    # Headings
                    for h_tag in ["h1", "h2", "h3"]:
                        for el in soup.find_all(h_tag):
                            text = el.get_text(strip=True)
                            if text:
                                page_data.headings[h_tag].append(text[:200])

                    # Counts
                    page_data.images_count = len(soup.find_all("img"))
                    page_data.forms_count = len(soup.find_all("form"))
                    page_data.buttons_count = len(soup.find_all(["button", "input[type=button]", "input[type=submit]"]))
                    page_data.scripts_count = len(soup.find_all("script"))
                    page_data.stylesheets_count = len(soup.find_all("link", rel=lambda v: v and "stylesheet" in v))
                    
                    # Links extraction
                    raw_links = soup.find_all("a", href=True)
                    page_data.links_count = len(raw_links)
                    
                    for a in raw_links:
                        href = a["href"].strip()
                        full_url = urljoin(current_url, href)
                        
                        if not self.is_crawlable_resource(full_url):
                            continue
                            
                        if self.is_same_domain(full_url):
                            norm = self.normalize_url(full_url)
                            page_data.extracted_internal_links.append(norm)
                            if norm not in self.visited_urls and norm not in queue:
                                queue.append(norm)
                        else:
                            page_data.extracted_external_links.append(full_url)

                except Exception as e:
                    logger.warning(f"Failed to crawl page {current_url}: {e}")
                    page_data.status_code = 500
                    page_data.title = "Page Load Error"
                finally:
                    await page.close()

                self.discovered_pages.append(page_data)

        finally:
            await context.close()

        return self.discovered_pages
