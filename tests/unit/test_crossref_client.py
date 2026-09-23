from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.crossref.client import CrossrefClient

FIXTURE = Path(__file__).parents[1] / "fixtures" / "crossref_search.json"


@pytest.mark.asyncio
async def test_crossref_client_searches_works() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/works"
        assert request.url.params["query"] == "evidence chain"
        assert request.url.params["rows"] == "5"
        assert request.url.params["cursor"] == "*"
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = CrossrefClient(http_client=http_client)
        result = await client.search("evidence chain", max_results=5)

    assert result.next_cursor == "next-page"
    assert len(result.papers) == 1
    assert result.papers[0].doi == "10.1145/1234567.1234568"


@pytest.mark.asyncio
async def test_crossref_client_gets_work_by_doi() -> None:
    work = json.loads(FIXTURE.read_text(encoding="utf-8"))["message"]["items"][0]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"message": work}, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = CrossrefClient(http_client=http_client)
        paper = await client.get_paper("https://doi.org/10.1145/1234567.1234568")

    assert paper.source_record_id == "10.1145/1234567.1234568"
    assert paper.venue == "Proceedings of the Example Conference"
