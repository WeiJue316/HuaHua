from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.common import RetryPolicy
from research_agent.mcp_servers.semantic_scholar.client import SemanticScholarClient
from research_agent.mcp_servers.semantic_scholar.server import (
    create_semantic_scholar_server,
    main,
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


@pytest.mark.asyncio
async def test_semantic_scholar_server_reports_timeout_as_failed_envelope() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        server = create_semantic_scholar_server(
            SemanticScholarClient(
                http_client=http_client,
                retry_policy=RetryPolicy(max_attempts=1),
            )
        )
        result = await server.call_tool(
            "semantic_scholar_search_papers",
            {"query": "evidence chain"},
        )

    assert result.structured_content is not None
    assert result.structured_content["ok"] is False
    assert result.structured_content["error"]["code"] == "upstream_unavailable"


def test_semantic_scholar_main_reads_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    import research_agent.mcp_servers.semantic_scholar.server as server_module

    created: list[dict[str, object]] = []
    real = SemanticScholarClient

    class _Spy(real):
        def __init__(self, **kwargs: object) -> None:
            created.append(kwargs)
            super().__init__(**kwargs)  # type: ignore[arg-type]

    async def _stop(self: object) -> None:
        return None

    monkeypatch.setattr(server_module, "SemanticScholarClient", _Spy)
    monkeypatch.setattr(server_module.MCPServer, "run_stdio_async", _stop)
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "test-s2-key")

    main()

    assert created[-1]["api_key"] == "test-s2-key"
