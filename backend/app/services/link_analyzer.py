import asyncio
import httpx
from typing import List, Dict, Any, Set
from backend.app.core.logging import logger


class LinkAnalyzer:
    def __init__(self, max_concurrent: int = 10, timeout_sec: float = 10.0):
        self.max_concurrent = max_concurrent
        self.timeout_sec = timeout_sec
        self.checked_urls: Dict[str, Dict[str, Any]] = {}

    async def _check_single_link(self, client: httpx.AsyncClient, link: str) -> Dict[str, Any]:
        if link in self.checked_urls:
            return self.checked_urls[link]

        result = {
            "url": link,
            "status": 200,
            "is_broken": False,
            "error_type": None,
            "message": "OK"
        }

        try:
            # Use HEAD first for efficiency, fallback to GET if method not allowed
            resp = await client.head(link, timeout=self.timeout_sec, follow_redirects=True)
            if resp.status_code == 405:
                resp = await client.get(link, timeout=self.timeout_sec, follow_redirects=True)
            
            result["status"] = resp.status_code
            if resp.status_code >= 400:
                result["is_broken"] = True
                result["error_type"] = f"HTTP {resp.status_code}"
                result["message"] = f"Server returned status code {resp.status_code}"
        except httpx.TimeoutException:
            result["is_broken"] = True
            result["status"] = 408
            result["error_type"] = "Timeout"
            result["message"] = f"Request timed out after {self.timeout_sec}s"
        except httpx.TooManyRedirects:
            result["is_broken"] = True
            result["status"] = 310
            result["error_type"] = "Redirect Loop"
            result["message"] = "Too many redirects detected"
        except httpx.RequestError as e:
            result["is_broken"] = True
            result["status"] = 0
            result["error_type"] = "Connection Error"
            result["message"] = f"Failed to connect: {str(e)}"
        except Exception as e:
            result["is_broken"] = True
            result["status"] = 0
            result["error_type"] = "Invalid URL"
            result["message"] = str(e)

        self.checked_urls[link] = result
        return result

    async def analyze_page_links(self, page_url: str, links: List[str]) -> List[Dict[str, Any]]:
        """
        Tests a list of links discovered on a page and returns structured issue objects for broken links.
        """
        issues = []
        unique_links = list(set(links))
        
        limits = httpx.Limits(max_keepalive_connections=self.max_concurrent, max_connections=self.max_concurrent * 2)
        async with httpx.AsyncClient(limits=limits, verify=False) as client:
            tasks = [self._check_single_link(client, link) for link in unique_links]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, dict) and r.get("is_broken"):
                    status = r.get("status", 0)
                    severity = "critical" if status in (404, 500, 502, 503) else "high"
                    
                    issues.append({
                        "category": "functional",
                        "severity": severity,
                        "page_url": page_url,
                        "title": f"Broken Link ({r['error_type']})",
                        "description": f"The page contains a broken link to '{r['url']}' which failed with: {r['message']}",
                        "why_it_matters": "Broken links frustrate users, hurt search engine rankings, and break navigation paths.",
                        "recommendation": f"Update or remove the href pointing to '{r['url']}'.",
                        "suggested_fix": f"Inspect the <a> tag linking to {r['url']} and provide a valid destination.",
                        "selector": f"a[href*='{r['url'].split('?')[0][-30:]}']",
                        "evidence": {
                            "link_url": r["url"],
                            "http_status": r["status"],
                            "error_type": r["error_type"]
                        }
                    })

        return issues
