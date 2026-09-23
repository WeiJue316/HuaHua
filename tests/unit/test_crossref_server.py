from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.crossref.client import CrossrefClient
from research_agent.mcp_servers.crossref.server import create_crossref_server

FIXTURE = Path(__file__).parents[1] / "fixtures" / "crossref_search.json"


def _server() -> object:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return create_crossref_server(CrossrefClient(http_client=http_client))


@pytest.mark.asyncio
async def test_crossref_server_exposes_manifest_and_tools() -> None:
    server = _server()

    tools = await server.list_tools()
    tool_names = {tool.name for tool in tools}
    assert {
        "crossref_describe",
        "crossref_search_papers",
        "crossref_get_paper",
        "crossref_get_references",
        "crossref_resolve_open_access",
    }.issubset(tool_names)

    result = await server.call_tool("crossref_describe", {})

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["source_id"] == "crossref"
    assert result.structured_content["source_type"] == "metadata_registry"
    assert result.structured_content["capabilities"]["download_pdf"] is False


@pytest.mark.asyncio
async def test_crossref_server_search_returns_envelope() -> None:
    server = _server()

    result = await server.call_tool(
        "crossref_search_papers",
        {"query": "evidence chain", "max_results": 5},
    )

    assert result.is_error is False
    assert result.structured_content is not None
    payload = result.structured_content
    assert payload["ok"] is True
    assert payload["source"] == "crossref"
    assert payload["items"][0]["identifiers"]["doi"] == "10.1145/1234567.1234568"
