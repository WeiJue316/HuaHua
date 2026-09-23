"""Shared MCP-facing data models and HTTP retry helpers."""

from __future__ import annotations

import asyncio
import os
import random
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field

SleepFn = Callable[[float], Awaitable[None]]
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

CONTACT_ENV_VAR = "RESEARCH_AGENT_CONTACT"
DEFAULT_CONTACT_URL = "https://github.com/WeiJue316/HuaHua"


def contact_email() -> str | None:
    """Return the operator contact email used for polite API pools."""

    value = os.environ.get(CONTACT_ENV_VAR, "").strip()
    return value or None


def user_agent() -> str:
    """Return the User-Agent required by arXiv, Crossref and DBLP policies."""

    email = contact_email()
    if email:
        return f"research-agent/0.1 (+{DEFAULT_CONTACT_URL}; mailto:{email})"
    return f"research-agent/0.1 (+{DEFAULT_CONTACT_URL})"


@dataclass(frozen=True)
class RateLimitPolicy:
    """Per-host minimum interval between consecutive requests."""

    default_interval_seconds: float = 0.0
    host_intervals: Mapping[str, float] = field(default_factory=dict)

    def interval_for(self, host: str) -> float:
        """Return the minimum interval that applies to one host."""

        return self.host_intervals.get(host, self.default_interval_seconds)


DEFAULT_RATE_LIMIT_POLICY = RateLimitPolicy(
    host_intervals={
        # arXiv asks for one request every three seconds.
        "export.arxiv.org": 3.0,
        # Semantic Scholar allows 1 request per second across all endpoints and
        # asks for a rate below that threshold, so leave deliberate margin
        # instead of sitting exactly on the boundary.
        "api.semanticscholar.org": 1.2,
        "dblp.org": 1.0,
        "api.openalex.org": 0.2,
        "api.crossref.org": 0.2,
    }
)


class HostRateLimiter:
    """Serialize requests per host so published rate limits are respected."""

    def __init__(
        self,
        policy: RateLimitPolicy,
        *,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self._policy = policy
        self._sleep = sleep
        self._locks: dict[str, asyncio.Lock] = {}
        self._last_request_at: dict[str, float] = {}

    async def wait(self, url: str) -> None:
        """Sleep until the next request to this host is allowed."""

        host = urlparse(url).netloc
        interval = self._policy.interval_for(host)
        if interval <= 0:
            return
        lock = self._locks.setdefault(host, asyncio.Lock())
        async with lock:
            previous = self._last_request_at.get(host)
            if previous is not None:
                remaining = interval - (time.monotonic() - previous)
                if remaining > 0:
                    await self._sleep(remaining)
            self._last_request_at[host] = time.monotonic()


DEFAULT_RATE_LIMITER = HostRateLimiter(DEFAULT_RATE_LIMIT_POLICY)


@dataclass(frozen=True)
class RetryPolicy:
    """Bounded exponential backoff policy."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 5.0
    jitter_ratio: float = 0.2
    retry_status_codes: frozenset[int] = RETRYABLE_STATUS_CODES

    def delay_for_attempt(
        self,
        attempt: int,
        retry_after_seconds: float | None = None,
    ) -> float:
        """Return the delay before a retry attempt."""

        if retry_after_seconds is not None:
            return max(0.0, retry_after_seconds)
        exponential = min(
            self.max_delay_seconds,
            self.base_delay_seconds * (2 ** max(0, attempt - 1)),
        )
        jitter = exponential * self.jitter_ratio * random.random()
        return float(min(self.max_delay_seconds, exponential + jitter))


def _retry_after_seconds(response: httpx.Response) -> float | None:
    value = response.headers.get("retry-after")
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


async def get_with_retry(
    http_client: httpx.AsyncClient,
    url: str,
    *,
    params: dict[str, str | int] | None = None,
    headers: dict[str, str] | None = None,
    retry_policy: RetryPolicy | None = None,
    rate_limiter: HostRateLimiter | None = None,
    sleep: SleepFn = asyncio.sleep,
) -> httpx.Response:
    """GET with per-host rate limiting and bounded retries."""

    policy = retry_policy or RetryPolicy()
    limiter = rate_limiter or DEFAULT_RATE_LIMITER
    last_error: httpx.HTTPError | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            await limiter.wait(url)
            response = await http_client.get(
                url,
                params=params,
                headers=headers,
            )
        except httpx.HTTPError as exc:
            last_error = exc
            if attempt >= policy.max_attempts:
                raise
            await sleep(policy.delay_for_attempt(attempt))
            continue

        if (
            response.status_code in policy.retry_status_codes
            and attempt < policy.max_attempts
        ):
            retry_after = _retry_after_seconds(response)
            await sleep(policy.delay_for_attempt(attempt, retry_after))
            continue
        return response

    if last_error is not None:
        raise last_error
    raise RuntimeError("HTTP retry loop exhausted without a response")


class Author(BaseModel):
    """Normalized author information."""

    name: str
    orcid: str | None = None
    source_author_id: str | None = None


class OpenAccessInfo(BaseModel):
    """Open-access resolution result."""

    is_oa: bool
    status: str
    license: str | None = None
    url: str | None = None


class PaperCandidate(BaseModel):
    """Source-neutral paper candidate returned by an MCP server."""

    source: str
    source_record_id: str
    source_version: str | None = None
    title: str
    abstract: str | None = None
    authors: list[Author] = Field(default_factory=list)
    year: int | None = None
    published_at: str | None = None
    updated_at: str | None = None
    venue: str | None = None
    categories: list[str] = Field(default_factory=list)
    doi: str | None = None
    landing_url: str
    pdf_url: str | None = None
    open_access: OpenAccessInfo
    raw: dict[str, Any] = Field(default_factory=dict)
