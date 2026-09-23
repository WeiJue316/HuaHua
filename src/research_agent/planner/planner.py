"""Deterministic research planning and source scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

SOURCE_BASE_SCORES = {
    "arxiv": 1.0,
    "openalex": 1.0,
    "crossref": 1.0,
    "semantic_scholar": 1.0,
    "dblp": 1.0,
}


@dataclass(frozen=True)
class ResearchPlan:
    """A reproducible plan for one research question."""

    question: str
    query_variants: tuple[str, ...]
    selected_sources: tuple[str, ...]
    fallback_sources: tuple[str, ...]
    max_results_per_source: int
    max_concurrency: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize the plan into the Run configuration snapshot."""

        return {
            "query_variants": list(self.query_variants),
            "selected_sources": list(self.selected_sources),
            "fallback_sources": list(self.fallback_sources),
            "max_results_per_source": self.max_results_per_source,
            "max_concurrency": self.max_concurrency,
            "reason": self.reason,
        }


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _query_variants(question: str) -> tuple[str, ...]:
    normalized = " ".join(question.split())
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*", normalized)
    variants = [normalized]
    if len(tokens) > 5:
        variants.append(" ".join(tokens[:5]))
    if " " in normalized:
        variants.append(f'"{normalized}"')
    return tuple(dict.fromkeys(variants))


def plan_research(
    question: str,
    *,
    available_sources: tuple[str, ...],
    max_results_per_source: int = 10,
    max_concurrency: int = 5,
    max_sources: int | None = None,
) -> ResearchPlan:
    """Create a deterministic source plan for a research question."""

    text = question.lower()
    needs_citations = _contains_any(
        text,
        (
            "citation",
            "citations",
            "reference",
            "references",
            "survey",
            "综述",
            "引用",
            "related work",
        ),
    )
    needs_full_text = _contains_any(
        text,
        ("full text", "full-text", "pdf", "全文"),
    )
    needs_bibliography = _contains_any(
        text,
        ("venue", "conference", "journal", "bibliography", "dblp", "会议", "期刊", "书目"),
    )

    scores: dict[str, float] = {}
    for source in available_sources:
        score = SOURCE_BASE_SCORES.get(source, 0.0)
        if needs_citations:
            score += {
                "openalex": 5.0,
                "semantic_scholar": 5.0,
                "crossref": 2.0,
            }.get(source, 0.0)
        if needs_full_text:
            score += {
                "arxiv": 5.0,
                "openalex": 1.0,
                "semantic_scholar": 1.0,
            }.get(source, 0.0)
        if needs_bibliography:
            score += {
                "dblp": 5.0,
                "crossref": 3.0,
            }.get(source, 0.0)
        scores[source] = score

    ordered = sorted(
        available_sources,
        key=lambda source: (-scores[source], available_sources.index(source)),
    )
    limit = len(ordered) if max_sources is None else max(1, min(max_sources, len(ordered)))
    selected = tuple(ordered[:limit])
    fallback = tuple(ordered[limit:])
    reasons: list[str] = []
    if needs_citations:
        reasons.append("citations")
    if needs_full_text:
        reasons.append("full_text")
    if needs_bibliography:
        reasons.append("bibliography")
    if not reasons:
        reasons.append("broad_metadata")

    return ResearchPlan(
        question=question,
        query_variants=_query_variants(question),
        selected_sources=selected,
        fallback_sources=fallback,
        max_results_per_source=max_results_per_source,
        max_concurrency=max(1, min(max_concurrency, len(selected))),
        reason="+".join(reasons),
    )
