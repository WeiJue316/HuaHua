"""Deterministic evaluation metrics.

Everything here is computed from stored records, so it can be recomputed from a
run without repeating network calls. Metrics that need human or model judgement
(for example whether a quote truly supports a claim) are deliberately not
computed here; they are recorded separately as manual review.
"""

from __future__ import annotations

import math
import sqlite3
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Any

from research_agent.identity import label_aliases, matched_gold_keys


@dataclass(frozen=True)
class RetrievalMetrics:
    """How many of the known-relevant papers a run actually retrieved."""

    retrieved_count: int
    gold_count: int
    matched_count: int
    recall_kept: float
    precision_kept: float
    k: int
    precision_at_k: float
    recall_at_k: float
    ndcg_at_k: float

    def to_dict(self) -> dict[str, float]:
        payload: dict[str, Any] = asdict(self)
        return {key: float(value) for key, value in payload.items()}


def _deduped(keys: Sequence[str]) -> list[str]:
    """Keep the first spelling of each paper."""

    seen: set[str] = set()
    ordered: list[str] = []
    for key in keys:
        aliases = set(label_aliases(key))
        if aliases & seen:
            continue
        seen.update(aliases)
        ordered.append(key)
    return ordered


def _matches_gold(key: str, gold_aliases: set[str]) -> bool:
    return bool(label_aliases(key) & gold_aliases)


def _dcg(gains: Sequence[int]) -> float:
    return sum(gain / math.log2(rank + 2) for rank, gain in enumerate(gains))


def retrieval_metrics(
    *,
    retrieved_keys: set[str],
    gold_keys: set[str],
    extra_aliases: set[str] | None = None,
    ranked_keys: Sequence[str] = (),
    k: int = 0,
) -> RetrievalMetrics:
    """Compare retrieved papers with the gold set, as a set and as Top-K.

    ``recall_kept`` and ``precision_kept`` use the whole kept set. ``precision_at_k``,
    ``recall_at_k`` and ``ndcg_at_k`` use the first ``k`` items of ``ranked_keys``.
    Precision@K divides by ``k`` even when the list is shorter. Identity aliases
    make an arXiv id and its arXiv DOI the same paper.
    """

    if k < 0:
        raise ValueError("k must not be negative")
    matched = matched_gold_keys(
        retrieved_keys,
        gold_keys,
        extra_aliases=extra_aliases,
    )
    gold_aliases: set[str] = set()
    for gold in gold_keys:
        gold_aliases.update(label_aliases(gold))
    top = _deduped(ranked_keys)[:k]
    top_hits = matched_gold_keys(set(top), gold_keys)
    gains = [1 if _matches_gold(key, gold_aliases) else 0 for key in top]
    gains.extend([0] * (k - len(gains)))
    ideal_hits = min(k, len(gold_keys))
    ideal = [1] * ideal_hits + [0] * (k - ideal_hits)
    ideal_dcg = _dcg(ideal)
    return RetrievalMetrics(
        retrieved_count=len(retrieved_keys),
        gold_count=len(gold_keys),
        matched_count=len(matched),
        recall_kept=len(matched) / len(gold_keys) if gold_keys else 0.0,
        precision_kept=len(matched) / len(retrieved_keys) if retrieved_keys else 0.0,
        k=k,
        precision_at_k=len(top_hits) / k if k else 0.0,
        recall_at_k=len(top_hits) / len(gold_keys) if gold_keys and k else 0.0,
        ndcg_at_k=_dcg(gains) / ideal_dcg if ideal_dcg else 0.0,
    )


@dataclass(frozen=True)
class EvidenceMetrics:
    """Structural health of the evidence chain for one run."""

    claim_count: int
    supported_count: int
    partially_supported_count: int
    unsupported_count: int
    disputed_count: int
    claims_with_evidence: int
    dangling_support_count: int
    evidence_coverage: float
    unsupported_claim_rate: float

    def to_dict(self) -> dict[str, float]:
        payload: dict[str, Any] = asdict(self)
        return {key: float(value) for key, value in payload.items()}


def evidence_metrics(claim_rows: list[tuple[str, int]]) -> EvidenceMetrics:
    """Summarise claim support and evidence linkage.

    ``claim_rows`` pairs each claim's ``support_status`` with the number of
    evidence spans linked to it.
    """

    total = len(claim_rows)
    statuses = [status for status, _ in claim_rows]
    with_evidence = sum(1 for _, count in claim_rows if count > 0)
    dangling = sum(
        1
        for status, count in claim_rows
        if status in {"supported", "partially_supported"} and count == 0
    )
    unsupported = statuses.count("unsupported")
    return EvidenceMetrics(
        claim_count=total,
        supported_count=statuses.count("supported"),
        partially_supported_count=statuses.count("partially_supported"),
        unsupported_count=unsupported,
        disputed_count=statuses.count("disputed"),
        claims_with_evidence=with_evidence,
        dangling_support_count=dangling,
        evidence_coverage=with_evidence / total if total else 0.0,
        unsupported_claim_rate=unsupported / total if total else 0.0,
    )


