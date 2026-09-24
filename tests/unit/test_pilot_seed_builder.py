from __future__ import annotations

import pytest

from research_agent.evaluator.pilot_seed import (
    PILOT_SEEDS,
    build_seed_questions,
    is_author_list,
    paper_to_annotation,
    usable_evidence_sentence,
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
        abstract=(
            "We study evidence chains for scientific literature agents and "
            "report reproducible results. A second sentence follows."
        ),
        doi="10.1000/example",
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=True, status="gold"),
    )

    annotation = paper_to_annotation(paper, supports_subquestion=2)

    assert annotation is not None
    assert annotation["paper_key"] == "doi:10.1000/example"
    assert annotation["evidence_level"] == "abstract"
    assert annotation["quote"] == (
        "We study evidence chains for scientific literature agents and "
        "report reproducible results."
    )
    assert annotation["locator"] == {"section": "Abstract"}
    assert annotation["supports_subquestion"] == 2


def _paper(
    *,
    record_id: str = "W123",
    doi: str | None = "10.1000/example",
    title: str = "A paper about evidence chains",
    abstract: str | None = None,
) -> PaperCandidate:
    return PaperCandidate(
        source="openalex",
        source_record_id=record_id,
        title=title,
        abstract=abstract,
        doi=doi,
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=True, status="gold"),
    )


def test_is_author_list_flags_name_lists() -> None:
    assert is_author_list(
        "Shahul Es, Jithin James, Luis Espinosa Anke, Steven Schockaert."
    )
    assert not is_author_list(
        "We study evidence chains for scientific literature agents and report results."
    )


def test_usable_evidence_sentence_rejects_author_lists() -> None:
    abstract = "Shahul Es, Jithin James, Luis Espinosa Anke, Steven Schockaert."

    assert usable_evidence_sentence(abstract) is None


def test_usable_evidence_sentence_rejects_short_fragments() -> None:
    assert usable_evidence_sentence("Brains are prediction machines.") is None


def test_usable_evidence_sentence_strips_openalex_abstract_prefix() -> None:
    abstract = "Abstract There is a failure mode in large language models that we study."

    sentence = usable_evidence_sentence(abstract)

    assert sentence == "There is a failure mode in large language models that we study."


def test_usable_evidence_sentence_repairs_missing_sentence_spaces() -> None:
    abstract = (
        "Large language models face challenges with outdated knowledge."
        "Retrievalaugmented generation is a promising solution for those models."
    )

    sentence = usable_evidence_sentence(abstract)

    # Without the whitespace repair the two sentences collapse into one
    # oversized run-on and the whole abstract would be quoted as evidence.
    assert sentence == (
        "Large language models face challenges with outdated knowledge."
    )


def test_usable_evidence_sentence_rejects_oversized_run_on_text() -> None:
    abstract = "We study retrieval augmented generation systems " + "and more " * 80

    assert usable_evidence_sentence(abstract) is None


def test_usable_evidence_sentence_prefers_the_sentence_answering_a_subquestion() -> None:
    abstract = (
        "Retrieval augmented generation has become a popular research topic. "
        "We evaluate our systems on Natural Questions and TriviaQA using EM and F1. "
        "The results show consistent improvements over strong baselines."
    )

    sentence = usable_evidence_sentence(
        abstract, prefer_terms={"datasets", "metrics", "triviaqa"}
    )

    assert sentence == (
        "We evaluate our systems on Natural Questions and TriviaQA using EM and F1."
    )


def test_usable_evidence_sentence_falls_back_to_the_first_sentence() -> None:
    abstract = (
        "Retrieval augmented generation has become a popular research topic. "
        "We evaluate our systems on Natural Questions and TriviaQA using EM and F1."
    )

    assert usable_evidence_sentence(abstract) == (
        "Retrieval augmented generation has become a popular research topic."
    )


def test_paper_to_annotation_records_the_paper_year() -> None:
    paper = _paper(
        title="Evaluation methods for retrieval augmented generation",
        abstract=(
            "We survey evaluation methods for retrieval augmented generation "
            "systems and compare reported metrics across benchmarks."
        ),
    )
    paper = paper.model_copy(update={"year": 2024})

    annotation = paper_to_annotation(paper, supports_subquestion=1)

    assert annotation is not None
    assert annotation["paper_year"] == 2024


