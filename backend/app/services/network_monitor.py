from typing import List, Dict, Any
from backend.app.services.browser import PageEventManager


class NetworkAndJSAnalyzer:
    def analyze_events(self, event_manager: PageEventManager, page_url: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []

        # 1. Page Errors / Uncaught Exceptions
        for err in event_manager.page_errors:
            msg = err.get("message", "Uncaught JavaScript error")
            issues.append({
                "category": "javascript",
                "severity": "critical",
                "page_url": page_url,
                "title": f"JavaScript Runtime Error: {msg[:60]}",
                "description": f"Uncaught exception encountered during page execution: {msg}",
                "why_it_matters": "Uncaught JavaScript exceptions can halt script execution, break user interactions, and cause white screens.",
                "recommendation": "Inspect browser console logs and debug the unhandled exception in your script.",
                "suggested_fix": "Add proper null checks or try-catch guards around the failing script code.",
                "selector": "window",
                "evidence": err
            })

        # 2. Console Errors
        for c in event_manager.console_messages:
            if c.get("type") == "error":
                text = c.get("text", "")
                # Deduplicate if matches page_error
                if any(text in p.get("message", "") for p in event_manager.page_errors):
                    continue
                    
                issues.append({
                    "category": "javascript",
                    "severity": "high",
                    "page_url": page_url,
                    "title": f"Console Error: {text[:60]}",
                    "description": f"The browser emitted a console error: {text}",
                    "why_it_matters": "Console errors indicate underlying JavaScript or asset loading failures.",
                    "recommendation": "Review the code emitting console.error and resolve the root issue.",
                    "suggested_fix": "Check the script source mentioned in console location.",
                    "selector": "console",
                    "evidence": c
                })

        # 3. Failed Network Requests (HTTP 4xx / 5xx or connection drops)
        for req in event_manager.failed_requests:
            url = req.get("url", "")
            resource_type = req.get("resource_type", "resource")
            failure = req.get("failure", "")
            
            issues.append({
                "category": "network",
                "severity": "high" if resource_type in ("script", "stylesheet", "xhr", "fetch") else "medium",
                "page_url": page_url,
                "title": f"Failed {resource_type.upper()} Request",
                "description": f"Request to '{url}' failed: {failure}",
                "why_it_matters": f"Failure to load critical {resource_type} resources leads to broken styling, missing functionality, or degraded experience.",
                "recommendation": f"Verify server availability and CORS headers for '{url}'.",
                "suggested_fix": f"Check endpoint routing, DNS, or firewall blocking {url}.",
                "selector": "network",
                "evidence": req
            })

        # 4. HTTP 4xx / 5xx Responses
        for resp in event_manager.network_events:
            status = resp.get("status", 0)
            url = resp.get("url", "")
            res_type = resp.get("resource_type", "resource")
            
            # Exclude main page itself since crawler records that
            if url != page_url:
                issues.append({
                    "category": "network",
                    "severity": "high" if status in (404, 500, 502, 503) else "medium",
                    "page_url": page_url,
                    "title": f"HTTP {status} on {res_type.upper()} Resource",
                    "description": f"Subresource '{url}' returned HTTP error status {status}.",
                    "why_it_matters": "Missing subresources impair page functionality, visuals, and performance.",
                    "recommendation": f"Fix the endpoint or remove stale reference to '{url}'.",
                    "suggested_fix": f"Verify {url} route and ensure it returns 200 OK.",
                    "selector": "network",
                    "evidence": resp
                })

        return issues
