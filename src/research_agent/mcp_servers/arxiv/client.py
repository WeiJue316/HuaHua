"""HTTP client for the arXiv Atom API."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

import httpx

from research_agent.mcp_servers.arxiv.parser import (
    normalize_arxiv_id,
    parse_search_response,
)
from research_agent.mcp_servers.cache import ResponseCache
from research_agent.mcp_servers.common import (
    DEFAULT_RATE_LIMITER,
    PaperCandidate,
    RetryPolicy,
    SleepFn,
    _http_attempts,
    get_with_retry,
    parse_retry_after,
    user_agent,
)

ARXIV_API_URL = "https://export.arxiv.org/api/query"
MAX_PDF_BYTES = 32 * 1024 * 1024
PDF_MAGIC = b"%PDF-"


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
    status: str = "stored"


def _build_search_query(query: str) -> str:
    normalized = query.strip()
    if not normalized:
        raise ArxivClientError("arXiv query must not be empty")
    if len(normalized.split()) == 1:
        return f"all:{normalized}"
    return f'all:"{normalized}"'


class ArxivClient:
    """Small async client around the public arXiv API."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        api_url: str = ARXIV_API_URL,
        cache: ResponseCache | None = None,
        retry_policy: RetryPolicy | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self.http_client = http_client
        self.api_url = api_url
        self.cache = cache
        self.retry_policy = retry_policy or RetryPolicy()
        self.sleep = sleep

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
    ) -> ArxivSearchResult:
        """Search arXiv and parse the Atom response."""

        query_value = quote(_build_search_query(query), safe=":")
        search_url = (
            f"{self.api_url}?search_query={query_value}"
            f"&start=0&max_results={max_results}"
            "&sortBy=relevance&sortOrder=descending"
        )
        try:
            response = await get_with_retry(
                self.http_client,
                search_url,
                headers={"User-Agent": user_agent()},
                retry_policy=self.retry_policy,
                cache=self.cache,
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
                headers={"User-Agent": user_agent()},
                retry_policy=self.retry_policy,
                cache=self.cache,
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
        max_bytes: int = MAX_PDF_BYTES,
    ) -> ArtifactRef:
        """Download a PDF, stopping once it exceeds the size limit.

        A body that is too large is not written. A body that does not start
        with the PDF magic is written and marked quarantined so it cannot be
        used as evidence.
        """

        content, size_bytes, final_url = await self._read_bounded(url, max_bytes)
        retrieved_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        if content is None:
            digest = hashlib.sha256(
                f"oversized\n{size_bytes}\n{url}".encode()
            ).hexdigest()
            return ArtifactRef(
                artifact_id=artifact_id,
                artifact_uri=f"artifact://arxiv/{artifact_id}",
                filename=f"{digest}.pdf",
                content_type="application/pdf",
                size_bytes=size_bytes,
                sha256=digest,
                source_url=url,
                final_url=final_url,
                retrieved_at=retrieved_at,
                status="quarantined",
            )

        digest = hashlib.sha256(content).hexdigest()
        destination_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{digest}.pdf"
        (destination_dir / filename).write_bytes(content)
        status = "stored" if content.startswith(PDF_MAGIC) else "quarantined"
        return ArtifactRef(
            artifact_id=artifact_id,
            artifact_uri=f"artifact://arxiv/{artifact_id}",
            filename=filename,
            content_type="application/pdf",
            size_bytes=len(content),
            sha256=digest,
            source_url=url,
            final_url=final_url,
            retrieved_at=retrieved_at,
            status=status,
        )

    async def _read_bounded(
        self, url: str, max_bytes: int
    ) -> tuple[bytes | None, int, str]:
        policy = self.retry_policy
        last_error: httpx.HTTPError | None = None
        for attempt in range(1, policy.max_attempts + 1):
            try:
                await DEFAULT_RATE_LIMITER.wait(url)
                active = _http_attempts.get()
                if active is not None:
                    active.calls += 1
                async with self.http_client.stream(
                    "GET",
                    url,
                    headers={"User-Agent": user_agent()},
                ) as response:
                    if (
                        response.status_code in policy.retry_status_codes
                        and attempt < policy.max_attempts
                    ):
                        await response.aread()
                        retry_after = response.headers.get("retry-after")
                        delay = parse_retry_after(retry_after)
                        await self.sleep(
                            policy.delay_for_attempt(attempt, delay)
                        )
                        continue
                    if response.status_code >= 400:
                        raise ArxivClientError(
                            "arXiv PDF request failed with status "
                            f"{response.status_code}",
                            status_code=response.status_code,
                        )
                    declared = response.headers.get("content-length")
                    if (
                        declared is not None
                        and declared.isdigit()
                        and int(declared) > max_bytes
                    ):
                        return None, int(declared), str(response.url)
                    chunks: list[bytes] = []
                    total = 0
                    async for chunk in response.aiter_bytes():
                        if total + len(chunk) > max_bytes:
                            return None, total + len(chunk), str(response.url)
                        chunks.append(chunk)
                        total += len(chunk)
                    return b"".join(chunks), total, str(response.url)
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt >= policy.max_attempts:
                    raise ArxivClientError(
                        f"arXiv PDF request failed: {exc}"
                    ) from exc
                await self.sleep(policy.delay_for_attempt(attempt))
        if last_error is not None:
            raise ArxivClientError(
                f"arXiv PDF request failed: {last_error}"
            ) from last_error
        raise ArxivClientError("arXiv PDF request failed without a response")
