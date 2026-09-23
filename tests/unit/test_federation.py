from __future__ import annotations

import asyncio

import pytest

from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate
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


def _paper(source: str, record_id: str) -> PaperCandidate:
    return PaperCandidate(
        source=source,
        source_record_id=record_id,
        title=f"Title {record_id}",
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=False, status="unknown"),
    )


class VariantClient:
    """Returns one distinct paper per query and records the queries it saw."""

    def __init__(self, source: str, *, fail_on: frozenset[str] = frozenset()) -> None:
        self.source = source
        self.fail_on = fail_on
        self.queries: list[str] = []

    async def search(self, query: str, *, max_results: int = 20) -> FakeResult:
        del max_results
        self.queries.append(query)
        if query in self.fail_on:
            raise RuntimeError(f"{self.source} failed for {query}")
        return FakeResult([_paper(self.source, f"{self.source}-{query}")])


@pytest.mark.asyncio
async def test_search_sources_runs_every_query_variant_once() -> None:
    client = VariantClient("openalex")

    result = await search_sources(
        {"openalex": client},
        query="evidence chain",
        query_variants=("evidence chain scientific", "evidence chain"),
        max_results_per_source=10,
    )

    assert client.queries == ["evidence chain", "evidence chain scientific"]
    assert result.source_counts == {"openalex": 2}
    assert result.errors == {}
    assert result.variant_errors == {}


@pytest.mark.asyncio
async def test_search_sources_caps_merged_results_per_source() -> None:
    client = VariantClient("openalex")

    result = await search_sources(
        {"openalex": client},
        query="evidence chain",
        query_variants=("evidence chain scientific",),
        max_results_per_source=1,
    )

    assert result.source_counts == {"openalex": 1}
    assert len(result.papers) == 1


@pytest.mark.asyncio
async def test_search_sources_surfaces_partial_variant_failures() -> None:
    client = VariantClient("openalex", fail_on=frozenset({"evidence chain scientific"}))

    result = await search_sources(
        {"openalex": client},
        query="evidence chain",
        query_variants=("evidence chain scientific",),
    )

    assert result.errors == {}
    assert result.source_counts == {"openalex": 1}
    assert "1/2 query variants failed" in result.variant_errors["openalex"]


@pytest.mark.asyncio
async def test_search_sources_reports_error_only_when_every_variant_fails() -> None:
    client = VariantClient("openalex", fail_on=frozenset({"a", "b"}))

    result = await search_sources(
        {"openalex": client},
        query="a",
        query_variants=("b",),
    )

    assert result.errors == {"openalex": "openalex failed for a"}
    assert result.variant_errors == {}
    assert result.source_counts == {"openalex": 0}
