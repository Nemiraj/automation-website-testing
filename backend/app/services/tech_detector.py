import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from backend.app.core.security import is_localhost_url


class TechnologyDetector:
    """
    Analyzes HTTP headers, HTML DOM, cookies, and scripts to accurately
    identify servers, backend frameworks, CMSs, frontend libraries, and databases.
    Never invents information; outputs 'Unknown' when indicators are insufficient.
    """

    def detect_technology(
        self,
        url: str,
        target_type: str = "live",
        headers: Optional[Dict[str, str]] = None,
        html_content: Optional[str] = None,
        cookies: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        headers = headers or {}
        html_content = html_content or ""
        cookies = cookies or []
        soup = BeautifulSoup(html_content, "html.parser") if html_content else None

        detected_server = self._detect_server(headers)
        detected_backend = self._detect_backend(headers, cookies, html_content, soup)
        detected_frontend = self._detect_frontend(html_content, soup)
        
        is_lh = target_type == "localhost" or is_localhost_url(url)["is_localhost"]
        environment = self._detect_environment(is_lh, detected_server, detected_backend, html_content)
        database = self._detect_database(detected_backend, environment, html_content)

        detected_stack = []
        if detected_server and detected_server != "Unknown":
            detected_stack.append(detected_server)
        if detected_backend and detected_backend != "Unknown":
            detected_stack.append(detected_backend)
        if detected_frontend:
            detected_stack.extend(detected_frontend)
        if database and database != "Unknown":
            detected_stack.append(database)

        return {
            "server": detected_server or "Unknown",
            "technology": detected_backend or ("HTML/Static" if detected_frontend else "Unknown"),
            "environment": environment,
            "database": database or "Unknown",
            "frontend_stack": detected_frontend,
            "detected_stack": detected_stack
        }

    def _detect_server(self, headers: Dict[str, str]) -> str:
        server_header = ""
        for k, v in headers.items():
            if k.lower() == "server":
                server_header = v
                break

        if not server_header:
            return "Unknown"

        server_lower = server_header.lower()
        if "apache" in server_lower:
            # Extract version if present
            m = re.search(r"Apache(?:/([0-9.]+))?", server_header, re.IGNORECASE)
            return f"Apache {m.group(1)}" if m and m.group(1) else "Apache"
        elif "nginx" in server_lower:
            m = re.search(r"nginx(?:/([0-9.]+))?", server_header, re.IGNORECASE)
            return f"Nginx {m.group(1)}" if m and m.group(1) else "Nginx"
        elif "litespeed" in server_lower:
            return "LiteSpeed"
        elif "microsoft-iis" in server_lower:
            return "Microsoft IIS"
        elif "caddy" in server_lower:
            return "Caddy"
        return server_header.split(" ")[0] if server_header else "Unknown"

    def _detect_backend(
        self,
        headers: Dict[str, str],
        cookies: List[Dict[str, Any]],
        html_content: str,
        soup: Optional[BeautifulSoup]
    ) -> str:
        # Check X-Powered-By
        x_powered = ""
        for k, v in headers.items():
            if k.lower() == "x-powered-by":
                x_powered = v
                break

        if x_powered:
            xp_lower = x_powered.lower()
            if "php" in xp_lower:
                m = re.search(r"PHP(?:/([0-9.]+))?", x_powered, re.IGNORECASE)
                return f"PHP {m.group(1)}" if m and m.group(1) else "PHP"
            elif "express" in xp_lower:
                return "Express (Node.js)"
            elif "asp.net" in xp_lower:
                return "ASP.NET"
            return x_powered

        # Check session cookies
        cookie_names = [c.get("name", "") for c in cookies]
        if any("PHPSESSID" in name for name in cookie_names):
            return "PHP"
        if any("JSESSIONID" in name for name in cookie_names):
            return "Java"
        if any("csrftoken" in name or "django" in name.lower() for name in cookie_names):
            return "Django (Python)"
        if any("laravel_session" in name for name in cookie_names):
            return "PHP (Laravel)"

        # Check DOM / Links / Forms for .php extensions
        if soup:
            # Check meta generator
            meta_gen = soup.find("meta", attrs={"name": lambda v: v and v.lower() == "generator"})
            if meta_gen and meta_gen.get("content"):
                gen_text = meta_gen["content"]
                if "WordPress" in gen_text:
                    return f"WordPress ({gen_text})"
                elif "Joomla" in gen_text:
                    return "Joomla (PHP)"
                elif "Drupal" in gen_text:
                    return "Drupal (PHP)"

            # Check for PHP script references or links
            php_links = soup.find_all(["a", "form", "script", "link"], href=True)
            for el in php_links:
                href = el.get("href", "").lower()
                if ".php" in href:
                    return "PHP"

            php_actions = soup.find_all("form", action=True)
            for f in php_actions:
                action = f.get("action", "").lower()
                if ".php" in action:
                    return "PHP"

        # Check raw HTML for common PHP error signatures or php tags
        if "<b>Warning</b>:" in html_content or "<b>Fatal error</b>:" in html_content or "<b>Notice</b>:" in html_content:
            return "PHP"

        return "Unknown"

    def _detect_frontend(self, html_content: str, soup: Optional[BeautifulSoup]) -> List[str]:
        libs = []
        if not html_content:
            return libs

        html_lower = html_content.lower()

        if "__next" in html_lower or "_next/static" in html_lower:
            libs.append("Next.js")
        elif "react" in html_lower or 'data-reactroot' in html_lower:
            libs.append("React")

        if "vue" in html_lower or 'data-v-' in html_lower:
            libs.append("Vue.js")

        if "ng-" in html_lower or "ng-version" in html_lower or "angular" in html_lower:
            libs.append("Angular")

        if "bootstrap" in html_lower or "navbar-expand" in html_lower:
            libs.append("Bootstrap")

        if "jquery" in html_lower:
            libs.append("jQuery")

        if "tailwind" in html_lower:
            libs.append("Tailwind CSS")

        return libs

    def _detect_environment(
        self,
        is_localhost: bool,
        server: str,
        backend: str,
        html_content: str
    ) -> str:
        if is_localhost:
            if "apache" in server.lower() or "php" in backend.lower() or "xampp" in html_content.lower():
                return "Localhost/XAMPP"
            return "Localhost/Development"
        return "Live/Production"

    def _detect_database(
        self,
        backend: str,
        environment: str,
        html_content: str
    ) -> str:
        # Check for visible database errors / signatures
        html_lower = html_content.lower()
        if "mysqli_" in html_lower or "mysql" in html_lower or "pdo_mysql" in html_lower:
            return "MySQL"
        elif "pgsql" in html_lower or "postgres" in html_lower:
            return "PostgreSQL"
        elif "sqlite" in html_lower:
            return "SQLite"
        elif "mongodb" in html_lower:
            return "MongoDB"

        # Common XAMPP / PHP default
        if "PHP" in backend or "XAMPP" in environment:
            return "Possibly MySQL"

        return "Unknown"


tech_detector = TechnologyDetector()
