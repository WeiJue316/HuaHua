from __future__ import annotations

import httpx
import pytest

from research_agent.mcp_servers.common import RetryPolicy, get_with_retry


def test_retry_policy_respects_retry_after() -> None:
    policy = RetryPolicy(jitter_ratio=0.0)

    assert policy.delay_for_attempt(1, retry_after_seconds=10) == 10.0
    assert policy.delay_for_attempt(2) == 1.0


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
        response = await get_with_retry(
            http_client,
            "https://example.org/works",
            retry_policy=RetryPolicy(jitter_ratio=0.0),
            sleep=fake_sleep,
        )

    assert response.status_code == 200
    assert calls == 2
    assert delays == [1.0]


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
