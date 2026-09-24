"""Adapt the research pipeline to the evaluation runner's callback contract."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import httpx

from research_agent.evaluator.b0 import B0Baseline
from research_agent.evaluator.bm25 import Bm25Index
from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.evaluator.metrics import (
    evidence_metrics,
    load_claim_rows,
    retrieval_metrics,
    source_coverage,
)
from research_agent.evaluator.react import PureReActBaseline
from research_agent.evaluator.runner import EvaluationCaseOutcome
from research_agent.evaluator.systems import (
    SystemConfig,
    get_system,
    restrict_sources,
)
from research_agent.llm.gateway import ModelGateway
from research_agent.mcp_servers.cache import ResponseCache
from research_agent.planner.planner import plan_research
from research_agent.policy.relevance import RelevanceJudge
from research_agent.router.registry import build_source_clients
from research_agent.runtime.research_service import (
    ResearchRunResult,
    run_federated_research,
)
from research_agent.storage.migrations import connect_database

SYSTEM_VERSION = "research-agent/0.1"


@dataclass(frozen=True)
class CaseRunnerSettings:
    """Everything a case needs except the question and the system."""

    db_path: Path
    reports_root: Path
    max_results_per_source: int = 10
    dataset_version: str = "pilot-v2"
    allowed_sources: tuple[str, ...] | None = None


class ResearchCaseRunner:
    """Run one (question, system, repeat) cell of the evaluation matrix."""

    def __init__(
        self,
        *,
        questions: Sequence[EvaluationQuestion],
        settings: CaseRunnerSettings,
        http_client: httpx.AsyncClient,
        gateway: ModelGateway | None = None,
        cache: ResponseCache | None = None,
        b0_index: Bm25Index | None = None,
    ) -> None:
        self.questions = {question.question_id: question for question in questions}
        self.settings = settings
        self.http_client = http_client
        self.gateway = gateway
        self.cache = cache
        self.b0_index = b0_index

    async def __call__(
        self, question_id: str, system_id: str, run_number: int
    ) -> EvaluationCaseOutcome:
        try:
            question = self.questions[question_id]
        except KeyError:
            return EvaluationCaseOutcome(error_code="unknown_question")
        try:
            config = get_system(system_id)
        except (KeyError, NotImplementedError) as exc:
            return EvaluationCaseOutcome(error_code=type(exc).__name__)

        if system_id == "B0":
            return await self._run_b0(question, run_number)
        if system_id == "B2":
            return await self._run_b2(question, run_number, config)

        source_ids = self._source_ids_for(config)
        if not source_ids:
            return EvaluationCaseOutcome(error_code="no_sources")

        clients = build_source_clients(self.http_client, source_ids, cache=self.cache)
        plan = plan_research(
            question.question,
            available_sources=tuple(source_ids),
            max_results_per_source=self.settings.max_results_per_source,
            max_sources=len(source_ids),
        )
        judge = None
        if config.relevance_filter:
            if self.gateway is None:
                return EvaluationCaseOutcome(error_code="no_model_gateway")
            judge = RelevanceJudge(self.gateway)

        result = await run_federated_research(
            question=question.question,
            db_path=self.settings.db_path,
            reports_root=self.settings.reports_root,
            clients=clients,
            max_results_per_source=self.settings.max_results_per_source,
            plan=plan,
            relevance_judge=judge,
            subquestions=question.subquestions,
            response_cache=self.cache,
        )

        metrics = self._metrics(question, result)
        return EvaluationCaseOutcome(
            research_run_id=result.run_id,
            metrics=metrics,
        )

    async def _run_b0(
        self,
        question: EvaluationQuestion,
        run_number: int,
    ) -> EvaluationCaseOutcome:
        if self.b0_index is None:
            return EvaluationCaseOutcome(error_code="b0_corpus_missing")
        if self.gateway is None:
            return EvaluationCaseOutcome(error_code="no_model_gateway")
        baseline = B0Baseline(
            index=self.b0_index,
            gateway=self.gateway,
            reports_root=self.settings.reports_root,
            top_k=self.settings.max_results_per_source,
        )
        outcome = await baseline.run(question, run_number=run_number)
        retrieval = retrieval_metrics(
            retrieved_keys=set(outcome.retrieved_keys),
            gold_keys=set(question.gold_papers),
        )
        return EvaluationCaseOutcome(
            metrics={
                **retrieval.to_dict(),
                "llm_calls": 1.0,
                "input_tokens": float(outcome.input_tokens or 0),
                "output_tokens": float(outcome.output_tokens or 0),
                "latency_ms": float(outcome.latency_ms or 0),
                "report_written": 1.0,
                "report_chars": float(len(outcome.report)),
            }
        )

    async def _run_b2(
        self,
        question: EvaluationQuestion,
        run_number: int,
        config: SystemConfig,
    ) -> EvaluationCaseOutcome:
        if self.gateway is None:
            return EvaluationCaseOutcome(error_code="no_model_gateway")
        source_ids = self._source_ids_for(config)
        if not source_ids:
            return EvaluationCaseOutcome(error_code="no_sources")
        clients = build_source_clients(self.http_client, source_ids, cache=self.cache)
        baseline = PureReActBaseline(
            clients=clients,
            gateway=self.gateway,
            reports_root=self.settings.reports_root,
            max_steps=8,
            max_results_per_search=self.settings.max_results_per_source,
        )
        outcome = await baseline.run(question, run_number=run_number)
        retrieval = retrieval_metrics(
            retrieved_keys=set(outcome.retrieved_keys),
            gold_keys=set(question.gold_papers),
        )
        return EvaluationCaseOutcome(
            metrics={
                **retrieval.to_dict(),
                "llm_calls": float(outcome.model_calls),
                "input_tokens": float(outcome.input_tokens),
                "output_tokens": float(outcome.output_tokens),
                "latency_ms": float(outcome.latency_ms),
                "steps_used": float(outcome.steps_used),
                "search_calls": float(outcome.search_calls),
                "report_written": 1.0,
                "report_chars": float(len(outcome.report)),
            }
        )

    def _source_ids_for(self, config: SystemConfig) -> tuple[str, ...]:
        requested = (
            config.sources if config.sources is not None else self._default_sources()
        )
        return restrict_sources(requested, self.settings.allowed_sources)

    @staticmethod
    def _default_sources() -> tuple[str, ...]:
        from research_agent.router.registry import SUPPORTED_SOURCES

        return tuple(SUPPORTED_SOURCES)

    def _metrics(
        self, question: EvaluationQuestion, result: ResearchRunResult
    ) -> dict[str, float]:
        stored = set(result.retrieved_paper_keys)
        kept = stored - set(result.dropped_paper_keys)
        claims = load_claim_rows_checked(self.settings.db_path, result.run_id)
        contributing = {
            source for source, count in result.source_counts.items() if count > 0
        }

        retrieval = retrieval_metrics(
            retrieved_keys=kept,
            gold_keys=set(question.gold_papers),
        )
        evidence = evidence_metrics(claims)
        coverage = source_coverage(
            contributing_sources=contributing,
            allowed_sources=set(result.source_counts),
        )
        return {
            **retrieval.to_dict(),
            **evidence.to_dict(),
            "source_coverage": coverage,
            "relevance_dropped": float(result.relevance_dropped),
            "relevance_failures": float(result.relevance_failures),
            "retrieved_paper_count": float(result.paper_count),
            "stored_paper_count": float(len(stored)),
        }


def load_claim_rows_checked(
    db_path: Path, run_id: str
) -> list[tuple[str, int]]:
    """Read per-claim support for a run.

    Reports are not deduplicated across runs, so this join is safe; only
    source records are shared, which is why retrieval keys come from the run
    result instead of the database.
    """

    with connect_database(db_path) as conn:
        return load_claim_rows(conn, run_id)
