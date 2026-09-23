"""Tests for the per-host request rate limiter."""

from __future__ import annotations

import asyncio
import time

import pytest

from research_agent.mcp_servers.common import (
    DEFAULT_RATE_LIMIT_POLICY,
    HostRateLimiter,
    RateLimitPolicy,
)


def test_semantic_scholar_interval_stays_below_one_request_per_second() -> None:
    """Semantic Scholar allows 1 rps and asks callers to stay below it."""

    interval = DEFAULT_RATE_LIMIT_POLICY.interval_for("api.semanticscholar.org")

    assert interval > 1.0, (
        "the interval must exceed one second, otherwise requests sit exactly on "
        "the provider's threshold instead of below it"
    )


def test_arxiv_interval_respects_the_published_three_second_rule() -> None:
    interval = DEFAULT_RATE_LIMIT_POLICY.interval_for("export.arxiv.org")

    assert interval >= 3.0


@pytest.mark.asyncio
async def test_rate_limiter_spaces_requests_to_the_same_host() -> None:
    limiter = HostRateLimiter(RateLimitPolicy(host_intervals={"example.org": 0.06}))

    started = time.monotonic()
    await limiter.wait("https://example.org/first")
    await limiter.wait("https://example.org/second")
    elapsed = time.monotonic() - started

    assert elapsed >= 0.06


@pytest.mark.asyncio
async def test_rate_limiter_keeps_hosts_independent() -> None:
    limiter = HostRateLimiter(RateLimitPolicy(host_intervals={"slow.example": 0.5}))

    started = time.monotonic()
    await limiter.wait("https://slow.example/a")
    await limiter.wait("https://fast.example/a")
    elapsed = time.monotonic() - started

    assert elapsed < 0.25, "an unrelated host must not inherit another host's interval"


@pytest.mark.asyncio
async def test_rate_limiter_does_not_delay_unlisted_hosts() -> None:
    limiter = HostRateLimiter(RateLimitPolicy(host_intervals={"slow.example": 1.0}))

    started = time.monotonic()
    await limiter.wait("https://unlisted.example/a")
    await limiter.wait("https://unlisted.example/b")

    assert time.monotonic() - started < 0.25


@pytest.mark.asyncio
async def test_rate_limiter_serialises_concurrent_requests() -> None:
    limiter = HostRateLimiter(RateLimitPolicy(host_intervals={"example.org": 0.06}))
    stamps: list[float] = []

    async def one() -> None:
        await limiter.wait("https://example.org/x")
        stamps.append(time.monotonic())

    await asyncio.gather(one(), one(), one())
    stamps.sort()

    gaps = [stamps[i] - stamps[i - 1] for i in range(1, len(stamps))]
    assert all(gap >= 0.055 for gap in gaps), gaps