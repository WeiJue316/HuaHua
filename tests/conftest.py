"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from research_agent.mcp_servers import common


@pytest.fixture(autouse=True)
def _disable_http_rate_limiting(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the suite fast.

    Timing behaviour is covered separately in tests/unit/test_rate_limiter.py;
    here the limiter is replaced with a no-op policy so request tests do not
    wait on real intervals.
    """

    monkeypatch.setattr(
        common,
        "DEFAULT_RATE_LIMITER",
        common.HostRateLimiter(common.RateLimitPolicy()),
    )