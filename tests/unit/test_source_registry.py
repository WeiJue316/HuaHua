from __future__ import annotations

import httpx
import pytest

from research_agent.router.registry import (
    UnsupportedSourceError,
    build_source_clients,
)


@pytest.mark.asyncio
async def test_build_source_clients_supports_five_sources() -> None:
    async with httpx.AsyncClient() as http_client:
        clients = build_source_clients(
            http_client,
            [
                "arxiv",
                "openalex",
                "crossref",
                "semantic_scholar",
                "dblp",
            ],
        )

    assert set(clients) == {
        "arxiv",
        "openalex",
        "crossref",
        "semantic_scholar",
        "dblp",
    }


@pytest.mark.asyncio
async def test_build_source_clients_rejects_unknown_source() -> None:
    async with httpx.AsyncClient() as http_client:
        with pytest.raises(UnsupportedSourceError, match="unknown"):
            build_source_clients(http_client, ["unknown"])