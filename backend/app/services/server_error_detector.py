import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup


class ServerErrorDetector:
    """
    Detects browser-visible PHP errors, notices, fatal errors,
    and database connection/query failures rendered in the DOM or response text.
    """

    PHP_PATTERNS = [
        {
            "regex": r"(?:Fatal error|<b>Fatal error</b>):\s*(.+?)(?:in\s+<b>?(.+?)</b>?\s+on\s+line\s+<b>?(\d+)</b>?|$)",
            "severity": "critical",
            "type": "PHP Fatal Error",
            "why": "PHP Fatal errors immediately terminate script execution, preventing page rendering.",
            "rec": "Resolve the fatal error in your PHP script. Check missing classes, functions, or file includes."
        },
        {
            "regex": r"(?:Parse error|<b>Parse error</b>):\s*(.+?)(?:in\s+<b>?(.+?)</b>?\s+on\s+line\s+<b>?(\d+)</b>?|$)",
            "severity": "critical",
            "type": "PHP Parse / Syntax Error",
            "why": "PHP syntax errors prevent the script from being compiled or executed.",
            "rec": "Fix the syntax error (missing semicolon, mismatched braces, or syntax typo)."
        },
        {
            "regex": r"(?:Uncaught (?:Exception|Error)|<b>Uncaught (?:Exception|Error)</b>):\s*(.+?)(?:in\s+<b>?(.+?)</b>?\s+on\s+line\s+<b>?(\d+)</b>?|$)",
            "severity": "critical",
            "type": "PHP Uncaught Exception",
            "why": "Unhandled PHP exceptions crash the request and expose internal stack traces to users.",
            "rec": "Wrap exception-prone logic in try/catch blocks or configure a global error handler."
        },
        {
            "regex": r"(?:Warning|<b>Warning</b>):\s*(.+?)(?:in\s+<b>?(.+?)</b>?\s+on\s+line\s+<b>?(\d+)</b>?|$)",
            "severity": "high",
            "type": "PHP Warning",
            "why": "PHP warnings indicate non-fatal issues (e.g. missing include files, undefined array keys) that may cause runtime bugs.",
            "rec": "Check the condition causing the warning, verify included file paths and array keys."
        },
        {
            "regex": r"(?:Notice|<b>Notice</b>):\s*(.+?)(?:in\s+<b>?(.+?)</b>?\s+on\s+line\s+<b>?(\d+)</b>?|$)",
            "severity": "medium",
            "type": "PHP Notice",
            "why": "PHP notices indicate minor flaws such as accessing undefined variables.",
            "rec": "Initialize variables and verify array keys with isset() or ?? before usage."
        },
        {
            "regex": r"(?:Deprecated|<b>Deprecated</b>):\s*(.+?)(?:in\s+<b>?(.+?)</b>?\s+on\s+line\s+<b>?(\d+)</b>?|$)",
            "severity": "low",
            "type": "PHP Deprecation Notice",
            "why": "Deprecated function usage will break in upcoming PHP version upgrades.",
            "rec": "Replace deprecated functions or features with modern PHP equivalents."
        }
    ]

    DB_PATTERNS = [
        {
            "regex": r"(?:Database connection error|Unable to connect to database|Failed to connect to MySQL|Access denied for user|Connection refused|SQLSTATE\[HY000\]\s*\[\d+\]|mysqli_connect\(\)|mysqli_real_connect\(\)|PDO::__construct\(\)|Unknown database|Table '[^']+' doesn't exist)",
            "severity": "critical",
            "type": "Database Error",
            "why": "Database connection or query failure prevents dynamic content loading and user transactions.",
            "rec": "Check that MySQL/database service is running in XAMPP and verify host, user, password, and database name in your PHP configuration."
        }
    ]

    def scan_page_content(self, html_content: str, page_url: str) -> List[Dict[str, Any]]:
        """
        Scans HTML text for PHP runtime errors, warnings, and database errors.
        """
        issues: List[Dict[str, Any]] = []
        if not html_content:
            return issues

        # 1. Scan PHP errors
        for pat in self.PHP_PATTERNS:
            matches = list(re.finditer(pat["regex"], html_content, re.IGNORECASE | re.MULTILINE))
            for m in matches[:3]:  # Limit duplicates per pattern
                raw_match = m.group(0)
                # Clean HTML tags from match string
                clean_text = re.sub(r"<[^>]+>", "", raw_match).strip()
                # Truncate clean text for display
                snippet = clean_text[:200]

                # Extract line/file if available from regex groups
                file_info = ""
                if len(m.groups()) >= 2 and m.group(2):
                    file_name = re.sub(r"<[^>]+>", "", m.group(2)).strip()
                    line_num = m.group(3) if len(m.groups()) >= 3 and m.group(3) else ""
                    if line_num:
                        file_info = f" in {file_name} on line {line_num}"

                issues.append({
                    "category": "functional",
                    "severity": pat["severity"],
                    "page_url": page_url,
                    "title": f"🔴 {pat['type']} Detected",
                    "description": f"{snippet}{file_info}",
                    "why_it_matters": pat["why"],
                    "recommendation": pat["rec"],
                    "suggested_fix": f"Review error output: '{snippet}'",
                    "selector": "body",
                    "evidence": {
                        "error_type": pat["type"],
                        "error_text": snippet,
                        "raw_snippet": raw_match[:300]
                    }
                })

        # 2. Scan Database errors
        for pat in self.DB_PATTERNS:
            matches = list(re.finditer(pat["regex"], html_content, re.IGNORECASE))
            if matches:
                m = matches[0]
                raw_match = m.group(0)
                # Extract surrounding context
                start = max(0, m.start() - 50)
                end = min(len(html_content), m.end() + 150)
                surrounding = re.sub(r"<[^>]+>", " ", html_content[start:end]).strip()
                surrounding = re.sub(r"\s+", " ", surrounding)[:250]

                issues.append({
                    "category": "functional",
                    "severity": pat["severity"],
                    "page_url": page_url,
                    "title": "🔴 Database Error Detected",
                    "description": f"Page emitted database error signature: {surrounding}",
                    "why_it_matters": pat["why"],
                    "recommendation": pat["rec"],
                    "suggested_fix": "Verify MySQL service status in XAMPP control panel and check database connection parameters (host, dbname, user, password).",
                    "selector": "body",
                    "evidence": {
                        "error_type": pat["type"],
                        "matched_signature": raw_match,
                        "context": surrounding
                    }
                })

        return issues


server_error_detector = ServerErrorDetector()
