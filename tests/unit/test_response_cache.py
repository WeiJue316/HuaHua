"""Offline tests for the source response cache."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.cache import ResponseCache, cache_key


def _response(url: str, *, text: str = "{}", status: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status,
        content=text.encode(),
        headers={"content-type": "application/json"},
        request=httpx.Request("GET", url),
    )


def test_empty_cache_is_a_miss(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache")

    assert cache.get(method="GET", url="https://x/a", now=1000.0) is None
    assert cache.stats.misses == 1
    assert cache.stats.hits == 0


def test_stored_response_is_replayed_byte_for_byte(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    url = "https://x/a?q=1"
    body = '{"results": ["one", "two"]}'

    cache.put(method="GET", url=url, response=_response(url, text=body), now=1000.0)
    replayed = cache.get(method="GET", url=url, now=1001.0)

    assert replayed is not None
    assert replayed.status_code == 200
    assert replayed.text == body
    assert str(replayed.request.url) == url
    assert cache.stats.hits == 1


def test_different_query_strings_are_different_entries(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    first = "https://x/a?q=alpha"
    second = "https://x/a?q=beta"

    cache.put(method="GET", url=first, response=_response(first, text="A"), now=1.0)
    cache.put(method="GET", url=second, response=_response(second, text="B"), now=1.0)

    assert cache.get(method="GET", url=first, now=2.0).text == "A"  # type: ignore[union-attr]
    assert cache.get(method="GET", url=second, now=2.0).text == "B"  # type: ignore[union-attr]


def test_expired_entry_is_a_miss(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache", ttl_seconds=60)
    url = "https://x/a"

    cache.put(method="GET", url=url, response=_response(url), now=1000.0)

    assert cache.get(method="GET", url=url, now=1030.0) is not None
    assert cache.get(method="GET", url=url, now=1100.0) is None


def test_failures_are_never_cached(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    url = "https://x/a"

    cache.put(
        method="GET", url=url, response=_response(url, status=429), now=1000.0
    )

    assert cache.get(method="GET", url=url, now=1001.0) is None
    assert cache.entry_count() == 0


def test_corrupt_entry_is_a_miss_not_a_crash(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    url = "https://x/a"
    cache.put(method="GET", url=url, response=_response(url), now=1.0)
    path = cache.root / f"{cache_key('GET', url)}.json"
    path.write_text("{ not json", encoding="utf-8")

    assert cache.get(method="GET", url=url, now=2.0) is None


def test_directory_hash_tracks_content_not_timestamps(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    url = "https://x/a"

    cache.put(method="GET", url=url, response=_response(url, text="A"), now=1.0)
    first = cache.directory_hash()
    cache.put(method="GET", url=url, response=_response(url, text="A"), now=999.0)

    assert cache.directory_hash() == first, "rewriting the same body must not change it"

    other = "https://x/b"
    cache.put(method="GET", url=other, response=_response(other, text="B"), now=1.0)

    assert cache.directory_hash() != first


def test_directory_hash_detects_tampering(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    url = "https://x/a"
    cache.put(method="GET", url=url, response=_response(url, text="A"), now=1.0)
    before = cache.directory_hash()

    path = cache.root / f"{cache_key('GET', url)}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["content_b64"] = "Qg=="  # "B"
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert cache.directory_hash() != before


def test_reset_stats_clears_counters(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache")
    cache.get(method="GET", url="https://x/a", now=1.0)

    cache.reset_stats()

    assert cache.stats.hits == 0
    assert cache.stats.misses == 0


@pytest.mark.asyncio
async def test_compressed_source_response_replays_correctly(tmp_path: Path) -> None:
    """A gzip-encoded response must not be decoded twice on replay.

    httpx returns an already-decoded body while leaving content-encoding in the
    headers. Storing those headers verbatim made every cached reply fail with
    "incorrect header check", which broke both crossref and openalex end to end.
    """

    import gzip

    from research_agent.mcp_servers.common import get_with_retry

    body = b'{"results": [1, 2, 3]}'
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(
            200,
            content=gzip.compress(body),
            headers={
                "content-type": "application/json",
                "content-encoding": "gzip",
            },
            request=request,
        )

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=None)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        first = await get_with_retry(client, "https://x/a", cache=cache)
        second = await get_with_retry(client, "https://x/a", cache=cache)

    assert len(calls) == 1, "the second call must be replayed"
    assert first.json() == {"results": [1, 2, 3]}
    assert second.json() == {"results": [1, 2, 3]}
    assert "content-encoding" not in second.headers
