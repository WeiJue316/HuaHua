"""Source registry for constructing configured search clients."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import httpx

from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.crossref.client import CrossrefClient
from research_agent.mcp_servers.dblp.client import DblpClient
from research_agent.mcp_servers.openalex.client import OpenAlexClient
from research_agent.mcp_servers.semantic_scholar.client import SemanticScholarClient
from research_agent.router.federation import SearchClient


class UnsupportedSourceError(ValueError):
    """Raised when a requested source is not registered."""


SOURCE_FACTORIES: dict[str, Callable[[httpx.AsyncClient], SearchClient]] = {
    "arxiv": lambda client: ArxivClient(http_client=client),
    "openalex": lambda client: OpenAlexClient(http_client=client),
    "crossref": lambda client: CrossrefClient(http_client=client),
    "semantic_scholar": lambda client: SemanticScholarClient(http_client=client),
    "dblp": lambda client: DblpClient(http_client=client),
}
SUPPORTED_SOURCES = tuple(SOURCE_FACTORIES)


def build_source_clients(
    http_client: httpx.AsyncClient,
    sources: Iterable[str],
) -> dict[str, SearchClient]:
    """Build source clients for the requested source IDs."""

    clients: dict[str, SearchClient] = {}
    for source in sources:
        factory = SOURCE_FACTORIES.get(source)
        if factory is None:
            raise UnsupportedSourceError(f"unsupported source: {source}")
        clients[source] = factory(http_client)
    return clients