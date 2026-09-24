from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_agent.evaluator.snapshot import SourceSnapshot
from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate


def _paper(
    *,
    source: str,
    title: str,
    doi: str | None,
) -> PaperCandidate:
    return PaperCandidate(
        source=source,
        source_record_id="W1",
        title=title,
        abstract="retrieval benchmark evidence",
        doi=doi,
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=True, status="gold"),
    )


def _write_snapshot(path: Path, papers: list[PaperCandidate]) -> None:
    path.write_text(
        "\n".join(
            json.dumps(paper.model_dump(mode="json"), ensure_ascii=False)
            for paper in papers
        )
        + "\n",
        encoding="utf-8",
    )


@pytest.mark.asyncio
async def test_snapshot_client_searches_only_its_source(tmp_path: Path) -> None:
    path = tmp_path / "snapshot.jsonl"
    _write_snapshot(
        path,
        [
            _paper(source="openalex", title="Retrieval benchmark", doi="10.1/a"),
            _paper(source="crossref", title="Vision benchmark", doi="10.1/b"),
        ],
    )
    snapshot = SourceSnapshot.from_jsonl(path)

    result = await snapshot.clients_for(["openalex"])["openalex"].search(
        "retrieval benchmark", max_results=5
    )

    assert [paper.doi for paper in result.papers] == ["10.1/a"]


@pytest.mark.asyncio
async def test_snapshot_missing_source_returns_no_papers(tmp_path: Path) -> None:
    path = tmp_path / "snapshot.jsonl"
    _write_snapshot(path, [_paper(source="openalex", title="A", doi="10.1/a")])
    snapshot = SourceSnapshot.from_jsonl(path)

    result = await snapshot.clients_for(["crossref"])["crossref"].search(
        "anything", max_results=5
    )

    assert result.papers == []


def test_snapshot_hash_is_independent_of_input_order(tmp_path: Path) -> None:
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    papers = [
        _paper(source="openalex", title="A", doi="10.1/a"),
        _paper(source="crossref", title="B", doi="10.1/b"),
    ]
    _write_snapshot(first, papers)
    _write_snapshot(second, list(reversed(papers)))

    assert SourceSnapshot.from_jsonl(first).snapshot_hash == SourceSnapshot.from_jsonl(
        second
    ).snapshot_hash