"""HTTP client for the arXiv Atom API."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx

from research_agent.mcp_servers.arxiv.parser import (
    normalize_arxiv_id,
    parse_search_response,
)
from research_agent.mcp_servers.common import PaperCandidate, RetryPolicy, SleepFn, get_with_retry

ARXIV_API_URL = "https://export.arxiv.org/api/query"


class ArxivClientError(RuntimeError):
    """Raised when arXiv cannot satisfy a request."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class ArxivSearchResult:
    """Normalized result metadata for one arXiv search."""

    query: str
    request_url: str
    response_hash: str
    papers: list[PaperCandidate]


@dataclass(frozen=True)
class ArtifactRef:
    """A downloaded temporary artifact with integrity metadata."""

    artifact_id: str
    artifact_uri: str
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    source_url: str
    final_url: str
    retrieved_at: str
    license: str | None = None


class ArxivClient:
    """Small async client around the public arXiv API."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        api_url: str = ARXIV_API_URL,
        retry_policy: RetryPolicy | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self.http_client = http_client
        self.api_url = api_url
        self.retry_policy = retry_policy or RetryPolicy()
        self.sleep = sleep

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
    ) -> ArxivSearchResult:
        """Search arXiv and parse the Atom response."""

        params: dict[str, str | int] = {
            "search_query": f'all:"{query.strip()}"',
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        try:
            response = await get_with_retry(
                self.http_client,
                self.api_url,
                params=params,
                headers={"User-Agent": "research-agent/0.1"},
                retry_policy=self.retry_policy,
                sleep=self.sleep,
            )
        except httpx.HTTPError as exc:
            raise ArxivClientError(f"arXiv request failed: {exc}") from exc

        if response.status_code >= 400:
            raise ArxivClientError(
                f"arXiv request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        try:
            papers = parse_search_response(response.text)
        except ValueError as exc:
            raise ArxivClientError(f"arXiv response parse failed: {exc}") from exc

        return ArxivSearchResult(
            query=query,
            request_url=str(response.request.url),
            response_hash=hashlib.sha256(response.content).hexdigest(),
            papers=papers,
        )

    async def get_paper(self, identifier: str) -> PaperCandidate:
        """Fetch one paper by arXiv identifier."""

        normalized_id = normalize_arxiv_id(identifier)
        params: dict[str, str | int] = {
            "id_list": normalized_id,
            "start": 0,
            "max_results": 5,
        }
        try:
            response = await get_with_retry(
                self.http_client,
                self.api_url,
                params=params,
                headers={"User-Agent": "research-agent/0.1"},
                retry_policy=self.retry_policy,
                sleep=self.sleep,
            )
        except httpx.HTTPError as exc:
            raise ArxivClientError(f"arXiv request failed: {exc}") from exc

        if response.status_code >= 400:
            raise ArxivClientError(
                f"arXiv request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        try:
            papers = parse_search_response(response.text)
        except ValueError as exc:
            raise ArxivClientError(f"arXiv response parse failed: {exc}") from exc

        for paper in papers:
            if paper.source_record_id == normalized_id:
                return paper
        raise ArxivClientError(f"arXiv paper not found: {normalized_id}")

    async def download_pdf(
        self,
        url: str,
        destination_dir: Path,
        *,
        artifact_id: str,
    ) -> ArtifactRef:
        """Download a PDF into a temporary destination and return its handle."""

        try:
            response = await get_with_retry(
                self.http_client,
                url,
                headers={"User-Agent": "research-agent/0.1"},
                retry_policy=self.retry_policy,
                sleep=self.sleep,
            )
        except httpx.HTTPError as exc:
            raise ArxivClientError(f"arXiv PDF request failed: {exc}") from exc

        if response.status_code >= 400:
            raise ArxivClientError(
                f"arXiv PDF request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        content = response.content
        digest = hashlib.sha256(content).hexdigest()
        destination_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{digest}.pdf"
        (destination_dir / filename).write_bytes(content)

        return ArtifactRef(
            artifact_id=artifact_id,
            artifact_uri=f"artifact://arxiv/{artifact_id}",
            filename=filename,
            content_type=response.headers.get("content-type", "application/pdf").split(
                ";", 1
            )[0],
            size_bytes=len(content),
            sha256=digest,
            source_url=url,
            final_url=str(response.url),
            retrieved_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )
