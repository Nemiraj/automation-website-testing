import pytest
from backend.app.core.security import is_localhost_url, validate_target_url, resolve_internal_url
from backend.app.services.tech_detector import tech_detector
from backend.app.services.server_error_detector import server_error_detector


def test_is_localhost_url_detection():
    r1 = is_localhost_url("http://localhost/mywebsite/")
    assert r1["is_localhost"] is True
    assert r1["host"] == "localhost"
    assert r1["port"] == 80
    assert r1["path"] == "/mywebsite/"

    r2 = is_localhost_url("http://127.0.0.1:8080/testsite/")
    assert r2["is_localhost"] is True
    assert r2["host"] == "127.0.0.1"
    assert r2["port"] == 8080

    r3 = is_localhost_url("http://host.docker.internal:3000/app")
    assert r3["is_localhost"] is True
    assert r3["host"] == "host.docker.internal"
    assert r3["port"] == 3000

    r4 = is_localhost_url("https://example.com/about")
    assert r4["is_localhost"] is False
    assert r4["host"] == "example.com"


def test_validate_target_url_localhost_mode():
    # Localhost mode accepts localhost targets with custom ports and paths
    valid, url = validate_target_url("http://localhost/mywebsite/", target_type="localhost")
    assert valid is True
    assert url == "http://localhost/mywebsite/"

    valid, url = validate_target_url("http://127.0.0.1:8080/mywebsite/", target_type="localhost")
    assert valid is True
    assert url == "http://127.0.0.1:8080/mywebsite/"

    # Localhost mode auto-prepends http if missing scheme
    valid, url = validate_target_url("localhost/testsite/", target_type="localhost")
    assert valid is True
    assert url.startswith("http://localhost")

    # Live mode blocks localhost by default
    valid, msg = validate_target_url("http://localhost/mywebsite/", target_type="live")
    assert valid is False
    assert "not permitted" in msg.lower()


def test_technology_detection():
    # Test Apache + PHP + XAMPP detection from headers and HTML
    headers = {
        "Server": "Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12",
        "X-Powered-By": "PHP/8.2.12"
    }
    cookies = [{"name": "PHPSESSID", "value": "12345"}]
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>My XAMPP Project</title></head>
    <body>
        <form action="process.php" method="POST">
            <input type="text" name="username">
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    result = tech_detector.detect_technology(
        url="http://localhost/mywebsite/",
        target_type="localhost",
        headers=headers,
        html_content=html,
        cookies=cookies
    )
    assert "Apache" in result["server"]
    assert "PHP" in result["technology"]
    assert result["environment"] == "Localhost/XAMPP"
    assert result["database"] == "Possibly MySQL"


def test_server_error_detection_php():
    # Test PHP Warning detection
    html_with_warning = """
    <html>
    <body>
        <b>Warning</b>: Undefined variable $conn in <b>C:\\xampp\\htdocs\\mywebsite\\db.php</b> on line <b>14</b>
        <h1>Welcome</h1>
    </body>
    </html>
    """
    issues = server_error_detector.scan_page_content(html_with_warning, "http://localhost/mywebsite/index.php")
    assert len(issues) >= 1
    php_iss = next(i for i in issues if "PHP Warning" in i["title"])
    assert php_iss["severity"] == "high"
    assert "Undefined variable" in php_iss["description"]
    assert "db.php on line 14" in php_iss["description"]


def test_server_error_detection_mysql_db():
    # Test MySQL Database connection error
    html_with_db_err = """
    <html>
    <body>
        <p>Database connection error: Connection refused to MySQL server at localhost</p>
    </body>
    </html>
    """
    issues = server_error_detector.scan_page_content(html_with_db_err, "http://localhost/mywebsite/products.php")
    assert len(issues) >= 1
    db_iss = next(i for i in issues if "Database Error" in i["title"])
    assert db_iss["severity"] == "critical"
    assert "MySQL" in db_iss["recommendation"]
