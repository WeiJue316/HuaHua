from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.openalex.client import OpenAlexClient
from research_agent.mcp_servers.openalex.server import create_openalex_server

FIXTURE = Path(__file__).parents[1] / "fixtures" / "openalex_search.json"


def _server() -> object:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            headers={"content-type": "application/json"},
            request=request,
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = OpenAlexClient(http_client=http_client)
    return create_openalex_server(client)


@pytest.mark.asyncio
async def test_openalex_server_exposes_manifest_and_tools() -> None:
    server = _server()

    tools = await server.list_tools()
    tool_names = {tool.name for tool in tools}
    assert {
        "openalex_describe",
        "openalex_search_papers",
        "openalex_get_paper",
        "openalex_get_citations",
        "openalex_get_references",
        "openalex_resolve_open_access",
    }.issubset(tool_names)

    result = await server.call_tool("openalex_describe", {})

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["source_id"] == "openalex"
    assert result.structured_content["source_type"] == "metadata_index"
    assert result.structured_content["capabilities"]["download_pdf"] is False


@pytest.mark.asyncio
async def test_openalex_server_search_returns_envelope() -> None:
    server = _server()

    result = await server.call_tool(
        "openalex_search_papers",
        {"query": "evidence chain", "max_results": 5},
    )

    assert result.is_error is False
    assert result.structured_content is not None
    payload = result.structured_content
    assert payload["ok"] is True
    assert payload["source"] == "openalex"
    assert len(payload["items"]) == 1
    assert payload["items"][0]["source_record_id"] == "W123456789"
    assert payload["items"][0]["provenance"]["source"] == "openalex"
