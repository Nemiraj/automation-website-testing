import os
import pytest
from PIL import Image
from backend.app.services.screenshot_annotator import screenshot_annotator, SEVERITY_COLORS


def test_coordinate_mapping():
    # Test CSS pixel coordinates to screenshot image scaling
    box = {"x": 100, "y": 200, "width": 300, "height": 50}
    # 2x Device Pixel Ratio: Viewport (390, 844), Image (780, 1688)
    image_size = (780, 1688)
    viewport_size = (390, 844)

    x, y, w, h = screenshot_annotator.map_coordinates(box, image_size, viewport_size)
    assert x == 200
    assert y == 400
    assert w == 600
    assert h == 100


def test_annotate_single_issue_creates_image(tmp_path):
    # Create a dummy image
    test_img_path = str(tmp_path / "test_screenshot.png")
    img = Image.new("RGB", (1280, 800), color=(30, 41, 59))
    img.save(test_img_path)

    issue = {
        "title": "Submit button overflows container",
        "severity": "high",
        "issue_number": 1,
        "coordinates": {"x": 300, "y": 400, "width": 200, "height": 60, "tag": "button"},
        "marker_type": "rectangle"
    }

    result = screenshot_annotator.annotate_single_issue(
        screenshot_path=test_img_path,
        issue=issue,
        viewport_size=(1280, 800),
        test_id="test-123"
    )

    assert result is not None
    assert os.path.exists(result["file_path"])
    assert "annotated_issue_1_test-123.png" in result["file_path"]

    # Verify that the generated image opens cleanly and has valid dimensions
    with Image.open(result["file_path"]) as out_img:
        assert out_img.size == (1280, 800)


def test_annotate_multi_issues_creates_combined_image(tmp_path):
    test_img_path = str(tmp_path / "test_multi_screenshot.png")
    img = Image.new("RGB", (390, 844), color=(15, 23, 42))
    img.save(test_img_path)

    issues = [
        {
            "title": "Header overflow",
            "severity": "critical",
            "issue_number": 1,
            "coordinates": {"x": 10, "y": 20, "width": 420, "height": 60}
        },
        {
            "title": "Small touch target",
            "severity": "medium",
            "issue_number": 2,
            "coordinates": {"x": 50, "y": 300, "width": 20, "height": 20}
        }
    ]

    result = screenshot_annotator.annotate_multi_issues(
        screenshot_path=test_img_path,
        issues=issues,
        viewport_size=(390, 844),
        test_id="test-multi-123",
        viewport_name="mobile_portrait"
    )

    assert result is not None
    assert os.path.exists(result["file_path"])
    assert "annotated_all_mobile_portrait_test-multi-123.png" in result["file_path"]
