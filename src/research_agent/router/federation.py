"""Parallel source search used by the research runtime."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, cast

from research_agent.mcp_servers.common import PaperCandidate


class SearchResultLike(Protocol):
    """Result shape shared by source-specific search clients."""

    papers: list[PaperCandidate]


class SearchClient(Protocol):
    """Client interface required by the federation layer."""

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
    ) -> Any: ...


@dataclass(frozen=True)
class FederatedSearchResult:
    """Combined results and per-source failures."""

    papers: list[PaperCandidate]
    source_counts: dict[str, int]
    errors: dict[str, str]


async def search_sources(
    clients: Mapping[str, SearchClient],
    *,
    query: str,
    max_results_per_source: int = 10,
    max_concurrency: int = 5,
) -> FederatedSearchResult:
    """Query all configured sources concurrently."""

    if max_concurrency < 1:
        raise ValueError("max_concurrency must be at least 1")
    source_names = list(clients)
    semaphore = asyncio.Semaphore(max_concurrency)

    async def search_one(source: str) -> Any:
        async with semaphore:
            return await clients[source].search(
                query,
                max_results=max_results_per_source,
            )

    tasks = [search_one(source) for source in source_names]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    papers: list[PaperCandidate] = []
    source_counts: dict[str, int] = {}
    errors: dict[str, str] = {}
    for source, result in zip(source_names, results, strict=True):
        if isinstance(result, BaseException):
            if not isinstance(result, Exception):
                raise result
            errors[source] = str(result)
            source_counts[source] = 0
            continue
        search_result = cast(SearchResultLike, result)
        source_counts[source] = len(search_result.papers)
        papers.extend(search_result.papers)
    return FederatedSearchResult(
        papers=papers,
        source_counts=source_counts,
        errors=errors,
    )
