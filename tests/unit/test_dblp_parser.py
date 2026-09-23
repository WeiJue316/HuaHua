from __future__ import annotations

from pathlib import Path

from research_agent.mcp_servers.dblp.parser import parse_search_response

FIXTURE = Path(__file__).parents[1] / "fixtures" / "dblp_search.json"


def test_parse_dblp_search_response() -> None:
    result = parse_search_response(FIXTURE.read_text(encoding="utf-8"))

    assert result.total == 1
    assert len(result.papers) == 1
    paper = result.papers[0]
    assert paper.source == "dblp"
    assert paper.source_record_id == "conf/example/paper"
    assert paper.doi == "10.1000/example"
    assert paper.title == "Traceable Retrieval for Scientific Agents"
    assert paper.abstract is None
    assert paper.year == 2024
    assert paper.venue == "Example Conference"
    assert paper.landing_url == "https://dblp.org/rec/conf/example/paper"
    assert [author.name for author in paper.authors] == [
        "Alice Example",
        "Bob Example",
    ]
    assert paper.raw["type"] == "Conference and Workshop Papers"
