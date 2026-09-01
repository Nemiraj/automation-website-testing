import pytest
from backend.app.services.crawler import WebsiteCrawler


def test_crawler_url_normalization():
    crawler = WebsiteCrawler(base_url="https://example.com")
    
    assert crawler.normalize_url("https://example.com/about#team") == "https://example.com/about"
    assert crawler.normalize_url("https://example.com/about/") == "https://example.com/about"
    assert crawler.normalize_url("https://example.com/") == "https://example.com"
    assert crawler.normalize_url("https://example.com/search?q=test#top") == "https://example.com/search?q=test"


def test_crawler_domain_check():
    crawler = WebsiteCrawler(base_url="https://example.com")
    
    assert crawler.is_same_domain("https://example.com/contact") is True
    assert crawler.is_same_domain("https://www.example.com/blog") is True
    assert crawler.is_same_domain("https://otherwebsite.com") is False


def test_crawler_resource_filtering():
    crawler = WebsiteCrawler(base_url="https://example.com")
    
    assert crawler.is_crawlable_resource("https://example.com/page") is True
    assert crawler.is_crawlable_resource("https://example.com/doc.pdf") is False
    assert crawler.is_crawlable_resource("https://example.com/photo.jpg") is False
    assert crawler.is_crawlable_resource("mailto:info@example.com") is False
