"""Download allowlist and open-access checks.

The decision records a host and a reason. It does not keep the request URL,
so query tokens are not copied into audit details.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

ALLOWED_DOWNLOAD_HOSTS = frozenset(
    {
        "arxiv.org",
        "www.arxiv.org",
        "export.arxiv.org",
    }
)
_OPEN_ACCESS_STATUSES = frozenset({"gold", "green", "hybrid"})


@dataclass(frozen=True)
class DownloadDecision:
    """Whether one PDF URL may be downloaded."""

    allowed: bool
    reason: str
    host: str


def decide_download(
    *,
    url: str,
    is_open_access: bool,
    open_access_status: str,
) -> DownloadDecision:
    """Allow an open-access PDF whose host is on the download allowlist."""

    host = _host(url)
    if host not in ALLOWED_DOWNLOAD_HOSTS:
        return DownloadDecision(False, "host_not_allowed", host)
    if not _is_open_access(is_open_access, open_access_status):
        return DownloadDecision(False, "not_open_access", host)
    return DownloadDecision(True, "open_access", host)


def _host(url: str) -> str:
    hostname = urlparse(url).hostname
    if not hostname:
        return ""
    return hostname.lower().rstrip(".")


def _is_open_access(is_open_access: bool, status: str) -> bool:
    if is_open_access:
        return True
    return status.strip().lower() in _OPEN_ACCESS_STATUSES
