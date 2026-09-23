"""MCP server exposing arXiv capabilities."""

from __future__ import annotations

import asyncio
import os
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from mcp.server.mcpserver import MCPServer

from research_agent.mcp_servers.arxiv.client import ArxivClient, ArxivClientError
from research_agent.mcp_servers.arxiv.parser import normalize_arxiv_id
from research_agent.mcp_servers.common import PaperCandidate

SCHEMA_VERSION = "1.0"
SOURCE_ID = "arxiv"


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
            "arxiv_id": candidate.source_record_id,
            "openalex_id": None,
            "semantic_scholar_id": None,
            "dblp_key": None,
        },
        "title": candidate.title,
        "authors": [author.model_dump() for author in candidate.authors],
        "year": candidate.year,
        "published_at": candidate.published_at,
        "updated_at": candidate.updated_at,
        "venue": candidate.venue,
        "abstract": candidate.abstract,
        "categories": candidate.categories,
        "urls": {
            "landing": candidate.landing_url,
            "pdf": candidate.pdf_url,
        },
        "open_access": candidate.open_access.model_dump(),
        "provenance": {
            "source": candidate.source,
            "source_record_id": candidate.source_record_id,
            "retrieved_at": retrieved_at,
            "api_endpoint": "https://export.arxiv.org/api/query",
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
        "error": {
            "code": code,
            "message": message,
            "retryable": retryable,
        },
    }


def _client_error_code(exc: ArxivClientError) -> str:
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
        "display_name": "arXiv",
        "source_type": "preprint_repository",
        "api_version": "2026-09",
        "upstream_api_version": "2.0",
        "max_limit": 200,
        "capabilities": {
            "search_papers": True,
            "get_paper": True,
            "get_abstract": True,
            "get_citations": False,
            "get_references": False,
            "resolve_open_access": True,
            "download_pdf": True,
            "author_disambiguation": False,
        },
        "supported_identifiers": ["arxiv_id", "doi"],
        "rate_limit": {
            "requests_per_second": 1,
            "burst": 3,
        },
        "auth_required": False,
        "data_license": "arXiv terms and per-paper license",
        "notes": [
            "PDF download only returns a temporary ArtifactRef.",
            "Full-text rights depend on the individual paper license.",
        ],
    }


def create_arxiv_server(
    client: ArxivClient,
    *,
    artifact_dir: Path,
) -> MCPServer[None]:
    """Create the arXiv MCP server around a configured client."""

    server: MCPServer[None] = MCPServer(
        name="arxiv",
        title="arXiv",
        description="Search and retrieve arXiv paper metadata and open PDFs.",
        version="0.1.0",
    )

    @server.tool(
        name="arxiv_describe",
        description="Return the arXiv capability manifest.",
    )
    async def arxiv_describe() -> dict[str, Any]:
        return _manifest()

    @server.tool(
        name="arxiv_search_papers",
        description="Search arXiv papers and return normalized provenance-bearing items.",
    )
    async def arxiv_search_papers(
        query: str,
        max_results: int = 20,
    ) -> dict[str, Any]:
        retrieved_at = _now()
        try:
            result = await client.search(query, max_results=max_results)
        except ArxivClientError as exc:
            return _error(_client_error_code(exc), str(exc), retryable=True)
        return _envelope(
            source_api="query",
            items=[_candidate_item(paper, retrieved_at) for paper in result.papers],
            retrieved_at=retrieved_at,
        )

    @server.tool(
        name="arxiv_get_paper",
        description="Fetch one arXiv paper by identifier.",
    )
    async def arxiv_get_paper(
        identifier: str,
        identifier_type: str = "arxiv_id",
    ) -> dict[str, Any]:
        if identifier_type not in {"arxiv_id", "arxiv"}:
            return _error(
                "capability_not_supported",
                f"unsupported identifier type: {identifier_type}",
            )
        retrieved_at = _now()
        try:
            candidate = await client.get_paper(identifier)
        except ArxivClientError as exc:
            return _error("not_available", str(exc))
        return _envelope(
            source_api="query",
            items=[_candidate_item(candidate, retrieved_at)],
            retrieved_at=retrieved_at,
        )

    @server.tool(
        name="arxiv_resolve_open_access",
        description="Resolve the open-access PDF location for an arXiv paper.",
    )
    async def arxiv_resolve_open_access(
        identifier: str,
        identifier_type: str = "arxiv_id",
    ) -> dict[str, Any]:
        if identifier_type not in {"arxiv_id", "arxiv"}:
            return _error(
                "capability_not_supported",
                f"unsupported identifier type: {identifier_type}",
            )
        try:
            normalized_id = normalize_arxiv_id(identifier)
        except ValueError as exc:
            return _error("invalid_identifier", str(exc))
        return {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "request_id": _request_id(),
            "source": SOURCE_ID,
            "requested_identifier": identifier,
            "open_access": {
                "is_oa": True,
                "status": "green",
                "license": None,
                "url": f"https://arxiv.org/pdf/{normalized_id}",
            },
        }

    @server.tool(
        name="arxiv_download_pdf",
        description="Download an open arXiv PDF and return a temporary ArtifactRef.",
    )
    async def arxiv_download_pdf(
        identifier: str,
        expected_url: str | None = None,
    ) -> dict[str, Any]:
        try:
            normalized_id = normalize_arxiv_id(identifier)
        except ValueError as exc:
            return _error("invalid_identifier", str(exc))
        url = expected_url or f"https://arxiv.org/pdf/{normalized_id}"
        try:
            artifact = await client.download_pdf(
                url,
                artifact_dir,
                artifact_id=normalized_id,
            )
        except ArxivClientError as exc:
            return _error("download_failed", str(exc), retryable=True)
        return {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "request_id": _request_id(),
            "source": SOURCE_ID,
            "artifact": asdict(artifact),
        }

    return server

def main() -> None:
    """Run the arXiv MCP server over stdio."""

    artifact_dir = Path(
        os.environ.get("RESEARCH_AGENT_ARTIFACT_DIR", "data/cache/downloads")
    )

    async def run() -> None:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            client = ArxivClient(http_client=http_client)
            server = create_arxiv_server(client, artifact_dir=artifact_dir)
            await server.run_stdio_async()

    asyncio.run(run())


if __name__ == "__main__":
    main()
