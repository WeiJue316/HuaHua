from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.dblp.client import DblpClient, DblpClientError

FIXTURE = Path(__file__).parents[1] / "fixtures" / "dblp_search.json"


@pytest.mark.asyncio
async def test_dblp_client_searches_publications() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/search/publ/api"
        assert request.url.params["q"] == "evidence chain"
        assert request.url.params["format"] == "json"
        assert request.url.params["h"] == "5"
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = DblpClient(http_client=http_client)
        result = await client.search("evidence chain", max_results=5)

    assert result.total == 1
    assert result.papers[0].source_record_id == "conf/example/paper"


@pytest.mark.asyncio
async def test_dblp_client_gets_record_by_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["q"] == "key:conf/example/paper"
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = DblpClient(http_client=http_client)
        paper = await client.get_paper("conf/example/paper")

    assert paper.title == "Traceable Retrieval for Scientific Agents"
    assert paper.year == 2024

@pytest.mark.asyncio
async def test_dblp_client_reports_bot_challenge() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="<!doctype html><html>challenge</html>",
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = DblpClient(http_client=http_client)
        with pytest.raises(DblpClientError, match="bot challenge"):
            await client.search("evidence chain")
