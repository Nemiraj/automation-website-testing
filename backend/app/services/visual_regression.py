from typing import List, Dict, Any
from backend.app.services.storage import storage_service
from backend.app.core.logging import logger


class VisualRegressionAnalyzer:
    def compare_test_runs(
        self,
        current_screenshots: List[Dict[str, Any]],
        previous_screenshots: List[Dict[str, Any]],
        test_id: str
    ) -> List[Dict[str, Any]]:
        """
        Compares screenshots between current test run and previous test run.
        Returns visual regression issues if significant layout difference is detected.
        """
        issues: List[Dict[str, Any]] = []

        # Index previous screenshots by (page_url, viewport)
        prev_map: Dict[str, Dict[str, Any]] = {}
        for s in previous_screenshots:
            key = f"{s.get('page_url')}_{s.get('viewport')}"
            prev_map[key] = s

        for curr in current_screenshots:
            key = f"{curr.get('page_url')}_{curr.get('viewport')}"
            prev = prev_map.get(key)
            if not prev:
                continue

            curr_file = curr.get("file_path")
            prev_file = prev.get("file_path")
            if not curr_file or not prev_file:
                continue

            diff_pct, diff_url = storage_service.compare_images(
                base_image_path=prev_file,
                current_image_path=curr_file,
                test_id=test_id
            )

            if diff_pct >= 2.0:  # More than 2% visual variation
                severity = "high" if diff_pct >= 10.0 else "medium"
                issues.append({
                    "category": "visual_regression",
                    "severity": severity,
                    "page_url": curr.get("page_url", "/"),
                    "viewport": curr.get("viewport", "desktop"),
                    "title": f"Visual Regression Detected ({diff_pct}% change)",
                    "description": f"Page layout or visual presentation changed by {diff_pct}% compared to the previous test run.",
                    "why_it_matters": "Unintended visual shifts can indicate broken styles, misplaced elements, or unintended layout changes.",
                    "recommendation": "Review the visual difference overlay and confirm if this change was intentional.",
                    "suggested_fix": "Inspect the visual diff overlay to isolate modified elements.",
                    "selector": "body",
                    "screenshot_url": diff_url or curr.get("url_path"),
                    "evidence": {
                        "diff_percentage": diff_pct,
                        "diff_mask_url": diff_url,
                        "current_screenshot": curr.get("url_path"),
                        "previous_screenshot": prev.get("url_path"),
                        "viewport": curr.get("viewport")
                    }
                })

        return issues
