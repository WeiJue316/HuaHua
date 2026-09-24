from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_agent.evaluator.bm25 import Bm25Document, Bm25Index


def test_bm25_ranks_the_document_matching_more_query_terms() -> None:
    index = Bm25Index(
        [
            Bm25Document(
                paper_key="doi:relevant",
                title="Dense and sparse retrieval for scientific search",
                abstract="We compare dense retrieval with BM25 on scientific search benchmarks.",
            ),
            Bm25Document(
                paper_key="doi:adjacent",
                title="Retrieval augmented generation evaluation",
                abstract="A study of answer quality.",
            ),
        ]
    )

    hits = index.search("dense sparse retrieval scientific search", top_k=2)

    assert hits[0].document.paper_key == "doi:relevant"
    assert hits[0].score > hits[1].score


def test_bm25_returns_no_hits_when_no_query_term_is_present() -> None:
    index = Bm25Index(
        [Bm25Document(paper_key="doi:one", title="Vision language alignment")]
    )

    assert index.search("sparse retrieval", top_k=5) == []


def test_bm25_is_deterministic_for_tied_scores() -> None:
    index = Bm25Index(
        [
            Bm25Document(paper_key="doi:b", title="retrieval benchmark"),
            Bm25Document(paper_key="doi:a", title="retrieval benchmark"),
        ]
    )

    hits = index.search("retrieval", top_k=2)

    assert [hit.document.paper_key for hit in hits] == ["doi:a", "doi:b"]


def test_corpus_loader_rejects_duplicate_paper_keys(tmp_path: Path) -> None:
    path = tmp_path / "corpus.jsonl"
    rows = [
        {"paper_key": "doi:same", "title": "One"},
        {"paper_key": "doi:same", "title": "Two"},
    ]
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate paper_key"):
        Bm25Index.from_jsonl(path)


def test_corpus_hash_is_independent_of_input_order(tmp_path: Path) -> None:
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    rows = [
        {"paper_key": "doi:b", "title": "B"},
        {"paper_key": "doi:a", "title": "A"},
    ]
    first.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
    )
    second.write_text(
        "\n".join(json.dumps(row) for row in reversed(rows)) + "\n",
        encoding="utf-8",
    )

    assert Bm25Index.from_jsonl(first).corpus_hash == Bm25Index.from_jsonl(
        second
    ).corpus_hash