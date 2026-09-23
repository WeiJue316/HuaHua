"""Source registry for constructing configured search clients."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable

import httpx

from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.common import contact_email
from research_agent.mcp_servers.crossref.client import CrossrefClient
from research_agent.mcp_servers.dblp.client import DblpClient
from research_agent.mcp_servers.openalex.client import OpenAlexClient
from research_agent.mcp_servers.semantic_scholar.client import SemanticScholarClient
from research_agent.router.federation import SearchClient


class UnsupportedSourceError(ValueError):
    """Raised when a requested source is not registered."""


OPENALEX_API_KEY_ENV_VAR = "OPENALEX_API_KEY"
SEMANTIC_SCHOLAR_API_KEY_ENV_VAR = "SEMANTIC_SCHOLAR_API_KEY"


def _env_value(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def build_openalex_client(http_client: httpx.AsyncClient) -> OpenAlexClient:
    """Build an OpenAlex client carrying the configured polite-pool identity."""

    return OpenAlexClient(
        http_client=http_client,
        mailto=contact_email(),
        api_key=_env_value(OPENALEX_API_KEY_ENV_VAR),
    )


SOURCE_FACTORIES: dict[str, Callable[[httpx.AsyncClient], SearchClient]] = {
    "arxiv": lambda client: ArxivClient(http_client=client),
    "openalex": build_openalex_client,
    "crossref": lambda client: CrossrefClient(
        http_client=client,
        mailto=contact_email(),
    ),
    "semantic_scholar": lambda client: SemanticScholarClient(
        http_client=client,
        api_key=_env_value(SEMANTIC_SCHOLAR_API_KEY_ENV_VAR),
    ),
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
