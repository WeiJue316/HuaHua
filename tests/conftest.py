"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from research_agent.mcp_servers import common


@pytest.fixture(autouse=True)
def _disable_http_rate_limiting(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the suite fast; the rate limiter itself is covered by unit tests."""

    monkeypatch.setattr(
        common,
        "DEFAULT_RATE_LIMITER",
        common.HostRateLimiter(common.RateLimitPolicy()),
    )
