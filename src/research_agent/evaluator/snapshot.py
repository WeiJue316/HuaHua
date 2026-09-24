"""Frozen source snapshot used for controlled system comparisons."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_agent.evaluator.bm25 import Bm25Document, Bm25Index
from research_agent.mcp_servers.common import PaperCandidate
from research_agent.storage.repository import canonical_key


@dataclass(frozen=True)
class SnapshotSearchResult:
    """Search result shape consumed by federated routing and ReAct."""

    papers: list[PaperCandidate]


class SnapshotSearchClient:
    """Search one source's candidates from a frozen global snapshot."""

    def __init__(self, source: str, papers: Sequence[PaperCandidate]) -> None:
        self.source = source
        self.papers = tuple(papers)
        self._by_key = {canonical_key(paper): paper for paper in self.papers}
        self._index = (
            Bm25Index(
                [
                    Bm25Document(
                        paper_key=canonical_key(paper),
                        title=paper.title,
                        abstract=paper.abstract or "",
                        year=paper.year,
                        doi=paper.doi,
                    )
                    for paper in self.papers
                ]
            )
            if self.papers
            else None
        )

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
    ) -> SnapshotSearchResult:
        if self._index is None:
            return SnapshotSearchResult(papers=[])
        hits = self._index.search(query, top_k=max_results)
        return SnapshotSearchResult(
            papers=[self._by_key[hit.document.paper_key] for hit in hits]
        )


class SourceSnapshot:
    """Immutable paper pool grouped by source and identified by a stable hash."""

    def __init__(
        self,
        papers_by_source: Mapping[str, Sequence[PaperCandidate]],
    ) -> None:
        if not papers_by_source:
            raise ValueError("source snapshot must not be empty")
        self.papers_by_source = {
            source: tuple(papers)
            for source, papers in sorted(papers_by_source.items())
            if papers
        }
        if not self.papers_by_source:
            raise ValueError("source snapshot must contain at least one paper")
        self.snapshot_hash = self._compute_hash()

    @classmethod
    def from_jsonl(cls, path: Path) -> SourceSnapshot:
        grouped: dict[str, list[PaperCandidate]] = defaultdict(list)
        seen: set[tuple[str, str]] = set()
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                raw: Any = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"invalid snapshot JSON on line {line_number}: {exc}"
                ) from exc
            if not isinstance(raw, dict):
                raise ValueError(f"snapshot line {line_number} must be an object")
            paper = PaperCandidate.model_validate(raw)
            key = (paper.source, canonical_key(paper))
            if key in seen:
                continue
            seen.add(key)
            grouped[paper.source].append(paper)
        return cls(grouped)

    def clients_for(self, sources: Iterable[str]) -> dict[str, SnapshotSearchClient]:
        return {
            source: SnapshotSearchClient(source, self.papers_by_source.get(source, ()))
            for source in sources
        }

    def _compute_hash(self) -> str:
        records = [
            paper.model_dump(mode="json")
            for source in sorted(self.papers_by_source)
            for paper in sorted(
                self.papers_by_source[source],
                key=canonical_key,
            )
        ]
        payload = json.dumps(
            records,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()