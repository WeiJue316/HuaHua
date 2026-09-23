"""Parallel source search used by the research runtime."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
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
    variant_errors: dict[str, str] = field(default_factory=dict)


def _dedupe_key(paper: PaperCandidate) -> str:
    return paper.source_record_id.strip().lower()


async def search_sources(
    clients: Mapping[str, SearchClient],
    *,
    query: str,
    query_variants: Sequence[str] = (),
    max_results_per_source: int = 10,
    max_concurrency: int = 5,
) -> FederatedSearchResult:
    """Query every source with every query variant and merge the results.

    Counting rules:

    - ``source_counts[source]`` is the number of distinct papers that source
      contributed after its variants were merged and truncated to
      ``max_results_per_source``.
    - ``errors[source]`` is set only when *every* variant of that source
      failed, so a partially failing source stays usable.
    - ``variant_errors[source]`` records partial variant failures without
      hiding the papers that did arrive.

    Variants are merged in the order given and then truncated, so the first
    variant fills the budget and later ones only contribute papers it missed.
    **The caller must therefore order variants best first.** Measured example:
    on csai_007 the full question ranks the gold papers at position 13 and the
    stopword-stripped form at 17, so at ``max_results_per_source=20`` putting
    the question first keeps them while interleaving the variants would drop
    both, since each would only be allotted ten slots.
    """

    if max_concurrency < 1:
        raise ValueError("max_concurrency must be at least 1")
    effective_queries = tuple(dict.fromkeys([query, *query_variants]))
    source_names = list(clients)
    semaphore = asyncio.Semaphore(max_concurrency)

    async def search_one(source: str, variant: str) -> Any:
        async with semaphore:
            return await clients[source].search(
                variant,
                max_results=max_results_per_source,
            )

    tasks = [
        search_one(source, variant)
        for source in source_names
        for variant in effective_queries
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    papers: list[PaperCandidate] = []
    source_counts: dict[str, int] = {}
    errors: dict[str, str] = {}
    variant_errors: dict[str, str] = {}
    width = len(effective_queries)
    for index, source in enumerate(source_names):
        merged: list[PaperCandidate] = []
        seen: set[str] = set()
        failures: list[str] = []
        for result in results[index * width : (index + 1) * width]:
            if isinstance(result, BaseException):
                if not isinstance(result, Exception):
                    raise result
                failures.append(str(result))
                continue
            search_result = cast(SearchResultLike, result)
            for paper in search_result.papers:
                key = _dedupe_key(paper)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(paper)
        if not merged and failures:
            errors[source] = failures[0]
            source_counts[source] = 0
            continue
        if failures:
            variant_errors[source] = (
                f"{len(failures)}/{width} query variants failed: {failures[0]}"
            )
        capped = merged[:max_results_per_source]
        source_counts[source] = len(capped)
        papers.extend(capped)
    return FederatedSearchResult(
        papers=papers,
        source_counts=source_counts,
        errors=errors,
        variant_errors=variant_errors,
    )
