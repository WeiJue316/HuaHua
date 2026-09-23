"""HTTP client for the Semantic Scholar Graph API."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from research_agent.mcp_servers.common import (
    PaperCandidate,
    RetryPolicy,
    SleepFn,
    get_with_retry,
)
from research_agent.mcp_servers.semantic_scholar.parser import (
    SemanticScholarParseError,
    parse_paper,
    parse_search_response,
)

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1"
PAPER_FIELDS = (
    "paperId,corpusId,title,abstract,authors,year,venue,publicationDate,"
    "externalIds,url,openAccessPdf,fieldsOfStudy,citationCount,referenceCount"
)


class SemanticScholarClientError(RuntimeError):
    """Raised when Semantic Scholar cannot satisfy a request."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after_seconds: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True)
class SemanticScholarSearchResult:
    """Normalized Semantic Scholar search or graph result."""

    total: int
    next_offset: int | None
    papers: list[PaperCandidate]


class SemanticScholarClient:
    """Small async client around Semantic Scholar's Graph API."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        api_url: str = SEMANTIC_SCHOLAR_API_URL,
        api_key: str | None = None,
        retry_policy: RetryPolicy | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self.http_client = http_client
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.retry_policy = retry_policy or RetryPolicy()
        self.sleep = sleep

    def _headers(self) -> dict[str, str]:
        headers = {"User-Agent": "research-agent/0.1"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def _get_json(
        self,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
    ) -> dict[str, Any]:
        response = await get_with_retry(
            self.http_client,
            f"{self.api_url}{path}",
            params=params,
            headers=self._headers(),
            retry_policy=self.retry_policy,
            sleep=self.sleep,
        )
        if response.status_code >= 400:
            retry_after = response.headers.get("retry-after")
            retry_after_seconds = (
                int(retry_after)
                if retry_after and retry_after.isdigit()
                else None
            )
            raise SemanticScholarClientError(
                f"Semantic Scholar request failed with status {response.status_code}",
                status_code=response.status_code,
                retry_after_seconds=retry_after_seconds,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise SemanticScholarClientError(
                f"Semantic Scholar response is not JSON: {exc}"
            ) from exc
        if not isinstance(payload, dict):
            raise SemanticScholarClientError(
                "Semantic Scholar response must be a JSON object"
            )
        return payload

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
        offset: int = 0,
    ) -> SemanticScholarSearchResult:
        """Search Semantic Scholar papers."""

        payload = await self._get_json(
            "/paper/search",
            params={
                "query": query.strip(),
                "limit": max_results,
                "offset": offset,
                "fields": PAPER_FIELDS,
            },
        )
        try:
            page = parse_search_response(json.dumps(payload))
        except SemanticScholarParseError as exc:
            raise SemanticScholarClientError(
                f"Semantic Scholar response parse failed: {exc}"
            ) from exc
        return SemanticScholarSearchResult(
            total=page.total,
            next_offset=page.next_offset,
            papers=page.papers,
        )

    async def get_paper(self, identifier: str) -> PaperCandidate:
        """Fetch one Semantic Scholar paper."""

        paper_id = _semantic_scholar_id(identifier)
        payload = await self._get_json(
            f"/paper/{quote(paper_id, safe=':')}",
            params={"fields": PAPER_FIELDS},
        )
        try:
            return parse_paper(payload)
        except SemanticScholarParseError as exc:
            raise SemanticScholarClientError(
                f"Semantic Scholar response parse failed: {exc}"
            ) from exc

    async def resolve_open_access(self, identifier: str) -> PaperCandidate:
        """Resolve candidate open-access metadata from a paper record."""

        return await self.get_paper(identifier)

    async def get_citations(
        self,
        identifier: str,
        *,
        max_results: int = 20,
        offset: int = 0,
    ) -> SemanticScholarSearchResult:
        """Fetch papers that cite the target paper."""

        return await self._related(
            identifier,
            relation="citations",
            embedded_key="citingPaper",
            max_results=max_results,
            offset=offset,
        )

    async def get_references(
        self,
        identifier: str,
        *,
        max_results: int = 20,
        offset: int = 0,
    ) -> SemanticScholarSearchResult:
        """Fetch papers referenced by the target paper."""

        return await self._related(
            identifier,
            relation="references",
            embedded_key="citedPaper",
            max_results=max_results,
            offset=offset,
        )

    async def _related(
        self,
        identifier: str,
        *,
        relation: str,
        embedded_key: str,
        max_results: int,
        offset: int,
    ) -> SemanticScholarSearchResult:
        paper_id = _semantic_scholar_id(identifier)
        payload = await self._get_json(
            f"/paper/{quote(paper_id, safe=':')}/{relation}",
            params={
                "limit": max_results,
                "offset": offset,
                "fields": PAPER_FIELDS,
            },
        )
        data = payload.get("data") or []
        papers: list[PaperCandidate] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            embedded = item.get(embedded_key)
            if not isinstance(embedded, dict):
                continue
            try:
                papers.append(parse_paper(embedded))
            except SemanticScholarParseError as exc:
                raise SemanticScholarClientError(
                    f"Semantic Scholar response parse failed: {exc}"
                ) from exc
        return SemanticScholarSearchResult(
            total=int(payload.get("total") or len(papers)),
            next_offset=payload.get("next"),
            papers=papers,
        )


def _semantic_scholar_id(identifier: str) -> str:
    value = identifier.strip()
    if value.startswith("https://www.semanticscholar.org/paper/"):
        value = value.rstrip("/").rsplit("/", 1)[-1]
    if value.lower().startswith("doi:"):
        return f"DOI:{value[4:]}"
    if value.lower().startswith("arxiv:"):
        return f"ARXIV:{value[6:]}"
    if value.startswith("10."):
        return f"DOI:{value}"
    return value
