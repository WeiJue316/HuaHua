from __future__ import annotations

import pytest

from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate
from research_agent.mcp_servers.openalex.client import OpenAlexClientError
from research_agent.runtime.enrichment import OpenAlexAbstractResolver


def _paper(
    *,
    source: str = "crossref",
    doi: str | None = "10.1/example",
    abstract: str | None = None,
) -> PaperCandidate:
    return PaperCandidate(
        source=source,
        source_record_id=doi or "record",
        title="Example paper",
        abstract=abstract,
        doi=doi,
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=False, status="unknown"),
    )


class FakeOpenAlexClient:
    def __init__(
        self,
        *,
        abstract: str | None = "Recovered abstract.",
        raises: bool = False,
    ) -> None:
        self.abstract = abstract
        self.raises = raises
        self.requested: list[str] = []

    async def get_work_by_doi(self, doi: str) -> PaperCandidate | None:
        self.requested.append(doi)
        if self.raises:
            raise OpenAlexClientError("OpenAlex is unavailable")
        if self.abstract is None:
            return None
        return _paper(source="openalex", doi=doi, abstract=self.abstract)


@pytest.mark.asyncio
async def test_resolver_backfills_missing_abstract_through_doi() -> None:
    client = FakeOpenAlexClient()
    resolver = OpenAlexAbstractResolver(client)  # type: ignore[arg-type]

    abstract = await resolver.resolve_abstract(_paper())

    assert abstract == "Recovered abstract."
    assert client.requested == ["10.1/example"]


@pytest.mark.asyncio
async def test_resolver_skips_papers_that_already_have_an_abstract() -> None:
    client = FakeOpenAlexClient()
    resolver = OpenAlexAbstractResolver(client)  # type: ignore[arg-type]

    abstract = await resolver.resolve_abstract(_paper(abstract="Already present."))

    assert abstract is None
    assert client.requested == []


@pytest.mark.asyncio
async def test_resolver_skips_papers_without_a_doi() -> None:
    client = FakeOpenAlexClient()
    resolver = OpenAlexAbstractResolver(client)  # type: ignore[arg-type]

    abstract = await resolver.resolve_abstract(_paper(doi=None))

    assert abstract is None
    assert client.requested == []


@pytest.mark.asyncio
async def test_resolver_degrades_gracefully_when_openalex_fails() -> None:
    client = FakeOpenAlexClient(raises=True)
    resolver = OpenAlexAbstractResolver(client)  # type: ignore[arg-type]

    assert await resolver.resolve_abstract(_paper()) is None


@pytest.mark.asyncio
async def test_resolver_returns_none_when_openalex_has_no_match() -> None:
    client = FakeOpenAlexClient(abstract=None)
    resolver = OpenAlexAbstractResolver(client)  # type: ignore[arg-type]

    assert await resolver.resolve_abstract(_paper()) is None
