from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.arxiv.server import create_arxiv_server

FIXTURE = Path(__file__).parents[1] / "fixtures" / "arxiv_search.xml"


def _server(tmp_path: Path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            headers={"content-type": "application/atom+xml"},
            request=request,
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = ArxivClient(http_client=http_client)
    return create_arxiv_server(client, artifact_dir=tmp_path)


@pytest.mark.asyncio
async def test_arxiv_server_exposes_capability_manifest(tmp_path: Path) -> None:
    server = _server(tmp_path)

    tools = await server.list_tools()
    tool_names = {tool.name for tool in tools}
    assert {
        "arxiv_describe",
        "arxiv_search_papers",
        "arxiv_get_paper",
        "arxiv_resolve_open_access",
        "arxiv_download_pdf",
    }.issubset(tool_names)

    result = await server.call_tool("arxiv_describe", {})

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["schema_version"] == "1.0"
    assert result.structured_content["source_id"] == "arxiv"
    assert result.structured_content["capabilities"]["search_papers"] is True


@pytest.mark.asyncio
async def test_arxiv_server_search_returns_envelope(tmp_path: Path) -> None:
    server = _server(tmp_path)

    result = await server.call_tool(
        "arxiv_search_papers",
        {"query": "evidence chain", "max_results": 5},
    )

    assert result.is_error is False
    assert result.structured_content is not None
    payload = result.structured_content
    assert payload["ok"] is True
    assert payload["source"] == "arxiv"
    assert len(payload["items"]) == 2
    first = payload["items"][0]
    assert first["source_record_id"] == "2407.18940"
    assert first["provenance"]["source"] == "arxiv"
    assert first["provenance"]["source_record_id"] == "2407.18940"

@pytest.mark.asyncio
async def test_arxiv_server_maps_rate_limit(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="slow down", request=request)

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = ArxivClient(http_client=http_client)
    server = create_arxiv_server(client, artifact_dir=tmp_path)

    result = await server.call_tool(
        "arxiv_search_papers",
        {"query": "evidence chain", "max_results": 5},
    )

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["ok"] is False
    assert result.structured_content["error"]["code"] == "rate_limited"
    assert result.structured_content["error"]["retryable"] is True
