"""B0 baseline: frozen BM25 retrieval followed by one LLM summary call."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from research_agent.evaluator.bm25 import Bm25Hit, Bm25Index
from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.llm.gateway import ModelGateway, ModelGatewayError


@dataclass(frozen=True)
class B0Outcome:
    """Artifacts and cost metadata from one B0 case."""

    retrieved_keys: frozenset[str]
    report: str
    report_path: Path
    corpus_hash: str
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: int | None


class B0Baseline:
    """Run the weakest intended workflow: BM25 Top-K plus one summary call."""

    def __init__(
        self,
        *,
        index: Bm25Index,
        gateway: ModelGateway,
        reports_root: Path,
        top_k: int = 10,
    ) -> None:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        self.index = index
        self.gateway = gateway
        self.reports_root = reports_root
        self.top_k = top_k

    async def run(
        self,
        question: EvaluationQuestion,
        *,
        run_number: int,
    ) -> B0Outcome:
        query_parts = [question.question, *question.subquestions]
        hits = self.index.search(" ".join(query_parts), top_k=self.top_k)
        response = await self.gateway.complete(
            prompt_hash=f"b0-summary-v1-{self.index.corpus_hash[:12]}",
            system=(
                "You are a literature research assistant. Summarize only the "
                "retrieved papers supplied by the user. Do not invent papers, "
                "citations, numbers, or findings. State clearly when the supplied "
                "evidence is insufficient."
            ),
            user=self._build_prompt(question, hits),
            max_output_tokens=6000,
        )
        if response.truncated:
            raise ModelGatewayError(
                "B0 summary was truncated; increase the output token budget"
            )

        report = self._render_report(question, hits, response.content)
        output_dir = self.reports_root / "b0"
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / (
            f"{question.question_id}-run{run_number}-{uuid4().hex[:8]}.md"
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")
        return B0Outcome(
            retrieved_keys=frozenset(hit.document.paper_key for hit in hits),
            report=report,
            report_path=report_path,
            corpus_hash=self.index.corpus_hash,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=response.latency_ms,
        )

    @staticmethod
    def _build_prompt(
        question: EvaluationQuestion,
        hits: list[Bm25Hit],
    ) -> str:
        subquestions = "\n".join(
            f"{index}. {item}"
            for index, item in enumerate(question.subquestions, start=1)
        )
        papers = "\n\n".join(
            B0Baseline._format_hit(index, hit)
            for index, hit in enumerate(hits, start=1)
        )
        if not papers:
            papers = "No papers were retrieved from the frozen corpus."
        return (
            f"Research question:\n{question.question}\n\n"
            f"Subquestions:\n{subquestions or '(none)'}\n\n"
            f"Retrieved papers:\n{papers}\n\n"
            "Write a concise report that answers the question using only the "
            "retrieved papers. Include the paper numbers you rely on."
        )

    @staticmethod
    def _format_hit(index: int, hit: Bm25Hit) -> str:
        document = hit.document
        identifier = document.doi or document.paper_key
        year = str(document.year) if document.year is not None else "unknown"
        abstract = " ".join(document.abstract.split())
        if len(abstract) > 1200:
            abstract = abstract[:1200].rstrip() + "..."
        return (
            f"[{index}] {document.title}\n"
            f"Year: {year}\nDOI/Key: {identifier}\n"
            f"Abstract: {abstract or '(not available)'}"
        )

    @staticmethod
    def _render_report(
        question: EvaluationQuestion,
        hits: list[Bm25Hit],
        summary: str,
    ) -> str:
        retrieved = "\n".join(
            f"{index}. {hit.document.title} ({hit.document.doi or hit.document.paper_key})"
            for index, hit in enumerate(hits, start=1)
        )
        return (
            f"# B0 Baseline Report\n\n"
            f"**Question**: {question.question}\n\n"
            f"## Retrieved Papers\n\n{retrieved or '(none)'}\n\n"
            f"## Summary\n\n{summary.strip()}\n"
        )