import os
import re
from typing import Dict, Any, Optional, List
from backend.app.core.logging import logger


class SourceCodeInspector:
    """
    Inspects local project source files (.php, .html, .css, .js) for matching
    CSS selectors or HTML components when local source analysis is enabled.
    """

    EXCLUDED_DIRS = {"node_modules", "vendor", ".git", ".idea", ".vscode", "dist", "build"}

    def inspect_selector_source(
        self,
        selector: Optional[str],
        local_source_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Locates the CSS rule or HTML element in the local codebase.
        Returns source mapping metadata and confidence level.
        """
        if not selector:
            return {
                "source_file": None,
                "line_number": None,
                "snippet": None,
                "confidence": "inferred",
                "search_hint": "Page-level issue (not mapped to a single selector)."
            }

        clean_sel = selector.split(":")[0].strip()
        class_or_id = None

        if "." in clean_sel:
            class_or_id = clean_sel.split(".")[-1].split(" ")[0].strip()
        elif "#" in clean_sel:
            class_or_id = clean_sel.split("#")[-1].split(" ")[0].strip()
        else:
            class_or_id = clean_sel

        # Fallback if no local project directory provided
        if not local_source_dir or not os.path.exists(local_source_dir):
            return {
                "source_file": None,
                "line_number": None,
                "snippet": None,
                "confidence": "inferred",
                "search_hint": f"Search your project codebase for selector `{clean_sel}`."
            }

        try:
            # 1. Search CSS files for the exact rule
            css_matches = self._search_in_files(
                base_dir=local_source_dir,
                patterns=[rf"\.{class_or_id}\s*\{{", rf"\#{class_or_id}\s*\{{", rf"{clean_sel}\s*\{{"],
                extensions=[".css", ".scss", ".less"]
            )
            if css_matches:
                best_match = css_matches[0]
                return {
                    "source_file": best_match["relative_path"],
                    "line_number": best_match["line_number"],
                    "snippet": best_match["snippet"],
                    "confidence": "confirmed",
                    "search_hint": f"Found exact CSS rule in `{best_match['relative_path']}:{best_match['line_number']}`"
                }

            # 2. Search PHP/HTML templates for class/id usage
            html_matches = self._search_in_files(
                base_dir=local_source_dir,
                patterns=[
                    rf'class=["\'][^"\']*\b{class_or_id}\b[^"\']*["\']',
                    rf'id=["\']{class_or_id}["\']',
                    rf'<{clean_sel}\b'
                ],
                extensions=[".php", ".html", ".blade.php", ".twig"]
            )
            if html_matches:
                best_match = html_matches[0]
                return {
                    "source_file": best_match["relative_path"],
                    "line_number": best_match["line_number"],
                    "snippet": best_match["snippet"],
                    "confidence": "likely",
                    "search_hint": f"Found matching element in template `{best_match['relative_path']}:{best_match['line_number']}`"
                }

        except Exception as e:
            logger.warning(f"Error inspecting source code for selector '{selector}': {e}")

        return {
            "source_file": None,
            "line_number": None,
            "snippet": None,
            "confidence": "inferred",
            "search_hint": f"Search your project for `{clean_sel}`."
        }

    def _search_in_files(
        self,
        base_dir: str,
        patterns: List[str],
        extensions: List[str]
    ) -> List[Dict[str, Any]]:
        matches = []
        compiled_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                            for line_idx, line in enumerate(lines, start=1):
                                for cp in compiled_patterns:
                                    if cp.search(line):
                                        # Extract context snippet (3 lines)
                                        start_l = max(0, line_idx - 1)
                                        end_l = min(len(lines), line_idx + 4)
                                        snippet = "".join(lines[start_l:end_l]).strip()
                                        matches.append({
                                            "relative_path": rel_path,
                                            "line_number": line_idx,
                                            "snippet": snippet
                                        })
                                        if len(matches) >= 5:
                                            return matches
                                        break
                    except Exception:
                        continue

        return matches


source_inspector = SourceCodeInspector()
