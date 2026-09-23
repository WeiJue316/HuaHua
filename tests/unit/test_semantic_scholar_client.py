from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.semantic_scholar.client import SemanticScholarClient

FIXTURE = Path(__file__).parents[1] / "fixtures" / "semantic_scholar_search.json"


@pytest.mark.asyncio
async def test_semantic_scholar_client_searches_papers() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/graph/v1/paper/search"
        assert request.url.params["query"] == "evidence chain"
        assert request.url.params["limit"] == "5"
        assert "paperId" in request.url.params["fields"]
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = SemanticScholarClient(http_client=http_client)
        result = await client.search("evidence chain", max_results=5)

    assert result.total == 1
    assert result.next_offset == 1
    assert result.papers[0].source_record_id == "abc123paper"

@pytest.mark.asyncio
async def test_semantic_scholar_client_gets_paper() -> None:
    paper = __import__("json").loads(
        FIXTURE.read_text(encoding="utf-8")
    )["data"][0]

    def handler(request: httpx.Request) -> httpx.Response:
        assert "paperId" in request.url.params["fields"]
        return httpx.Response(200, json=paper, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = SemanticScholarClient(http_client=http_client)
        result = await client.get_paper("10.1000/example")

    assert result.source_record_id == "abc123paper"
    assert result.doi == "10.1000/example"


@pytest.mark.asyncio
async def test_semantic_scholar_client_gets_citations_and_references() -> None:
    paper = __import__("json").loads(
        FIXTURE.read_text(encoding="utf-8")
    )["data"][0]

    def handler(request: httpx.Request) -> httpx.Response:
        key = "citingPaper" if request.url.path.endswith("/citations") else "citedPaper"
        return httpx.Response(
            200,
            json={"total": 1, "offset": 0, "next": 1, "data": [{key: paper}]},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = SemanticScholarClient(http_client=http_client)
        citations = await client.get_citations("abc123paper")
        references = await client.get_references("abc123paper")

    assert citations.papers[0].source_record_id == "abc123paper"
    assert references.papers[0].source_record_id == "abc123paper"
