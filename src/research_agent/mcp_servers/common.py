"""Shared MCP-facing data models and HTTP retry helpers."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import BaseModel, Field

SleepFn = Callable[[float], Awaitable[None]]
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


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
    sleep: SleepFn = asyncio.sleep,
) -> httpx.Response:
    """GET with bounded retries for transient HTTP failures."""

    policy = retry_policy or RetryPolicy()
    last_error: httpx.HTTPError | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
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
