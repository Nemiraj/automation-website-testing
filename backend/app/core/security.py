import ipaddress
import socket
from urllib.parse import urlparse, urlunparse
from typing import Tuple, Dict, Any
from backend.app.core.config import settings


LOCALHOST_HOSTNAMES = {
    "localhost",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "host.docker.internal"
}

BLOCKED_HOSTS = {
    "metadata.google.internal",
    "169.254.169.254"
}


def is_ip_private(ip_str: str) -> bool:
    """Check if an IP string is private, loopback, link-local, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )
    except ValueError:
        return False


def is_localhost_url(url: str) -> Dict[str, Any]:
    """
    Detects if a given URL targets a localhost or local development instance.
    Returns structured info: is_localhost, host, port, path.
    """
    if not url:
        return {"is_localhost": False, "host": "", "port": 80, "path": "/"}

    url_clean = url.strip()
    if not (url_clean.startswith("http://") or url_clean.startswith("https://")):
        url_clean = "http://" + url_clean

    try:
        parsed = urlparse(url_clean)
        hostname = (parsed.hostname or "").lower()
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path or "/"

        is_lh = (
            hostname in LOCALHOST_HOSTNAMES
            or hostname.startswith("127.")
            or hostname.endswith(".localhost")
            or hostname == "host.docker.internal"
        )
        return {
            "is_localhost": is_lh,
            "host": hostname,
            "port": port,
            "path": path
        }
    except Exception:
        return {"is_localhost": False, "host": "", "port": 80, "path": "/"}


def resolve_internal_url(url: str) -> str:
    """
    Resolves localhost URL when running inside Docker containers
    where host.docker.internal should be used instead of localhost.
    """
    if not url:
        return url

    lh_info = is_localhost_url(url)
    if not lh_info["is_localhost"]:
        return url

    target_host = settings.LOCALHOST_HOST
    # If LOCALHOST_HOST is configured and different from localhost/127.0.0.1 (e.g. host.docker.internal)
    if target_host and target_host not in ("localhost", "127.0.0.1"):
        try:
            parsed = urlparse(url)
            # Reconstruct with target_host
            netloc = f"{target_host}:{parsed.port}" if parsed.port else target_host
            return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        except Exception:
            return url
    return url


def validate_target_url(url: str, target_type: str = "live") -> Tuple[bool, str]:
    """
    Validates a target URL against SSRF vulnerabilities, invalid protocols,
    and internal network probes, with explicit support for Localhost testing.
    """
    if not url:
        return False, "URL cannot be empty."
    
    url = url.strip()
    lh_info = is_localhost_url(url)

    # Auto-detect default scheme if not present
    if not (url.startswith("http://") or url.startswith("https://")):
        if target_type == "localhost" or lh_info["is_localhost"]:
            url = "http://" + url
        else:
            url = "https://" + url

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL structure: {str(e)}"

    if parsed.scheme not in ("http", "https"):
        return False, "Only HTTP and HTTPS protocols are supported."

    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid URL: Missing hostname."

    hostname_lower = hostname.lower()

    # If Localhost testing mode or explicitly allowed localhost target
    if target_type == "localhost" or (lh_info["is_localhost"] and settings.ALLOW_LOCALHOST_TESTING):
        if not lh_info["is_localhost"]:
            return False, f"URL '{url}' is not a valid localhost target (expected localhost, 127.0.0.1, ::1, or host.docker.internal)."
        return True, url

    # Live testing mode security checks
    if hostname_lower in BLOCKED_HOSTS or hostname_lower in LOCALHOST_HOSTNAMES:
        return False, f"Targeting internal/local hostname '{hostname}' is not permitted in Live mode. Switch to 'Localhost Website' mode to test local applications."

    if not settings.ALLOW_INTERNAL_NETWORKS:
        try:
            # Resolve DNS
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip = item[4][0]
                if is_ip_private(ip):
                    return False, f"Resolved IP '{ip}' for '{hostname}' is private/internal and cannot be scanned."
        except socket.gaierror:
            return False, f"Could not resolve host '{hostname}'."
        except Exception as e:
            return False, f"DNS resolution error: {str(e)}"

    return True, url


def sanitize_url(url: str) -> str:
    """Normalize and format URL."""
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        if is_localhost_url(url)["is_localhost"]:
            url = "http://" + url
        else:
            url = "https://" + url
    return url

