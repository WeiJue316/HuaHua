"""HTTP client for the OpenAlex works API."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import httpx

from research_agent.mcp_servers.common import PaperCandidate, RetryPolicy, SleepFn, get_with_retry
from research_agent.mcp_servers.openalex.parser import (
    OpenAlexParseError,
    normalize_openalex_id,
    parse_search_response,
    parse_work,
)

OPENALEX_API_URL = "https://api.openalex.org"


class OpenAlexClientError(RuntimeError):
    """Raised when OpenAlex cannot satisfy a request."""

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
class OpenAlexSearchResult:
    """Normalized result metadata for one OpenAlex search."""

    query: str
    total_count: int
    next_cursor: str | None
    papers: list[PaperCandidate]


class OpenAlexClient:
    """Small async client around OpenAlex's public works API."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        api_url: str = OPENALEX_API_URL,
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
        try:
            response = await get_with_retry(
                self.http_client,
                f"{self.api_url}{path}",
                params=params,
                headers={"User-Agent": "research-agent/0.1"},
                retry_policy=self.retry_policy,
                sleep=self.sleep,
            )
        except httpx.HTTPError as exc:
            raise OpenAlexClientError(f"OpenAlex request failed: {exc}") from exc

        if response.status_code >= 400:
            retry_after = response.headers.get("retry-after")
            retry_after_seconds = (
                int(retry_after)
                if retry_after and retry_after.isdigit()
                else None
            )
            raise OpenAlexClientError(
                f"OpenAlex request failed with status {response.status_code}",
                status_code=response.status_code,
                retry_after_seconds=retry_after_seconds,
            )

        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise OpenAlexClientError(f"OpenAlex response is not JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise OpenAlexClientError("OpenAlex response must be a JSON object")
        return payload

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
        cursor: str = "*",
    ) -> OpenAlexSearchResult:
        """Search OpenAlex works."""

        payload = await self._get_json(
            "/works",
            params=self._params(
                {
                    "search": query.strip(),
                    "per-page": max_results,
                    "cursor": cursor,
                }
            ),
        )
        try:
            papers = parse_search_response(json.dumps(payload))
        except OpenAlexParseError as exc:
            raise OpenAlexClientError(f"OpenAlex response parse failed: {exc}") from exc
        meta = payload.get("meta") or {}
        return OpenAlexSearchResult(
            query=query,
            total_count=int(meta.get("count") or 0),
            next_cursor=meta.get("next_cursor"),
            papers=papers,
        )

    async def get_paper(self, identifier: str) -> PaperCandidate:
        """Fetch one OpenAlex work by OpenAlex ID."""

        openalex_id = normalize_openalex_id(identifier)
        payload = await self._get_json(f"/works/{openalex_id}")
        try:
            return parse_work(payload)
        except OpenAlexParseError as exc:
            raise OpenAlexClientError(f"OpenAlex response parse failed: {exc}") from exc

    async def resolve_open_access(self, identifier: str) -> PaperCandidate:
        """Resolve open-access metadata through the work record."""

        return await self.get_paper(identifier)

    async def get_citations(
        self,
        identifier: str,
        *,
        max_results: int = 20,
        cursor: str = "*",
    ) -> OpenAlexSearchResult:
        """Fetch works that cite the given OpenAlex work."""

        openalex_id = normalize_openalex_id(identifier)
        payload = await self._get_json(
            "/works",
            params=self._params(
                {
                    "filter": f"cites:{openalex_id}",
                    "per-page": max_results,
                    "cursor": cursor,
                }
            ),
        )
        try:
            papers = parse_search_response(json.dumps(payload))
        except OpenAlexParseError as exc:
            raise OpenAlexClientError(f"OpenAlex response parse failed: {exc}") from exc
        meta = payload.get("meta") or {}
        return OpenAlexSearchResult(
            query=f"cites:{openalex_id}",
            total_count=int(meta.get("count") or 0),
            next_cursor=meta.get("next_cursor"),
            papers=papers,
        )

    async def get_references(
        self,
        identifier: str,
        *,
        max_results: int = 20,
    ) -> OpenAlexSearchResult:
        """Fetch works referenced by the given OpenAlex work."""

        openalex_id = normalize_openalex_id(identifier)
        work = await self._get_json(f"/works/{openalex_id}")
        reference_ids = [
            normalize_openalex_id(value)
            for value in work.get("referenced_works") or []
            if isinstance(value, str)
        ][:max_results]
        if not reference_ids:
            return OpenAlexSearchResult(
                query=f"references:{openalex_id}",
                total_count=0,
                next_cursor=None,
                papers=[],
            )
        payload = await self._get_json(
            "/works",
            params=self._params(
                {
                    "filter": f"openalex_id:{'|'.join(reference_ids)}",
                    "per-page": len(reference_ids),
                }
            ),
        )
        try:
            papers = parse_search_response(json.dumps(payload))
        except OpenAlexParseError as exc:
            raise OpenAlexClientError(f"OpenAlex response parse failed: {exc}") from exc
        return OpenAlexSearchResult(
            query=f"references:{openalex_id}",
            total_count=len(reference_ids),
            next_cursor=None,
            papers=papers,
        )
