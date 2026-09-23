"""MCP server exposing DBLP capabilities."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from typing import Any
from uuid import uuid4

import httpx
from mcp.server.mcpserver import MCPServer

from research_agent.mcp_servers.common import PaperCandidate
from research_agent.mcp_servers.dblp.client import DblpClient, DblpClientError

SCHEMA_VERSION = "1.0"
SOURCE_ID = "dblp"


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _request_id() -> str:
    return f"req_{uuid4().hex}"


def _sdk_version() -> str:
    try:
        return version("mcp")
    except PackageNotFoundError:
        return "unknown"


def _candidate_item(candidate: PaperCandidate, retrieved_at: str) -> dict[str, Any]:
    return {
        "source_record_id": candidate.source_record_id,
        "source_version": candidate.source_version,
        "identifiers": {
            "doi": candidate.doi,
            "arxiv_id": None,
            "openalex_id": None,
            "semantic_scholar_id": None,
            "dblp_key": candidate.source_record_id,
        },
        "title": candidate.title,
        "authors": [author.model_dump() for author in candidate.authors],
        "year": candidate.year,
        "venue": candidate.venue,
        "abstract": candidate.abstract,
        "categories": candidate.categories,
        "urls": {"landing": candidate.landing_url, "pdf": None},
        "open_access": candidate.open_access.model_dump(),
        "provenance": {
            "source": candidate.source,
            "source_record_id": candidate.source_record_id,
            "retrieved_at": retrieved_at,
            "api_endpoint": "https://dblp.org/search/publ/api",
        },
        "raw": candidate.raw,
    }


def _envelope(
    *,
    source_api: str,
    items: list[dict[str, Any]],
    retrieved_at: str,
) -> dict[str, Any]:
    return {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "request_id": _request_id(),
        "source": SOURCE_ID,
        "source_api": source_api,
        "retrieved_at": retrieved_at,
        "items": items,
    }


def _error(code: str, message: str, *, retryable: bool = False) -> dict[str, Any]:
    return {
        "ok": False,
        "schema_version": SCHEMA_VERSION,
        "request_id": _request_id(),
        "source": SOURCE_ID,
        "error": {"code": code, "message": message, "retryable": retryable},
    }


def _client_error_code(exc: DblpClientError) -> str:
    if exc.status_code == 429:
        return "rate_limited"
    if exc.status_code == 404:
        return "not_available"
    return "upstream_unavailable"


def _manifest() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol_version": "2026-07-28",
        "sdk_version": _sdk_version(),
        "source_id": SOURCE_ID,
        "display_name": "DBLP",
        "source_type": "bibliography_database",
        "api_version": "2026-09",
        "upstream_api_version": "1.0",
        "max_limit": 1000,
        "capabilities": {
            "search_papers": True,
            "get_paper": True,
            "get_abstract": False,
            "get_citations": False,
            "get_references": False,
            "resolve_open_access": False,
            "download_pdf": False,
            "author_disambiguation": True,
        },
        "supported_identifiers": ["dblp_key", "doi"],
        "rate_limit": {"requests_per_second": 1, "burst": 3},
        "auth_required": False,
        "data_license": "DBLP metadata terms",
        "notes": [
            "DBLP does not provide abstracts or full text.",
        ],
    }


def create_dblp_server(client: DblpClient) -> MCPServer[None]:
    """Create the DBLP MCP server around a configured client."""

    server: MCPServer[None] = MCPServer(
        name="dblp",
        title="DBLP",
        description="Search computer-science bibliography records through DBLP.",
        version="0.1.0",
    )

    @server.tool(name="dblp_describe", description="Return the DBLP manifest.")
    async def dblp_describe() -> dict[str, Any]:
        return _manifest()

    @server.tool(
        name="dblp_search_papers",
        description="Search DBLP publication records.",
    )
    async def dblp_search_papers(
        query: str,
        max_results: int = 20,
    ) -> dict[str, Any]:
        retrieved_at = _now()
        try:
            result = await client.search(query, max_results=max_results)
        except DblpClientError as exc:
            return _error(_client_error_code(exc), str(exc), retryable=True)
        return _envelope(
            source_api="search/publ/api",
            items=[_candidate_item(paper, retrieved_at) for paper in result.papers],
            retrieved_at=retrieved_at,
        )

    @server.tool(
        name="dblp_get_paper",
        description="Fetch one DBLP publication by key.",
    )
    async def dblp_get_paper(identifier: str) -> dict[str, Any]:
        retrieved_at = _now()
        try:
            paper = await client.get_paper(identifier)
        except DblpClientError as exc:
            return _error(_client_error_code(exc), str(exc))
        return _envelope(
            source_api="search/publ/api",
            items=[_candidate_item(paper, retrieved_at)],
            retrieved_at=retrieved_at,
        )

    return server


def main() -> None:
    """Run the DBLP MCP server over stdio."""

    async def run() -> None:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            server = create_dblp_server(DblpClient(http_client=http_client))
            await server.run_stdio_async()

    asyncio.run(run())


if __name__ == "__main__":
    main()
