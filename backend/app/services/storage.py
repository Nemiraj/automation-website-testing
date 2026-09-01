import os
import uuid
from typing import Optional, Tuple
from PIL import Image, ImageChops
from backend.app.core.config import settings
from backend.app.core.logging import logger


class StorageService:
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        self.screenshots_path = os.path.join(self.storage_path, "screenshots")
        self.diffs_path = os.path.join(self.screenshots_path, "diffs")
        os.makedirs(self.screenshots_path, exist_ok=True)
        os.makedirs(self.diffs_path, exist_ok=True)

    def save_screenshot_bytes(self, image_bytes: bytes, test_id: str, viewport: str, page_name: str = "page") -> Tuple[str, str]:
        """
        Saves screenshot bytes to disk and returns (file_path, url_path).
        """
        safe_page_name = "".join(c for c in page_name if c.isalnum() or c in ("-", "_")).strip() or "page"
        filename = f"{test_id}_{safe_page_name}_{viewport}_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(self.screenshots_path, filename)
        
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        url_path = f"/api/screenshots/{filename}"
        return file_path, url_path

    def compare_images(self, base_image_path: str, current_image_path: str, test_id: str) -> Tuple[float, Optional[str]]:
        """
        Compares two images, computes difference percentage, and saves visual diff mask.
        Returns (diff_percentage, diff_url_path).
        """
        if not os.path.exists(base_image_path) or not os.path.exists(current_image_path):
            return 0.0, None

        try:
            img1 = Image.open(base_image_path).convert("RGBA")
            img2 = Image.open(current_image_path).convert("RGBA")

            # Resize if sizes differ slightly to match base
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.Resampling.BILINEAR)

            diff = ImageChops.difference(img1, img2)
            bbox = diff.getbbox()

            if not bbox:
                return 0.0, None

            # Calculate diff percentage
            diff_data = diff.getdata()
            non_zero_pixels = sum(1 for p in diff_data if any(val > 15 for val in p[:3]))
            total_pixels = img1.size[0] * img1.size[1]
            diff_percentage = round((non_zero_pixels / total_pixels) * 100, 2)

            if diff_percentage > 0.5:
                # Generate visual diff mask image
                diff_filename = f"diff_{test_id}_{uuid.uuid4().hex[:8]}.png"
                diff_file_path = os.path.join(self.diffs_path, diff_filename)
                
                # Blend highlighted diff
                highlight = Image.new("RGBA", img1.size, (255, 0, 0, 100))
                mask = diff.convert("L").point(lambda x: 255 if x > 15 else 0)
                composed = Image.composite(highlight, img2, mask)
                composed.save(diff_file_path, "PNG")

                return diff_percentage, f"/api/screenshots/diffs/{diff_filename}"

            return diff_percentage, None
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            return 0.0, None


storage_service = StorageService()
