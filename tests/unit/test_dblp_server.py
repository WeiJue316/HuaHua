from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.dblp.client import DblpClient
from research_agent.mcp_servers.dblp.server import create_dblp_server

FIXTURE = Path(__file__).parents[1] / "fixtures" / "dblp_search.json"


def _server() -> object:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return create_dblp_server(DblpClient(http_client=http_client))


@pytest.mark.asyncio
async def test_dblp_server_exposes_manifest_and_tools() -> None:
    server = _server()

    tools = await server.list_tools()
    tool_names = {tool.name for tool in tools}
    assert {
        "dblp_describe",
        "dblp_search_papers",
        "dblp_get_paper",
    }.issubset(tool_names)

    result = await server.call_tool("dblp_describe", {})

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["source_id"] == "dblp"
    assert result.structured_content["source_type"] == "bibliography_database"
    assert result.structured_content["capabilities"]["get_abstract"] is False
    assert result.structured_content["capabilities"]["download_pdf"] is False


@pytest.mark.asyncio
async def test_dblp_server_search_returns_envelope() -> None:
    server = _server()

    result = await server.call_tool(
        "dblp_search_papers",
        {"query": "evidence chain", "max_results": 5},
    )

    assert result.is_error is False
    assert result.structured_content is not None
    payload = result.structured_content
    assert payload["ok"] is True
    assert payload["source"] == "dblp"
    assert payload["items"][0]["source_record_id"] == "conf/example/paper"
