from __future__ import annotations

from research_agent.identity import (
    identity_aliases,
    labels_match,
    matched_gold_keys,
    primary_identity,
)
from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate


def _paper(**overrides: object) -> PaperCandidate:
    values: dict[str, object] = {
        "source": "openalex",
        "source_record_id": "W123",
        "title": "Evidence chains",
        "landing_url": "https://openalex.org/W123",
        "open_access": OpenAccessInfo(is_oa=True, status="gold"),
    }
    values.update(overrides)
    return PaperCandidate(**values)  # type: ignore[arg-type]


def test_arxiv_doi_arxiv_id_and_arxiv_url_are_one_paper() -> None:
    gold = "doi:10.48550/arXiv.2312.10997"
    retrieved = "arxiv:2312.10997v2"
    url = "https://arxiv.org/pdf/2312.10997v2.pdf"

    assert labels_match(gold, retrieved)
    assert labels_match(retrieved, url)
    assert matched_gold_keys({retrieved}, {gold}) == {gold}


def test_doi_url_and_bare_doi_match_ignoring_case() -> None:
    assert labels_match("https://dx.doi.org/10.1000/AbC", "doi:10.1000/abc")


def test_openalex_url_matches_openalex_id() -> None:
    assert labels_match("https://openalex.org/W123", "openalex:w123")


def test_one_candidate_exposes_doi_arxiv_and_openalex_together() -> None:
    paper = _paper(
        source="openalex",
        source_record_id="W999",
        doi="10.48550/arxiv.2401.00001",
    )

    aliases = identity_aliases(paper)

    assert aliases == frozenset({"arxiv:2401.00001", "openalex:W999"})
    assert primary_identity(paper) == "arxiv:2401.00001"
    assert matched_gold_keys(
        {"arxiv:2401.00001"},
        {"openalex:W999", "doi:10.48550/arxiv.2401.00001"},
        extra_aliases=set(aliases),
    ) == {"openalex:W999", "doi:10.48550/arxiv.2401.00001"}


def test_journal_doi_is_the_primary_key_even_on_an_arxiv_record() -> None:
    paper = _paper(
        source="arxiv",
        source_record_id="2501.00001",
        doi="10.1000/Example",
        landing_url="https://arxiv.org/abs/2501.00001",
    )

    assert primary_identity(paper) == "doi:10.1000/example"
    assert "arxiv:2501.00001" in identity_aliases(paper)


def test_unrelated_papers_do_not_match() -> None:
    assert matched_gold_keys({"doi:10.1000/one"}, {"doi:10.1000/two"}) == set()
