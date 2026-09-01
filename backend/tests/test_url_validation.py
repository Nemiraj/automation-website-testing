import pytest
from backend.app.core.security import validate_target_url, is_ip_private


def test_private_ip_detection():
    assert is_ip_private("127.0.0.1") is True
    assert is_ip_private("192.168.1.1") is True
    assert is_ip_private("10.0.0.1") is True
    assert is_ip_private("172.16.0.1") is True
    assert is_ip_private("169.254.169.254") is True
    assert is_ip_private("8.8.8.8") is False
    assert is_ip_private("1.1.1.1") is False


def test_url_validation_empty():
    is_valid, msg = validate_target_url("")
    assert is_valid is False
    assert "empty" in msg.lower()


def test_url_validation_blocked_hosts():
    is_valid, msg = validate_target_url("http://localhost:3000")
    assert is_valid is False
    assert "not permitted" in msg.lower()

    is_valid, msg = validate_target_url("http://127.0.0.1:8000")
    assert is_valid is False


def test_url_validation_valid_domains():
    is_valid, url = validate_target_url("example.com")
    assert is_valid is True
    assert url == "https://example.com"

    is_valid, url = validate_target_url("https://google.com/test?param=1")
    assert is_valid is True
    assert url.startswith("https://google.com")
