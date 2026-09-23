"""MCP server exposing OpenAlex capabilities."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from typing import Any
from uuid import uuid4

import httpx
from mcp.server.mcpserver import MCPServer

from research_agent.mcp_servers.common import PaperCandidate
from research_agent.mcp_servers.openalex.client import OpenAlexClient, OpenAlexClientError

SCHEMA_VERSION = "1.0"
SOURCE_ID = "openalex"


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
            "openalex_id": candidate.source_record_id,
            "semantic_scholar_id": None,
            "dblp_key": None,
        },
        "title": candidate.title,
        "authors": [author.model_dump() for author in candidate.authors],
        "year": candidate.year,
        "published_at": candidate.published_at,
        "venue": candidate.venue,
        "abstract": candidate.abstract,
        "categories": candidate.categories,
        "urls": {"landing": candidate.landing_url, "pdf": candidate.pdf_url},
        "open_access": candidate.open_access.model_dump(),
        "provenance": {
            "source": candidate.source,
            "source_record_id": candidate.source_record_id,
            "retrieved_at": retrieved_at,
            "api_endpoint": "https://api.openalex.org/works",
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


def _client_error_code(exc: OpenAlexClientError) -> str:
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
        "display_name": "OpenAlex",
        "source_type": "metadata_index",
        "api_version": "2026-09",
        "upstream_api_version": "2026-09",
        "max_limit": 200,
        "capabilities": {
            "search_papers": True,
            "get_paper": True,
            "get_abstract": True,
            "get_citations": True,
            "get_references": True,
            "resolve_open_access": True,
            "download_pdf": False,
            "author_disambiguation": True,
        },
        "supported_identifiers": ["doi", "openalex_id", "pmid", "arxiv_id"],
        "rate_limit": {"requests_per_second": 5, "burst": 10},
        "auth_required": False,
        "data_license": "CC0 for metadata; source-specific for full text",
        "notes": ["Full text is not hosted by OpenAlex."],
    }


def create_openalex_server(client: OpenAlexClient) -> MCPServer[None]:
    """Create the OpenAlex MCP server around a configured client."""

    server: MCPServer[None] = MCPServer(
        name="openalex",
        title="OpenAlex",
        description="Search and resolve scholarly metadata through OpenAlex.",
        version="0.1.0",
    )

    @server.tool(name="openalex_describe", description="Return the OpenAlex manifest.")
    async def openalex_describe() -> dict[str, Any]:
        return _manifest()

    @server.tool(
        name="openalex_search_papers",
        description="Search OpenAlex works and return provenance-bearing items.",
    )
    async def openalex_search_papers(
        query: str,
        max_results: int = 20,
    ) -> dict[str, Any]:
        retrieved_at = _now()
        try:
            result = await client.search(query, max_results=max_results)
        except OpenAlexClientError as exc:
            return _error(_client_error_code(exc), str(exc), retryable=True)
        return _envelope(
            source_api="works",
            items=[_candidate_item(paper, retrieved_at) for paper in result.papers],
            retrieved_at=retrieved_at,
        )

    @server.tool(name="openalex_get_paper", description="Fetch one OpenAlex work.")
    async def openalex_get_paper(identifier: str) -> dict[str, Any]:
        retrieved_at = _now()
        try:
            paper = await client.get_paper(identifier)
        except OpenAlexClientError as exc:
            return _error(_client_error_code(exc), str(exc))
        return _envelope(
            source_api="works",
            items=[_candidate_item(paper, retrieved_at)],
            retrieved_at=retrieved_at,
        )

    @server.tool(
        name="openalex_get_citations",
        description="Fetch works citing the given OpenAlex work.",
    )
    async def openalex_get_citations(
        identifier: str,
        max_results: int = 20,
    ) -> dict[str, Any]:
        retrieved_at = _now()
        try:
            result = await client.get_citations(identifier, max_results=max_results)
        except OpenAlexClientError as exc:
            return _error(_client_error_code(exc), str(exc), retryable=True)
        return _envelope(
            source_api="works",
            items=[_candidate_item(paper, retrieved_at) for paper in result.papers],
            retrieved_at=retrieved_at,
        )

    @server.tool(
        name="openalex_get_references",
        description="Fetch works referenced by the given OpenAlex work.",
    )
    async def openalex_get_references(
        identifier: str,
        max_results: int = 20,
    ) -> dict[str, Any]:
        retrieved_at = _now()
        try:
            result = await client.get_references(identifier, max_results=max_results)
        except OpenAlexClientError as exc:
            return _error(_client_error_code(exc), str(exc), retryable=True)
        return _envelope(
            source_api="works",
            items=[_candidate_item(paper, retrieved_at) for paper in result.papers],
            retrieved_at=retrieved_at,
        )

    @server.tool(
        name="openalex_resolve_open_access",
        description="Resolve open-access metadata for an OpenAlex work.",
    )
    async def openalex_resolve_open_access(identifier: str) -> dict[str, Any]:
        try:
            paper = await client.resolve_open_access(identifier)
        except OpenAlexClientError as exc:
            return _error(_client_error_code(exc), str(exc))
        return {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "request_id": _request_id(),
            "source": SOURCE_ID,
            "requested_identifier": identifier,
            "open_access": paper.open_access.model_dump(),
        }

    return server


def main() -> None:
    """Run the OpenAlex MCP server over stdio."""

    async def run() -> None:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            server = create_openalex_server(OpenAlexClient(http_client=http_client))
            await server.run_stdio_async()

    asyncio.run(run())


if __name__ == "__main__":
    main()