@pytest.mark.asyncio
async def test_build_seed_questions_drops_papers_outside_the_year_range() -> None:
    inside = _paper(
        record_id="W1",
        doi="10.1/inside",
        title="Evaluation methods for retrieval augmented generation systems",
        abstract=(
            "We survey evaluation methods for retrieval augmented generation "
            "systems and compare reported metrics across benchmarks."
        ),
    ).model_copy(update={"year": 2024})
    outside = _paper(
        record_id="W2",
        doi="10.1/outside",
        title="Evaluation methods for retrieval augmented generation systems",
        abstract=(
            "We survey evaluation methods for retrieval augmented generation "
            "systems and compare reported metrics across benchmarks."
        ),
    ).model_copy(update={"year": 2003})
    client = FakeOpenAlexClient([outside, inside])

    records = await build_seed_questions(
        client,  # type: ignore[arg-type]
        seeds=[PILOT_SEEDS[0]],
    )

    assert records[0]["gold_papers"] == ["doi:10.1/inside"]


def test_paper_to_annotation_rejects_a_container_title_as_quote() -> None:
    venue = (
        "Proceedings of the 61st Annual Meeting of the Association for "
        "Computational Linguistics (Volume 1: Long Papers)"
    )
    paper = _paper(
        title="A reasoning paper",
        abstract=venue + ".",
    ).model_copy(update={"venue": venue})

    assert paper_to_annotation(paper, supports_subquestion=1) is None


def test_paper_to_annotation_rejects_a_title_echoed_as_quote() -> None:
    title = (
        "Retrieval augmented generation for scientific literature agents "
        "with traceable evidence chains"
    )
    paper = _paper(title=title, abstract=title + ".")

    assert paper_to_annotation(paper, supports_subquestion=1) is None


@pytest.mark.asyncio
async def test_build_seed_questions_can_assign_a_dataset_subquestion() -> None:
    metrics_paper = _paper(
        record_id="W1",
        doi="10.1/metrics",
        title="Evaluation metrics for retrieval augmented generation",
        abstract=(
            "We report faithfulness and answer relevance metrics for retrieval "
            "augmented generation systems across several benchmarks."
        ),
    )
    dataset_paper = _paper(
        record_id="W2",
        doi="10.1/datasets",
        title="Benchmark datasets for retrieval augmented generation",
        abstract=(
            "We compare benchmark datasets and baseline systems used for "
            "retrieval augmented generation evaluation in our study."
        ),
    )
    client = FakeOpenAlexClient([metrics_paper, dataset_paper])

    records = await build_seed_questions(
        client,  # type: ignore[arg-type]
        seeds=[PILOT_SEEDS[0]],
    )

    assigned = {
        item["paper_key"]: item["supports_subquestion"]
        for item in records[0]["gold_evidence"]
    }
    assert assigned.get("doi:10.1/datasets") == 2


def test_content_terms_treat_hyphens_as_word_boundaries() -> None:
    from research_agent.evaluator.pilot_seed import _content_terms

    assert _content_terms("retrieval-augmented generation") == {
        "retrieval",
        "augmented",
        "generation",
    }


def test_usable_evidence_sentence_rejects_container_titles() -> None:
    for container in (
        "Proceedings of the 61st Annual Meeting of the Association for "
        "Computational Linguistics (Volume 1: Long Papers).",
        "Findings of the Association for Computational Linguistics: EMNLP 2024.",
        "IEEE Transactions on Pattern Analysis and Machine Intelligence.",
        "Advances in Neural Information Processing Systems 36.",
        "Journal of Machine Learning Research.",
    ):
        assert usable_evidence_sentence("Authors, And More Authors. " + container) is None


def test_content_terms_fold_simple_plurals() -> None:
    from research_agent.evaluator.pilot_seed import _content_terms, _tokenize

    # "dataset" is a generic term and is dropped, but the fold must still happen
    # before filtering so that plural and singular forms compare equal.
    assert _content_terms("datasets and baselines") == {"baseline"}
    assert _tokenize("datasets baselines metrics") == [
        "dataset",
        "baseline",
        "metric",
    ]
    assert _tokenize("analysis class") == ["analysis", "class"]


