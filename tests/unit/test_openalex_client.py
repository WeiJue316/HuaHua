from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.common import RetryPolicy
from research_agent.mcp_servers.openalex.client import (
    OpenAlexClient,
    OpenAlexClientError,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "openalex_search.json"


@pytest.mark.asyncio
async def test_openalex_client_searches_works() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/works"
        assert request.url.params["search"] == "evidence chain"
        assert request.url.params["per-page"] == "5"
        assert request.url.params["cursor"] == "*"
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            headers={"content-type": "application/json"},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = OpenAlexClient(http_client=http_client)
        result = await client.search("evidence chain", max_results=5)

    assert result.query == "evidence chain"
    assert result.total_count == 1
    assert result.next_cursor is None
    assert len(result.papers) == 1
    assert result.papers[0].source_record_id == "W123456789"


@pytest.mark.asyncio
async def test_openalex_client_gets_paper_by_id() -> None:
    payload = FIXTURE.read_text(encoding="utf-8")
    work = __import__("json").loads(payload)["results"][0]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/works/W123456789"
        return httpx.Response(
            200,
            json=work,
            headers={"content-type": "application/json"},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = OpenAlexClient(http_client=http_client)
        paper = await client.get_paper("https://openalex.org/W123456789")

    assert paper.source_record_id == "W123456789"
    assert paper.doi == "10.1000/example"


@pytest.mark.asyncio
async def test_openalex_client_maps_rate_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            text="slow down",
            headers={"retry-after": "10"},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = OpenAlexClient(
            http_client=http_client,
            retry_policy=RetryPolicy(max_attempts=1),
        )
        with pytest.raises(OpenAlexClientError, match="429") as exc_info:
            await client.search("evidence chain")

    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after_seconds == 10

@pytest.mark.asyncio
async def test_openalex_client_gets_citations() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/works"
        assert request.url.params["filter"] == "cites:W123456789"
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = OpenAlexClient(http_client=http_client)
        result = await client.get_citations("https://openalex.org/W123456789")

    assert result.query == "cites:W123456789"
    assert result.total_count == 1
    assert result.papers[0].source_record_id == "W123456789"


@pytest.mark.asyncio
async def test_openalex_client_gets_references() -> None:
    work = __import__("json").loads(FIXTURE.read_text(encoding="utf-8"))["results"][0]
    work["referenced_works"] = ["https://openalex.org/W222222222"]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/works/W123456789":
            return httpx.Response(200, json=work, request=request)
        assert request.url.path == "/works"
        assert request.url.params["filter"] == "openalex_id:W222222222"
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = OpenAlexClient(http_client=http_client)
        result = await client.get_references("W123456789")

    assert result.query == "references:W123456789"
    assert result.total_count == 1
    assert result.papers[0].source_record_id == "W123456789"

@pytest.mark.asyncio
async def test_openalex_client_retries_rate_limit_then_succeeds() -> None:
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
        client = OpenAlexClient(http_client=http_client, sleep=fake_sleep)
        result = await client.search("evidence chain", max_results=5)

    assert calls == 2
    assert delays == [1.0]
    assert result.papers[0].source_record_id == "W123456789"
