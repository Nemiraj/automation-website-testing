import os
import math
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.services.storage import storage_service


SEVERITY_COLORS = {
    "critical": {"hex": "#ef4444", "rgba": (239, 68, 68, 255), "fill": (239, 68, 68, 40)},
    "high": {"hex": "#f97316", "rgba": (249, 115, 22, 255), "fill": (249, 115, 22, 40)},
    "medium": {"hex": "#f59e0b", "rgba": (245, 158, 11, 255), "fill": (245, 158, 11, 40)},
    "low": {"hex": "#3b82f6", "rgba": (59, 130, 246, 255), "fill": (59, 130, 246, 35)},
    "info": {"hex": "#10b981", "rgba": (16, 185, 129, 255), "fill": (16, 185, 129, 30)}
}


class ScreenshotAnnotator:
    """
    Draws precise visual annotations (bounding boxes, numbered badges, arrows, highlights)
    on Playwright screenshots using exact DOM bounding box coordinates.
    """

    def _get_font(self, size: int = 16) -> ImageFont.ImageFont:
        try:
            # Try common system fonts on Windows / Linux / macOS
            for font_name in ["arial.ttf", "segoeui.ttf", "Helvetica.ttf", "DejaVuSans-Bold.ttf"]:
                try:
                    return ImageFont.truetype(font_name, size)
                except Exception:
                    pass
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    def map_coordinates(
        self,
        box: Dict[str, Any],
        image_size: Tuple[int, int],
        viewport_size: Tuple[int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Maps DOM/CSS pixel coordinates to screenshot image pixels,
        accounting for device pixel ratio or resizing.
        """
        img_w, img_h = image_size
        vp_w, vp_h = viewport_size

        scale_x = img_w / max(1, vp_w)
        scale_y = img_h / max(1, vp_h)

        x = int(box.get("x", 0) * scale_x)
        y = int(box.get("y", 0) * scale_y)
        w = int(box.get("width", 0) * scale_x)
        h = int(box.get("height", 0) * scale_y)

        # Ensure inside image bounds
        x = max(2, min(x, img_w - 10))
        y = max(2, min(y, img_h - 10))
        w = max(10, min(w, img_w - x - 2))
        h = max(10, min(h, img_h - y - 2))

        return x, y, w, h

    def annotate_single_issue(
        self,
        screenshot_path: str,
        issue: Dict[str, Any],
        viewport_size: Tuple[int, int],
        test_id: str
    ) -> Optional[Dict[str, str]]:
        """
        Annotates a screenshot for a single specific issue.
        Returns {"file_path": ..., "url_path": ...} or None if no image/coords.
        """
        if not os.path.exists(screenshot_path):
            return None

        coords = issue.get("coordinates")
        if not coords or not coords.get("width") or not coords.get("height"):
            return None

        try:
            with Image.open(screenshot_path) as img:
                # Convert to RGBA for alpha drawing
                annotated = img.convert("RGBA")
                overlay = Image.new("RGBA", annotated.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(overlay)

                img_w, img_h = annotated.size
                x, y, w, h = self.map_coordinates(coords, (img_w, img_h), viewport_size)

                sev = (issue.get("severity") or "high").lower()
                colors = SEVERITY_COLORS.get(sev, SEVERITY_COLORS["high"])
                stroke_color = colors["rgba"]
                fill_color = colors["fill"]
                issue_num = issue.get("issue_number", 1)
                marker_type = issue.get("marker_type", "rectangle")

                # 1. Draw Bounding Box & Tint
                draw.rectangle([x, y, x + w, y + h], outline=stroke_color, width=3, fill=fill_color)

                # Corner brackets for high-tech premium visual indicator
                corner_len = min(16, min(w // 3, h // 3))
                if corner_len > 4:
                    # Top-left
                    draw.line([(x - 2, y - 2), (x - 2 + corner_len, y - 2)], fill=stroke_color, width=4)
                    draw.line([(x - 2, y - 2), (x - 2, y - 2 + corner_len)], fill=stroke_color, width=4)
                    # Top-right
                    draw.line([(x + w + 2, y - 2), (x + w + 2 - corner_len, y - 2)], fill=stroke_color, width=4)
                    draw.line([(x + w + 2, y - 2), (x + w + 2, y - 2 + corner_len)], fill=stroke_color, width=4)
                    # Bottom-left
                    draw.line([(x - 2, y + h + 2), (x - 2 + corner_len, y + h + 2)], fill=stroke_color, width=4)
                    draw.line([(x - 2, y + h + 2), (x - 2, y + h + 2 - corner_len)], fill=stroke_color, width=4)
                    # Bottom-right
                    draw.line([(x + w + 2, y + h + 2), (x + w + 2 - corner_len, y + h + 2)], fill=stroke_color, width=4)
                    draw.line([(x + w + 2, y + h + 2), (x + w + 2, y + h + 2 - corner_len)], fill=stroke_color, width=4)

                # 2. Draw Numbered Badge Circle
                badge_radius = 16
                badge_center_x = max(badge_radius + 4, x)
                badge_center_y = max(badge_radius + 4, y - badge_radius - 6)

                # Badge drop shadow
                draw.ellipse(
                    [badge_center_x - badge_radius + 2, badge_center_y - badge_radius + 2, badge_center_x + badge_radius + 2, badge_center_y + badge_radius + 2],
                    fill=(0, 0, 0, 140)
                )
                # Badge circle
                draw.ellipse(
                    [badge_center_x - badge_radius, badge_center_y - badge_radius, badge_center_x + badge_radius, badge_center_y + badge_radius],
                    fill=stroke_color,
                    outline=(255, 255, 255, 230),
                    width=2
                )

                # Badge number text
                font = self._get_font(18)
                text_num = str(issue_num)
                draw.text(
                    (badge_center_x, badge_center_y - 1),
                    text_num,
                    fill=(255, 255, 255, 255),
                    anchor="mm",
                    font=font
                )

                # 3. Draw Title Pill Label (if room permits)
                title = (issue.get("title") or "Issue")[:35]
                font_label = self._get_font(12)
                label_x = badge_center_x + badge_radius + 6
                label_y = badge_center_y - 10
                
                # Check if label fits inside image width
                if label_x + 180 < img_w:
                    draw.rounded_rectangle(
                        [label_x, label_y, label_x + len(title) * 8 + 14, label_y + 20],
                        radius=4,
                        fill=(15, 23, 42, 220),
                        outline=stroke_color,
                        width=1
                    )
                    draw.text((label_x + 6, label_y + 3), title, fill=(255, 255, 255, 240), font=font_label)

                # Composite overlay onto original
                final_img = Image.alpha_composite(annotated, overlay).convert("RGB")

                # Save annotated screenshot
                filename = f"annotated_issue_{issue_num}_{test_id}.png"
                out_dir = os.path.join(settings.STORAGE_PATH, "screenshots")
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, filename)
                final_img.save(out_path, format="PNG", optimize=True)

                url_path = f"/api/storage/screenshots/{filename}"
                return {"file_path": out_path, "url_path": url_path}

        except Exception as e:
            logger.error(f"Failed to annotate screenshot for issue {issue.get('title')}: {e}")
            return None

    def annotate_multi_issues(
        self,
        screenshot_path: str,
        issues: List[Dict[str, Any]],
        viewport_size: Tuple[int, int],
        test_id: str,
        viewport_name: str
    ) -> Optional[Dict[str, str]]:
        """
        Creates a combined screenshot with all issue markers annotated on it.
        """
        if not os.path.exists(screenshot_path) or not issues:
            return None

        # Filter issues with valid coordinates
        annotatable_issues = [i for i in issues if i.get("coordinates") and i["coordinates"].get("width")]
        if not annotatable_issues:
            return None

        try:
            with Image.open(screenshot_path) as img:
                annotated = img.convert("RGBA")
                overlay = Image.new("RGBA", annotated.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(overlay)
                img_w, img_h = annotated.size

                for iss in annotatable_issues:
                    coords = iss["coordinates"]
                    x, y, w, h = self.map_coordinates(coords, (img_w, img_h), viewport_size)
                    sev = (iss.get("severity") or "high").lower()
                    colors = SEVERITY_COLORS.get(sev, SEVERITY_COLORS["high"])
                    stroke_color = colors["rgba"]
                    fill_color = colors["fill"]
                    issue_num = iss.get("issue_number", 1)

                    # Draw rectangle
                    draw.rectangle([x, y, x + w, y + h], outline=stroke_color, width=3, fill=fill_color)

                    # Number badge
                    badge_radius = 16
                    badge_center_x = max(badge_radius + 4, x)
                    badge_center_y = max(badge_radius + 4, y - badge_radius - 6)

                    # Shadow & Circle
                    draw.ellipse(
                        [badge_center_x - badge_radius + 2, badge_center_y - badge_radius + 2, badge_center_x + badge_radius + 2, badge_center_y + badge_radius + 2],
                        fill=(0, 0, 0, 140)
                    )
                    draw.ellipse(
                        [badge_center_x - badge_radius, badge_center_y - badge_radius, badge_center_x + badge_radius, badge_center_y + badge_radius],
                        fill=stroke_color,
                        outline=(255, 255, 255, 230),
                        width=2
                    )

                    font = self._get_font(18)
                    draw.text(
                        (badge_center_x, badge_center_y - 1),
                        str(issue_num),
                        fill=(255, 255, 255, 255),
                        anchor="mm",
                        font=font
                    )

                final_img = Image.alpha_composite(annotated, overlay).convert("RGB")
                filename = f"annotated_all_{viewport_name}_{test_id}.png"
                out_dir = os.path.join(settings.STORAGE_PATH, "screenshots")
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, filename)
                final_img.save(out_path, format="PNG", optimize=True)

                url_path = f"/api/storage/screenshots/{filename}"
                return {"file_path": out_path, "url_path": url_path}

        except Exception as e:
            logger.error(f"Failed to create multi-issue annotated screenshot for {viewport_name}: {e}")
            return None


screenshot_annotator = ScreenshotAnnotator()
