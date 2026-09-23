"""Cross-source metadata enrichment for sparse source records."""

from __future__ import annotations

from typing import Protocol

from research_agent.mcp_servers.common import PaperCandidate
from research_agent.mcp_servers.openalex.client import (
    OpenAlexClient,
    OpenAlexClientError,
)


class AbstractResolver(Protocol):
    """Resolve a missing abstract for a paper candidate."""

    async def resolve_abstract(self, candidate: PaperCandidate) -> str | None: ...


class OpenAlexAbstractResolver:
    """Backfill missing abstracts through OpenAlex DOI lookup.

    Sources such as Crossref often return metadata without an abstract, which
    would leave the evidence chain empty for those papers. OpenAlex usually
    holds the abstract for the same DOI, so the runtime can recover a
    traceable evidence span instead of dropping the paper.
    """

    def __init__(self, client: OpenAlexClient) -> None:
        self._client = client

    async def resolve_abstract(self, candidate: PaperCandidate) -> str | None:
        if candidate.abstract or not candidate.doi:
            return None
        try:
            resolved = await self._client.get_work_by_doi(candidate.doi)
        except OpenAlexClientError:
            return None
        if resolved is None:
            return None
        return resolved.abstract
