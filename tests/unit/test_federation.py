from __future__ import annotations

import asyncio

import pytest

from research_agent.mcp_servers.common import PaperCandidate
from research_agent.router.federation import search_sources


class FakeResult:
    def __init__(self, papers: list[PaperCandidate]) -> None:
        self.papers = papers


class FakeClient:
    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0

    async def search(self, query: str, *, max_results: int = 20) -> FakeResult:
        del query, max_results
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        await asyncio.sleep(0.01)
        self.active -= 1
        return FakeResult([])


@pytest.mark.asyncio
async def test_search_sources_respects_concurrency_budget() -> None:
    clients = {f"source-{index}": FakeClient() for index in range(5)}

    await search_sources(
        clients,
        query="evidence chain",
        max_results_per_source=5,
        max_concurrency=2,
    )

    assert all(client.max_active <= 2 for client in clients.values())
