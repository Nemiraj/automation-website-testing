import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple
from backend.app.core.config import settings


BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
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


def validate_target_url(url: str) -> Tuple[bool, str]:
    """
    Validates a target URL against SSRF vulnerabilities, invalid protocols,
    and internal network probes.
    """
    if not url:
        return False, "URL cannot be empty."
    
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
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

    if not settings.ALLOW_INTERNAL_NETWORKS:
        if hostname_lower in BLOCKED_HOSTS:
            return False, f"Targeting internal/local hostname '{hostname}' is not permitted."

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
        url = "https://" + url
    return url
