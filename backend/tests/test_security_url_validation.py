import pytest
from backend.app.core.security import validate_target_url


def test_validate_target_url_live_and_localhost():
    # Live URL
    valid_live, res_live = validate_target_url("https://example.com", target_type="live")
    assert valid_live is True
    assert res_live == "https://example.com"

    # Localhost with live mode (should block)
    invalid_lh, err_lh = validate_target_url("http://localhost/mywebsite/", target_type="live")
    assert invalid_lh is False
    assert "Switch to 'Localhost Website' mode" in err_lh

    # Localhost with localhost mode (should pass)
    valid_lh, res_lh = validate_target_url("http://localhost/mywebsite/", target_type="localhost")
    assert valid_lh is True
    assert "localhost" in res_lh