@dataclass(frozen=True)
class ModelUsage:
    """Aggregated model calls recorded for one research run."""

    calls: int
    input_tokens: int
    output_tokens: int
    latency_ms: int

    def to_dict(self) -> dict[str, float]:
        return {
            "llm_calls": float(self.calls),
            "input_tokens": float(self.input_tokens),
            "output_tokens": float(self.output_tokens),
            "model_latency_ms": float(self.latency_ms),
        }


def load_model_usage(
    connection: sqlite3.Connection,
    run_id: str,
) -> ModelUsage:
    """Aggregate every model-call attempt recorded for a run.

    Failed attempts remain in the result because a retry or rejected response
    still consumes latency and may consume provider tokens.
    """

    row = connection.execute(
        """
        SELECT COUNT(*),
               COALESCE(SUM(input_tokens), 0),
               COALESCE(SUM(output_tokens), 0),
               COALESCE(SUM(latency_ms), 0)
        FROM model_call
        WHERE run_id = ?
        """,
        (run_id,),
    ).fetchone()
    if row is None:
        return ModelUsage(calls=0, input_tokens=0, output_tokens=0, latency_ms=0)
    return ModelUsage(
        calls=int(row[0] or 0),
        input_tokens=int(row[1] or 0),
        output_tokens=int(row[2] or 0),
        latency_ms=int(row[3] or 0),
    )


def source_coverage(
    *, contributing_sources: set[str], allowed_sources: set[str]
) -> float:
    """Share of the permitted sources that contributed at least one result."""

    if not allowed_sources:
        return 0.0
    return len(contributing_sources & allowed_sources) / len(allowed_sources)


def load_retrieved_keys(
    connection: sqlite3.Connection,
    run_id: str,
    *,
    kept_only: bool = False,
) -> set[str]:
    """Return the canonical keys of source records first created by a run.

    **Do not use this for retrieval metrics.** ``record_source_record`` dedupes
    by ``(source, source_record_id, content_hash)`` across runs, so a paper
    retrieved a second time reuses the first run's source record and the join
    through ``source_call.run_id`` misses it. A real two-system smoke test
    showed a run reporting ten persisted papers while this query returned one.

    Use ``ResearchRunResult.retrieved_paper_keys`` instead: the runtime records
    the keys in memory as it persists them, and subtracts
    ``dropped_paper_keys`` for the kept set. This helper remains for inspecting
    first-seen records only.
    """

    sql = """
        SELECT DISTINCT p.canonical_key
        FROM paper p
        JOIN paper_source_record psr ON psr.paper_id = p.id
        JOIN source_record sr ON sr.id = psr.source_record_id
        JOIN source_call sc ON sc.id = sr.source_call_id
        WHERE sc.run_id = ?
    """
    if kept_only:
        sql += """
          AND NOT EXISTS (
              SELECT 1 FROM audit_event ae
              WHERE ae.run_id = sc.run_id
                AND ae.action = 'semantic_relevance'
                AND ae.decision = 'denied'
                AND ae.target_id = sr.id
          )
        """
    rows = connection.execute(sql, (run_id,)).fetchall()
    return {row[0] for row in rows}


def load_claim_rows(
    connection: sqlite3.Connection, run_id: str
) -> list[tuple[str, int]]:
    """Return one ``(support_status, evidence_count)`` pair per claim."""

    rows = connection.execute(
        """
        SELECT c.support_status,
               (SELECT COUNT(*) FROM claim_evidence ce WHERE ce.claim_id = c.id)
        FROM claim c
        JOIN report r ON r.id = c.report_id
        WHERE r.run_id = ?
        """,
        (run_id,),
    ).fetchall()
    return [(str(row[0]), int(row[1])) for row in rows]


def load_contributing_sources(
    connection: sqlite3.Connection, run_id: str
) -> set[str]:
    """Return the sources that returned at least one usable record."""

    rows = connection.execute(
        """
        SELECT DISTINCT sc.source
        FROM source_call sc
        JOIN source_record sr ON sr.source_call_id = sc.id
        WHERE sc.run_id = ?
        """,
        (run_id,),
    ).fetchall()
    return {str(row[0]) for row in rows}