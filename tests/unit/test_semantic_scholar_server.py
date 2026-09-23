from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.semantic_scholar.client import SemanticScholarClient
from research_agent.mcp_servers.semantic_scholar.server import (
    create_semantic_scholar_server,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "semantic_scholar_search.json"


def _server() -> object:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return create_semantic_scholar_server(
        SemanticScholarClient(http_client=http_client)
    )


@pytest.mark.asyncio
async def test_semantic_scholar_server_exposes_manifest_and_tools() -> None:
    server = _server()

    tools = await server.list_tools()
    tool_names = {tool.name for tool in tools}
    assert {
        "semantic_scholar_describe",
        "semantic_scholar_search_papers",
        "semantic_scholar_get_paper",
        "semantic_scholar_get_citations",
        "semantic_scholar_get_references",
        "semantic_scholar_resolve_open_access",
    }.issubset(tool_names)

    result = await server.call_tool("semantic_scholar_describe", {})

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["source_id"] == "semantic_scholar"
    assert result.structured_content["source_type"] == "metadata_index"
    assert result.structured_content["capabilities"]["download_pdf"] is False


@pytest.mark.asyncio
async def test_semantic_scholar_server_search_returns_envelope() -> None:
    server = _server()

    result = await server.call_tool(
        "semantic_scholar_search_papers",
        {"query": "evidence chain", "max_results": 5},
    )

    assert result.is_error is False
    assert result.structured_content is not None
    payload = result.structured_content
    assert payload["ok"] is True
    assert payload["source"] == "semantic_scholar"
    assert payload["items"][0]["source_record_id"] == "abc123paper"
