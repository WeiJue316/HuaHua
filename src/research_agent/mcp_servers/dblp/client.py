"""HTTP client for the DBLP publication API."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import httpx

from research_agent.mcp_servers.common import (
    PaperCandidate,
    RetryPolicy,
    SleepFn,
    get_with_retry,
)
from research_agent.mcp_servers.dblp.parser import DblpParseError, parse_search_response

DBLP_API_URL = "https://dblp.org"


class DblpClientError(RuntimeError):
    """Raised when DBLP cannot satisfy a request."""

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
class DblpSearchResult:
    """Normalized DBLP publication search result."""

    total: int
    papers: list[PaperCandidate]


class DblpClient:
    """Small async client around the public DBLP API."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        api_url: str = DBLP_API_URL,
        retry_policy: RetryPolicy | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self.http_client = http_client
        self.api_url = api_url.rstrip("/")
        self.retry_policy = retry_policy or RetryPolicy()
        self.sleep = sleep

    async def _get_json(
        self,
        params: dict[str, str | int],
    ) -> dict[str, Any]:
        response = await get_with_retry(
            self.http_client,
            f"{self.api_url}/search/publ/api",
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
            raise DblpClientError(
                f"DBLP request failed with status {response.status_code}",
                status_code=response.status_code,
                retry_after_seconds=retry_after_seconds,
            )
        response_text = response.text.lstrip()
        normalized_text = response_text.lower()
        if normalized_text.startswith("<!doctype") or normalized_text.startswith("<html"):
            raise DblpClientError(
                "DBLP returned a bot challenge page; source is temporarily blocked"
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise DblpClientError(f"DBLP response is not JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise DblpClientError("DBLP response must be a JSON object")
        return payload

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
        offset: int = 0,
    ) -> DblpSearchResult:
        """Search DBLP publications."""

        payload = await self._get_json(
            {
                "q": query.strip(),
                "format": "json",
                "h": max_results,
                "f": offset,
            }
        )
        try:
            page = parse_search_response(json.dumps(payload))
        except DblpParseError as exc:
            raise DblpClientError(f"DBLP response parse failed: {exc}") from exc
        return DblpSearchResult(total=page.total, papers=page.papers)

    async def get_paper(self, key: str) -> PaperCandidate:
        """Fetch one DBLP record by its stable key."""

        payload = await self._get_json(
            {
                "q": f"key:{key.strip()}",
                "format": "json",
                "h": 5,
                "f": 0,
            }
        )
        try:
            page = parse_search_response(json.dumps(payload))
        except DblpParseError as exc:
            raise DblpClientError(f"DBLP response parse failed: {exc}") from exc
        for paper in page.papers:
            if paper.source_record_id == key.strip():
                return paper
        raise DblpClientError(f"DBLP record not found: {key}")