def test_paper_to_annotation_returns_none_without_usable_evidence() -> None:
    paper = _paper(abstract="Shahul Es, Jithin James, Luis Espinosa Anke.")

    assert paper_to_annotation(paper, supports_subquestion=1) is None


class FakeOpenAlexClient:
    """Returns a fixed paper list regardless of the query variant."""

    def __init__(self, papers: list[PaperCandidate]) -> None:
        self._papers = papers
        self.queries: list[str] = []

    async def search(self, query: str, *, max_results: int = 20) -> object:
        del max_results
        self.queries.append(query)
        return type("Result", (), {"papers": list(self._papers)})()


@pytest.mark.asyncio
async def test_build_seed_questions_keeps_gold_papers_and_evidence_in_sync() -> None:
    good = _paper(
        record_id="W1",
        doi="10.1/good",
        title="Evaluation methods for retrieval augmented generation systems",
        abstract=(
            "We survey evaluation methods for retrieval augmented generation "
            "systems and compare reported metrics across benchmarks."
        ),
    )
    unusable = _paper(
        record_id="W2",
        doi="10.1/unusable",
        title="Unrelated records",
        abstract="Shahul Es, Jithin James, Luis Espinosa Anke, Steven Schockaert.",
    )
    client = FakeOpenAlexClient([good, unusable])

    records = await build_seed_questions(
        client,  # type: ignore[arg-type]
        seeds=[PILOT_SEEDS[0]],
    )

    record = records[0]
    assert record["gold_papers"] == ["doi:10.1/good"]
    assert {item["paper_key"] for item in record["gold_evidence"]} == {"doi:10.1/good"}


@pytest.mark.asyncio
async def test_build_seed_questions_deduplicates_repeated_papers() -> None:
    good = _paper(
        record_id="W1",
        doi="10.1/good",
        title="Evaluation methods for retrieval augmented generation systems",
        abstract=(
            "We survey evaluation methods for retrieval augmented generation "
            "systems and compare reported metrics across benchmarks."
        ),
    )
    client = FakeOpenAlexClient([good, good])

    records = await build_seed_questions(
        client,  # type: ignore[arg-type]
        seeds=[PILOT_SEEDS[0]],
    )

    assert records[0]["gold_papers"] == ["doi:10.1/good"]


@pytest.mark.asyncio
async def test_build_seed_questions_runs_query_variants() -> None:
    client = FakeOpenAlexClient([])

    await build_seed_questions(client, seeds=[PILOT_SEEDS[0]])  # type: ignore[arg-type]

    assert len(client.queries) > 1


@pytest.mark.asyncio
async def test_build_seed_questions_assigns_subquestions() -> None:
    paper = _paper(
        record_id="W9",
        doi="10.1/metrics",
        title="Metrics used for retrieval augmented generation evaluation",
        abstract=(
            "We report which metrics are used to evaluate retrieval augmented "
            "generation systems across several benchmarks."
        ),
    )
    client = FakeOpenAlexClient([paper])

    records = await build_seed_questions(
        client,  # type: ignore[arg-type]
        seeds=[PILOT_SEEDS[0]],
    )

    assigned = {item["supports_subquestion"] for item in records[0]["gold_evidence"]}
    assert assigned == {1}



def test_paper_to_annotation_keeps_a_verbatim_audit_quote() -> None:
    paper = _paper(
        abstract=(
            "Retrieval augmented generation has become a common research topic. "
            "We evaluate our systems on Natural Questions using exact match. "
            "The results show consistent improvements."
        )
    )

    annotation = paper_to_annotation(
        paper,
        supports_subquestion=1,
        evidence_quote=(
            "We evaluate our systems on Natural Questions using exact match."
        ),
    )

    assert annotation is not None
    assert annotation["quote"] == (
        "We evaluate our systems on Natural Questions using exact match."
    )


def test_paper_to_annotation_rejects_a_non_verbatim_audit_quote() -> None:
    paper = _paper(
        abstract=(
            "We evaluate our systems on Natural Questions using exact match. "
            "The results show consistent improvements."
        )
    )

    annotation = paper_to_annotation(
        paper,
        supports_subquestion=1,
        evidence_quote="The paper uses exact match.",
    )

    assert annotation is None
