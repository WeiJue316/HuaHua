"""Build a seed Pilot question set from OpenAlex metadata."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx

from research_agent.mcp_servers.common import PaperCandidate
from research_agent.mcp_servers.openalex.client import OpenAlexClient
from research_agent.planner.planner import STOPWORDS, plan_research
from research_agent.router.registry import build_openalex_client

PILOT_SEEDS: tuple[dict[str, Any], ...] = (
    {
        "question_id": "csai_001",
        "question": (
            "What are the main evaluation methods for "
            "retrieval-augmented generation systems?"
        ),
        "subquestions": [
            "Which metrics are used?",
            "Which datasets and baselines are common?",
        ],
        "domain": "llm_rag",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_002",
        "question": "How do agentic tool-use methods differ in planning and memory design?",
        "subquestions": [
            "How is planning represented?",
            "How is long-term state retained?",
        ],
        "domain": "llm_rag",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_003",
        "question": (
            "What are reported limitations of chain-of-thought prompting "
            "on reasoning benchmarks?"
        ),
        "subquestions": [
            "Which benchmarks expose limitations?",
            "Which failure modes are reported?",
        ],
        "domain": "llm_rag",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_004",
        "question": "How do vision-language models align image and text representations?",
        "subquestions": [
            "Which alignment objectives are used?",
            "How is alignment evaluated?",
        ],
        "domain": "vision_multimodal",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_005",
        "question": "What evaluation benchmarks are used for multimodal retrieval?",
        "subquestions": [
            "Which datasets are used?",
            "Which retrieval metrics are reported?",
        ],
        "domain": "vision_multimodal",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_006",
        "question": "How does dense retrieval compare with sparse retrieval for scientific search?",
        "subquestions": [
            "What are the reported trade-offs?",
            "Which evaluation setups are used?",
        ],
        "domain": "nlp_ir",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_007",
        "question": "What methods are used for query expansion in neural information retrieval?",
        "subquestions": [
            "What are the main query expansion families?",
            "What evidence supports their effectiveness?",
        ],
        "domain": "nlp_ir",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_008",
        "question": "How do parameter-efficient fine-tuning methods reduce training memory?",
        "subquestions": [
            "Which parameter subsets are updated?",
            "What memory and quality trade-offs are reported?",
        ],
        "domain": "ml_systems",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_009",
        "question": "What techniques accelerate transformer inference without retraining?",
        "subquestions": [
            "Which inference-time optimizations are used?",
            "What latency and quality trade-offs are reported?",
        ],
        "domain": "ml_systems",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_010",
        "question": (
            "What reproducibility practices are reported in machine "
            "learning benchmark papers?"
        ),
        "subquestions": [
            "Which artifacts and metadata are shared?",
            "What barriers to reproducibility are reported?",
        ],
        "domain": "datasets_repro",
        "year_range": [2022, 2026],
    },
)


MIN_RELEVANCE_TERMS = 2
MIN_EVIDENCE_WORDS = 8
MAX_EVIDENCE_CHARS = 400
MAX_GOLD_PAPERS = 3

SENTENCE_ENDINGS = (".", "!", "?")

GENERIC_TERMS = frozenset(
    {
        "approach", "approaches", "based", "common", "compared", "data",
        "dataset", "datasets", "deep", "different", "evaluation", "framework",
        "information", "learning", "method", "methods", "model", "models",
        "network", "networks", "neural", "paper", "papers", "performance",
        "problem", "report", "reported", "research", "result", "results",
        "study", "system", "systems", "technique", "techniques", "training",
        "used", "using", "work",
    }
)

CONTAINER_TITLE_PATTERN = re.compile(
    r"^(?:"
    r"proceedings of\b"
    r"|findings of\b"
    r"|conference on\b"
    r"|journal of\b"
    r"|ieee transactions on\b"
    r"|acm transactions on\b"
    r"|advances in neural information processing systems\b"
    r"|volume \d+\b"
    r")",
    re.IGNORECASE,
)

COMMON_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
        "have", "in", "is", "it", "its", "of", "on", "or", "that", "the",
        "their", "these", "this", "to", "was", "we", "were", "which", "with",
    }
)


def paper_key(paper: PaperCandidate) -> str:
    """Return the stable identifier used by the frozen dataset."""

    if paper.doi:
        return f"doi:{paper.doi}"
    return f"openalex:{paper.source_record_id}"


def _tokenize(value: str) -> list[str]:
    """Split text into comparable words.

    Hyphens and underscores separate words so that "retrieval-augmented" in a
    question matches "retrieval augmented" in an abstract.
    """

    flattened = value.lower().replace("-", " ").replace("_", " ")
    return [_singularize(token) for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9]*", flattened)]


def _singularize(token: str) -> str:
    """Fold simple English plurals so "datasets" matches "dataset".

    Only unambiguous endings are folded; words such as "analysis" or "class"
    are left alone.
    """

    if len(token) <= 4:
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith(("ss", "us", "is", "as")):
        return token
    if token.endswith("s"):
        return token[:-1]
    return token


def _content_terms(value: str) -> set[str]:
    """Return distinctive question terms, dropping stopwords and generic words."""

    tokens = _tokenize(value)
    return {
        token
        for token in tokens
        if token not in STOPWORDS and token not in GENERIC_TERMS and len(token) > 2
    }


def match_terms(value: str) -> set[str]:
    """Terms used to match a paper against a subquestion.

    Unlike :func:`_content_terms` this keeps generic words such as
    ``datasets`` or ``evaluation``. Filtering them out would make a subquestion
    like "Which datasets are used?" impossible to match at all.
    """

    tokens = _tokenize(value)
    return {token for token in tokens if token not in STOPWORDS and len(token) > 2}


def _relevance_score(paper: PaperCandidate, terms: set[str]) -> int:
    """Count distinctive question terms that appear as whole words in the paper."""

    words = set(_tokenize(f"{paper.title} {paper.abstract or ''}"))
    return sum(1 for term in terms if term in words)


def _assign_subquestions(
    papers: Sequence[PaperCandidate],
    terms: list[set[str]],
) -> dict[str, int]:
    """Assign papers to subquestions, guaranteeing coverage where possible.

    Each subquestion first claims the candidate that matches it best, so a
    question rarely ends up with every paper pointing at one subquestion.
    Remaining papers go to their best-matching subquestion.
    """

    assignment: dict[str, int] = {}
    for index, group in enumerate(terms):
        best_paper: PaperCandidate | None = None
        best_score = 0
        for paper in papers:
            key = paper_key(paper)
            if key in assignment:
                continue
            score = _relevance_score(paper, group)
            if score > best_score:
                best_paper, best_score = paper, score
        if best_paper is not None:
            assignment[paper_key(best_paper)] = index + 1

    for paper in papers:
        key = paper_key(paper)
        if key in assignment:
            continue
        scores = [_relevance_score(paper, group) for group in terms]
        assignment[key] = scores.index(max(scores)) + 1
    return assignment


def is_author_list(sentence: str) -> bool:
    """Detect OpenAlex abstract reconstructions that are really author lists."""

    tokens = re.findall(r"[A-Za-z][A-Za-z'-]*", sentence)
    if len(tokens) < 3:
        return False
    capitalized = sum(1 for token in tokens if token[0].isupper())
    ratio = capitalized / len(tokens)
    has_common_word = any(token.lower() in COMMON_WORDS for token in tokens)
    return ratio >= 0.75 and not has_common_word


def _strip_abstract_prefix(value: str) -> str:
    normalized = " ".join(value.replace("\\n", " ").split())
    return re.sub(r"^abstract[\s:.-]+", "", normalized, flags=re.IGNORECASE)


def _repair_missing_sentence_spaces(value: str) -> str:
    """Restore spaces that OpenAlex drops after a sentence period.

    Abstracts are rebuilt from an inverted index, so a run such as
    ``knowledge.Retrieval`` arrives without whitespace. Reinserting the space is
    pure whitespace normalization, the same class of change as collapsing runs
    of spaces.
    """

    return re.sub(r"([.!?])(?=[A-Z])", r"\1 ", value)


def _split_sentences(abstract: str | None) -> list[str]:
    """Split a reconstructed abstract into candidate sentences."""

    if not abstract:
        return []
    cleaned = _repair_missing_sentence_spaces(_strip_abstract_prefix(abstract))
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]


def _is_usable_sentence(sentence: str) -> bool:
    """Reject fragments, author lists and oversized run-on text."""

    if len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", sentence)) < MIN_EVIDENCE_WORDS:
        return False
    if not sentence.endswith(SENTENCE_ENDINGS):
        return False
    if len(sentence) > MAX_EVIDENCE_CHARS:
        return False
    if is_author_list(sentence):
        return False
    # Crossref and OpenAlex records for some venues prepend the author list and
    # the container title, so the "abstract" is pure metadata.
    return not CONTAINER_TITLE_PATTERN.match(sentence.strip())


def _term_overlap(sentence: str, terms: set[str]) -> int:
    return len(terms & set(_tokenize(sentence)))


def _normalize_for_compare(value: str) -> str:
    return " ".join(value.lower().rstrip(".").split())


def usable_evidence_sentence(
    abstract: str | None,
    *,
    prefer_terms: set[str] | None = None,
    reject_exact: set[str] | None = None,
) -> str | None:
    """Return one citable sentence, or None when the text is not usable.

    The first usable sentence is the default. When ``prefer_terms`` is given the
    sentence with the largest overlap with those terms wins, so the recorded
    quote supports the subquestion instead of restating the abstract's
    background. Ties keep the earliest sentence.
    """

    sentences = [item for item in _split_sentences(abstract) if _is_usable_sentence(item)]
    if reject_exact:
        blocked = {
            _normalize_for_compare(value) for value in reject_exact if value and value.strip()
        }
        sentences = [
            item for item in sentences if _normalize_for_compare(item) not in blocked
        ]
    if not sentences:
        return None
    if prefer_terms:
        best_index = max(
            range(len(sentences)),
            key=lambda index: (_term_overlap(sentences[index], prefer_terms), -index),
        )
        return sentences[best_index]
    return sentences[0]


def paper_to_annotation(
    paper: PaperCandidate,
    *,
    supports_subquestion: int,
    prefer_terms: set[str] | None = None,
) -> dict[str, Any] | None:
    """Convert a paper into one gold-evidence annotation.

    Returns None when the record has no sentence that can carry evidence. The
    paper year is recorded so the review can check the year range without
    re-querying the source.
    """

    quote = usable_evidence_sentence(
        paper.abstract,
        prefer_terms=prefer_terms,
        reject_exact={paper.venue or "", paper.title},
    )
    if quote is None:
        return None
    return {
        "paper_key": paper_key(paper),
        "evidence_level": "abstract",
        "quote": quote,
        "locator": {"section": "Abstract"},
        "supports_subquestion": supports_subquestion,
        "paper_year": paper.year,
    }


def within_year_range(
    paper: PaperCandidate,
    year_range: tuple[int, int] | None,
) -> bool:
    """Return True when a paper is inside the declared year range.

    Papers with an unknown year are kept; they are rare and the review can
    judge them individually.
    """

    if year_range is None or paper.year is None:
        return True
    return year_range[0] <= paper.year <= year_range[1]


async def build_seed_questions(
    client: OpenAlexClient,
    *,
    seeds: Sequence[dict[str, Any]] = PILOT_SEEDS,
    results_per_question: int = 25,
    max_gold_papers: int = MAX_GOLD_PAPERS,
) -> list[dict[str, Any]]:
    """Query OpenAlex and build seed annotations for each question.

    Every variant produced by the planner is searched, results are deduplicated,
    and only papers whose title or abstract overlaps the question are kept, so
    ``gold_papers`` always matches the papers that actually carry evidence.
    """

    records: list[dict[str, Any]] = []
    for seed in seeds:
        question = str(seed["question"])
        subquestions = [str(item) for item in seed["subquestions"]]
        plan = plan_research(question, available_sources=("openalex",))
        question_terms = sorted(_content_terms(question))
        variants: list[str] = list(plan.query_variants)
        for subquestion in subquestions:
            sub_terms = sorted(match_terms(subquestion))
            if sub_terms:
                variants.append(
                    " ".join(dict.fromkeys([*question_terms, *sub_terms]))
                )

        candidates: list[PaperCandidate] = []
        seen: set[str] = set()
        for variant in dict.fromkeys(variants):
            result = await client.search(variant, max_results=results_per_question)
            for paper in result.papers:
                key = paper_key(paper)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(paper)

        relevance_terms = _content_terms(" ".join([question, *subquestions]))
        subquestion_terms = [match_terms(item) for item in subquestions]

        year_range = seed.get("year_range")
        parsed_year_range: tuple[int, int] | None = None
        if (
            isinstance(year_range, (list, tuple))
            and len(year_range) == 2
            and all(isinstance(value, int) for value in year_range)
        ):
            parsed_year_range = (int(year_range[0]), int(year_range[1]))

        in_range = [
            paper for paper in candidates if within_year_range(paper, parsed_year_range)
        ]
        year_filter_relaxed = False
        if not in_range and candidates:
            # The declared range excluded everything; keep the candidates so the
            # question is not silently empty, and flag it for the review.
            in_range = list(candidates)
            year_filter_relaxed = True

        scored = [
            (paper, _relevance_score(paper, relevance_terms)) for paper in in_range
        ]
        selected = [item for item in scored if item[1] >= MIN_RELEVANCE_TERMS]
        relaxed = False
        if not selected:
            # Keep the question usable: fall back to the best available
            # candidates, and record that the match was weak.
            selected = [item for item in scored if item[1] > 0]
            relaxed = bool(selected)
        selected = selected[:max_gold_papers]
        if not selected:
            relaxed = False

        assignment = _assign_subquestions(
            [paper for paper, _score in selected], subquestion_terms
        )
        gold_papers: list[str] = []
        gold_evidence: list[dict[str, Any]] = []
        for paper, _score in selected:
            subquestion_index = assignment[paper_key(paper)]
            annotation = paper_to_annotation(
                paper,
                supports_subquestion=subquestion_index,
                prefer_terms=subquestion_terms[subquestion_index - 1],
            )
            if annotation is None:
                continue
            gold_papers.append(annotation["paper_key"])
            gold_evidence.append(annotation)

        covered = {item["supports_subquestion"] for item in gold_evidence}
        uncovered = [
            index
            for index in range(1, len(subquestions) + 1)
            if index not in covered
        ]

        notes = (
            "Seed annotation generated from OpenAlex metadata; "
            "requires human verification before freezing."
        )
        if relaxed:
            notes += " Relevance threshold relaxed: no strong match was found."
        if year_filter_relaxed:
            notes += " Year range excluded every candidate; range not enforced."
        if uncovered:
            missing = ", ".join(str(index) for index in uncovered)
            notes += f" Subquestion(s) {missing} have no supporting evidence."

        records.append(
            {
                **seed,
                "gold_papers": gold_papers,
                "gold_evidence": gold_evidence,
                "acceptable_answers": [],
                "notes": notes,
            }
        )
    return records


async def _amain(output_path: Path) -> None:
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        client = build_openalex_client(http_client)
        records = await build_seed_questions(client)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    """Generate the Pilot seed JSONL file."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation/datasets/pilot_questions.seed.jsonl"),
    )
    args = parser.parse_args()
    asyncio.run(_amain(args.output))


if __name__ == "__main__":
    main()
