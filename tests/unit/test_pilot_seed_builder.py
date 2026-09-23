from __future__ import annotations

from research_agent.evaluator.pilot_seed import (
    PILOT_SEEDS,
    paper_to_annotation,
)
from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate


def test_pilot_seed_has_ten_domain_balanced_questions() -> None:
    assert len(PILOT_SEEDS) == 10
    assert {seed["domain"] for seed in PILOT_SEEDS} == {
        "llm_rag",
        "vision_multimodal",
        "nlp_ir",
        "ml_systems",
        "datasets_repro",
    }


def test_paper_to_annotation_builds_stable_evidence() -> None:
    paper = PaperCandidate(
        source="openalex",
        source_record_id="W123",
        title="A paper",
        abstract="First evidence sentence. Second sentence.",
        doi="10.1000/example",
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=True, status="gold"),
    )

    annotation = paper_to_annotation(paper)

    assert annotation["paper_key"] == "doi:10.1000/example"
    assert annotation["evidence_level"] == "abstract"
    assert annotation["quote"] == "First evidence sentence."
    assert annotation["locator"] == {"section": "Abstract"}
