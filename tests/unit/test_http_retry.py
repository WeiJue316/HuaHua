from __future__ import annotations

from datetime import UTC, datetime
from email.utils import format_datetime
from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.cache import ResponseCache
from research_agent.mcp_servers.common import (
    RetryPolicy,
    count_http_attempts,
    get_with_retry,
    parse_retry_after,
)


def test_retry_policy_respects_retry_after() -> None:
    policy = RetryPolicy(jitter_ratio=0.0)

    assert policy.delay_for_attempt(1, retry_after_seconds=10) == 10.0
    assert policy.delay_for_attempt(2) == 1.0


def test_parse_retry_after_reads_an_http_date() -> None:
    now = datetime(2026, 10, 14, 1, 0, tzinfo=UTC)

    assert parse_retry_after("Wed, 14 Oct 2026 01:00:30 GMT", now=now) == 30.0
    assert parse_retry_after("30", now=now) == 30.0
    assert parse_retry_after("Wed, 14 Oct 2026 00:00:00 GMT", now=now) == 0.0
    assert parse_retry_after("not a date", now=now) is None


@pytest.mark.asyncio
async def test_get_with_retry_retries_rate_limit_then_succeeds() -> None:
    delays: list[float] = []
    calls = 0

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                429,
                headers={"retry-after": "1"},
                request=request,
            )
        return httpx.Response(200, json={"ok": True}, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        with count_http_attempts() as attempts:
            response = await get_with_retry(
                http_client,
                "https://example.org/works",
                retry_policy=RetryPolicy(jitter_ratio=0.0),
                sleep=fake_sleep,
            )

    assert response.status_code == 200
    assert calls == 2
    assert attempts.calls == 2
    assert delays == [1.0]


@pytest.mark.asyncio
async def test_get_with_retry_waits_for_an_http_date() -> None:
    delays: list[float] = []
    calls = 0
    later = datetime.now(UTC).timestamp() + 30

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            when = format_datetime(datetime.fromtimestamp(later, UTC), usegmt=True)
            return httpx.Response(
                429,
                headers={"retry-after": when},
                request=request,
            )
        return httpx.Response(200, json={"ok": True}, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        response = await get_with_retry(
            http_client,
            "https://example.org/works",
            retry_policy=RetryPolicy(jitter_ratio=0.0),
            sleep=fake_sleep,
        )

    assert response.status_code == 200
    assert len(delays) == 1
    assert delays[0] == pytest.approx(30, abs=1)


@pytest.mark.asyncio
async def test_get_with_retry_stops_after_policy_limit() -> None:
    delays: list[float] = []
    calls = 0

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        response = await get_with_retry(
            http_client,
            "https://example.org/works",
            retry_policy=RetryPolicy(max_attempts=3, jitter_ratio=0.0),
            sleep=fake_sleep,
        )

    assert response.status_code == 503
    assert calls == 3
    assert delays == [0.5, 1.0]


@pytest.mark.asyncio
async def test_response_cache_avoids_a_second_network_call(tmp_path: Path) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return httpx.Response(200, json={"ok": True}, request=request)

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        first = await get_with_retry(
            client, "https://example.org/works", params={"q": "1"}, cache=cache
        )
        second = await get_with_retry(
            client, "https://example.org/works", params={"q": "1"}, cache=cache
        )

    assert len(calls) == 1, "the second call must be served from the cache"
    assert first.text == second.text
    assert str(second.request.url) == "https://example.org/works?q=1"
    assert cache.stats.hits == 1
    assert cache.stats.misses == 1


@pytest.mark.asyncio
async def test_cache_does_not_store_failures(tmp_path: Path) -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(503, json={}, request=request)

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    retry = RetryPolicy(max_attempts=1)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        await get_with_retry(
            client, "https://example.org/works", retry_policy=retry, cache=cache
        )
        await get_with_retry(
            client, "https://example.org/works", retry_policy=retry, cache=cache
        )

    assert len(calls) == 2, "a failed response must be retried, not replayed"
    assert cache.entry_count() == 0
