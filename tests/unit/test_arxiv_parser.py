from __future__ import annotations

from pathlib import Path

import pytest

from research_agent.mcp_servers.arxiv.parser import (
    ArxivParseError,
    normalize_arxiv_id,
    parse_search_response,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "arxiv_search.xml"


def test_parse_search_response_extracts_entries() -> None:
    papers = parse_search_response(FIXTURE.read_text(encoding="utf-8"))

    assert len(papers) == 2
    first = papers[0]
    assert first.source_record_id == "2407.18940"
    assert first.source_version == "v2"
    assert first.title == "Traceable Retrieval for Scientific Agents"
    assert first.abstract == "We study evidence chains for scientific literature agents."
    assert first.year == 2024
    assert [author.name for author in first.authors] == ["Alice Example", "Bob Example"]
    assert first.doi == "10.1000/example"
    assert first.categories == ["cs.AI", "cs.IR"]
    assert first.landing_url == "http://arxiv.org/abs/2407.18940v2"
    assert first.pdf_url == "http://arxiv.org/pdf/2407.18940v2"
    assert first.open_access.is_oa is True
    assert first.raw["source_record_id"] == "2407.18940"

    second = papers[1]
    assert second.source_record_id == "2501.00001"
    assert second.pdf_url == "https://arxiv.org/pdf/2501.00001"
    assert second.doi is None


def test_parse_search_response_handles_empty_feed() -> None:
    assert parse_search_response("<feed xmlns='http://www.w3.org/2005/Atom' />") == []


def test_parse_search_response_rejects_invalid_xml() -> None:
    with pytest.raises(ArxivParseError):
        parse_search_response("<feed>")


def test_normalize_arxiv_id_handles_urls_and_versions() -> None:
    assert normalize_arxiv_id("http://arxiv.org/abs/2407.18940v2") == "2407.18940"
    assert normalize_arxiv_id("https://arxiv.org/pdf/2501.00001v1") == "2501.00001"
    assert normalize_arxiv_id(" 2407.18940 ") == "2407.18940"