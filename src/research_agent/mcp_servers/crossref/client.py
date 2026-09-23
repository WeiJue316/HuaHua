"""HTTP client for the Crossref works API."""

from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from research_agent.mcp_servers.common import (
    OpenAccessInfo,
    PaperCandidate,
    RetryPolicy,
    SleepFn,
    get_with_retry,
)
from research_agent.mcp_servers.crossref.parser import (
    CrossrefParseError,
    normalize_crossref_doi,
    parse_search_response,
    parse_work,
)

CROSSREF_API_URL = "https://api.crossref.org"


class CrossrefClientError(RuntimeError):
    """Raised when Crossref cannot satisfy a request."""

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
class CrossrefSearchResult:
    """Normalized Crossref search result."""

    query: str
    next_cursor: str | None
    papers: list[PaperCandidate]


class CrossrefClient:
    """Small async client around Crossref's public works API."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        api_url: str = CROSSREF_API_URL,
        mailto: str | None = None,
        retry_policy: RetryPolicy | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self.http_client = http_client
        self.api_url = api_url.rstrip("/")
        self.mailto = mailto
        self.retry_policy = retry_policy or RetryPolicy()
        self.sleep = sleep

    def _params(self, values: dict[str, str | int | None]) -> dict[str, str | int]:
        params: dict[str, str | int] = {}
        for key, value in values.items():
            if value is not None:
                params[key] = value
        if self.mailto:
            params["mailto"] = self.mailto
        return params

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
            headers={"User-Agent": "research-agent/0.1"},
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
            raise CrossrefClientError(
                f"Crossref request failed with status {response.status_code}",
                status_code=response.status_code,
                retry_after_seconds=retry_after_seconds,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise CrossrefClientError(f"Crossref response is not JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise CrossrefClientError("Crossref response must be a JSON object")
        return payload

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
        cursor: str = "*",
    ) -> CrossrefSearchResult:
        """Search Crossref works."""

        payload = await self._get_json(
            "/works",
            params=self._params(
                {
                    "query": query.strip(),
                    "rows": max_results,
                    "cursor": cursor,
                }
            ),
        )
        try:
            page = parse_search_response(json.dumps(payload))
        except CrossrefParseError as exc:
            raise CrossrefClientError(f"Crossref response parse failed: {exc}") from exc
        return CrossrefSearchResult(
            query=query,
            next_cursor=page.next_cursor,
            papers=page.papers,
        )

    async def get_paper(self, identifier: str) -> PaperCandidate:
        """Fetch one Crossref work by DOI."""

        doi = normalize_crossref_doi(identifier)
        payload = await self._get_json(f"/works/{quote(doi, safe='')}")
        message = payload.get("message")
        if not isinstance(message, dict):
            raise CrossrefClientError("Crossref response is missing message")
        try:
            return parse_work(message)
        except CrossrefParseError as exc:
            raise CrossrefClientError(f"Crossref response parse failed: {exc}") from exc

    async def resolve_open_access(self, identifier: str) -> PaperCandidate:
        """Resolve candidate open-access link from Crossref metadata."""

        return await self.get_paper(identifier)

    async def get_references(
        self,
        identifier: str,
        *,
        max_results: int = 20,
    ) -> list[PaperCandidate]:
        """Return partial candidates from a Crossref reference list."""

        doi = normalize_crossref_doi(identifier)
        payload = await self._get_json(f"/works/{quote(doi, safe='')}")
        message = payload.get("message")
        if not isinstance(message, dict):
            raise CrossrefClientError("Crossref response is missing message")
        references = message.get("reference") or []
        return [
            _reference_candidate(reference)
            for reference in references[:max_results]
            if isinstance(reference, dict)
        ]


def _reference_candidate(reference: dict[str, Any]) -> PaperCandidate:
    raw_doi = reference.get("DOI")
    reference_doi = normalize_crossref_doi(raw_doi) if isinstance(raw_doi, str) else None
    raw_json = json.dumps(reference, ensure_ascii=False, sort_keys=True)
    record_id = reference_doi or hashlib.sha256(raw_json.encode()).hexdigest()
    title = (
        reference.get("article-title")
        or reference.get("unstructured")
        or reference.get("journal-title")
        or f"Reference {record_id}"
    )
    return PaperCandidate(
        source="crossref",
        source_record_id=record_id,
        title=str(title),
        year=int(reference["year"]) if str(reference.get("year", "")).isdigit() else None,
        venue=reference.get("journal-title"),
        doi=reference_doi,
        landing_url=f"https://doi.org/{reference_doi}" if reference_doi else "",
        open_access=OpenAccessInfo(is_oa=False, status="unknown"),
        raw=reference,
    )
