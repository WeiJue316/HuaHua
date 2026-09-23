from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.arxiv.client import ArxivClient, ArxivClientError
from research_agent.mcp_servers.common import RetryPolicy

FIXTURE = Path(__file__).parents[1] / "fixtures" / "arxiv_search.xml"


@pytest.mark.asyncio
async def test_arxiv_client_search_parses_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["search_query"] == 'all:"evidence chain"'
        assert request.url.params["max_results"] == "5"
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            headers={"content-type": "application/atom+xml"},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        arxiv = ArxivClient(http_client=http_client)
        response = await arxiv.search("evidence chain", max_results=5)

    assert response.query == "evidence chain"
    assert response.request_url.startswith("https://export.arxiv.org/api/query")
    assert response.response_hash
    assert len(response.papers) == 2
    assert response.papers[0].source_record_id == "2407.18940"


@pytest.mark.asyncio
async def test_arxiv_client_maps_upstream_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="busy", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        arxiv = ArxivClient(
            http_client=http_client,
            retry_policy=RetryPolicy(max_attempts=1),
        )
        with pytest.raises(ArxivClientError, match="503") as exc_info:
            await arxiv.search("evidence chain")

    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_arxiv_client_downloads_pdf_with_hash(tmp_path: Path) -> None:
    pdf_bytes = b"%PDF-1.4\nfixture\n"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=pdf_bytes,
            headers={"content-type": "application/pdf"},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        arxiv = ArxivClient(http_client=http_client)
        artifact = await arxiv.download_pdf(
            "https://arxiv.org/pdf/2407.18940v2",
            tmp_path,
            artifact_id="2407.18940",
        )

    assert artifact.filename == f"{artifact.sha256}.pdf"
    assert artifact.size_bytes == len(pdf_bytes)
    assert artifact.content_type == "application/pdf"
    assert artifact.artifact_uri == "artifact://arxiv/2407.18940"
    assert (tmp_path / artifact.filename).read_bytes() == pdf_bytes

@pytest.mark.asyncio
async def test_arxiv_client_maps_rate_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="slow down", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        arxiv = ArxivClient(http_client=http_client)
        with pytest.raises(ArxivClientError, match="429") as exc_info:
            await arxiv.search("evidence chain")

    assert exc_info.value.status_code == 429

@pytest.mark.asyncio
async def test_arxiv_client_retries_rate_limit_then_succeeds() -> None:
    calls = 0
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                429,
                headers={"retry-after": "1"},
                request=request,
            )
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        arxiv = ArxivClient(http_client=http_client, sleep=fake_sleep)
        result = await arxiv.search("evidence chain", max_results=5)

    assert calls == 2
    assert delays == [1.0]
    assert result.papers[0].source_record_id == "2407.18940"
