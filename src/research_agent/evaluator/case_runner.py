"""Adapt the research pipeline to the evaluation runner's callback contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import httpx

from research_agent.evaluator.b0 import B0Baseline
from research_agent.evaluator.bm25 import Bm25Index
from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.evaluator.metrics import (
    ModelUsage,
    evidence_metrics,
    load_claim_rows,
    load_model_usage,
    retrieval_metrics,
    source_coverage,
)
from research_agent.evaluator.react import PureReActBaseline
from research_agent.evaluator.runner import EvaluationCaseOutcome
from research_agent.evaluator.snapshot import SourceSnapshot
from research_agent.evaluator.systems import (
    SystemConfig,
    get_system,
    restrict_sources,
)
from research_agent.evaluator.task_completion import TaskCompletionJudge
from research_agent.evidence.synthesis import ClaimSynthesizer
from research_agent.llm.gateway import ModelGateway
from research_agent.mcp_servers.cache import ResponseCache
from research_agent.planner.planner import ResearchPlan, plan_research
from research_agent.policy.relevance import RelevanceJudge
from research_agent.router.federation import SearchClient
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
    enable_task_completion_judge: bool = True
    model_call_budget: int = 20


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
        source_snapshot: SourceSnapshot | None = None,
    ) -> None:
        self.questions = {question.question_id: question for question in questions}
        self.settings = settings
        self.http_client = http_client
        self.gateway = gateway
        self.cache = cache
        self.b0_index = b0_index
        self.source_snapshot = source_snapshot
        self.task_judge = (
            TaskCompletionJudge(
                gateway=gateway,
                model_call_budget=settings.model_call_budget,
            )
            if settings.enable_task_completion_judge and gateway is not None
            else None
        )

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

        clients = self._build_clients(source_ids)
        if system_id == "A2":
            plan = ResearchPlan(
                question=question.question,
                query_variants=(question.question,),
                selected_sources=tuple(source_ids),
                fallback_sources=(),
                max_results_per_source=self.settings.max_results_per_source,
                max_concurrency=len(source_ids),
                reason="A2_fixed_pipeline",
            )
        else:
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
        synthesizer = None
        if system_id != "A1" and self.gateway is not None:
            synthesizer = ClaimSynthesizer(self.gateway)

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
            evidence_chain=system_id != "A1",
            claim_synthesizer=synthesizer,
            citation_constraint=config.citation_constraint,
        )

        usage = load_model_usage_checked(self.settings.db_path, result.run_id)
        task_metrics = await self._task_completion_metrics(
            question=question,
            report_text=result.report_path.read_text(encoding="utf-8"),
            model_calls_used=usage.calls,
        )
        metrics = self._metrics(question, result, usage, task_metrics)
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
        task_metrics = await self._task_completion_metrics(
            question=question,
            report_text=outcome.report,
            model_calls_used=1,
        )
        retrieval = retrieval_metrics(
            retrieved_keys=set(outcome.retrieved_keys),
            gold_keys=set(question.gold_papers),
            ranked_keys=outcome.ranked_keys,
            k=self.settings.max_results_per_source,
        )
        return EvaluationCaseOutcome(
            metrics={
                **retrieval.to_dict(),
                "llm_calls": 1.0,
                "input_tokens": float(outcome.input_tokens or 0),
                "output_tokens": float(outcome.output_tokens or 0),
                "latency_ms": float(outcome.latency_ms or 0),
                "model_latency_ms": float(outcome.latency_ms or 0),
                "report_written": 1.0,
                "report_chars": float(len(outcome.report)),
                **task_metrics,
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
        clients = self._build_clients(source_ids)
        baseline = PureReActBaseline(
            clients=clients,
            gateway=self.gateway,
            reports_root=self.settings.reports_root,
            max_steps=8,
            max_results_per_search=self.settings.max_results_per_source,
        )
        outcome = await baseline.run(question, run_number=run_number)
        task_metrics = await self._task_completion_metrics(
            question=question,
            report_text=outcome.report,
            model_calls_used=outcome.model_calls,
        )
        retrieval = retrieval_metrics(
            retrieved_keys=set(outcome.retrieved_keys),
            gold_keys=set(question.gold_papers),
            ranked_keys=outcome.ranked_keys,
            k=self.settings.max_results_per_source,
        )
        return EvaluationCaseOutcome(
            metrics={
                **retrieval.to_dict(),
                "llm_calls": float(outcome.model_calls),
                "input_tokens": float(outcome.input_tokens),
                "output_tokens": float(outcome.output_tokens),
                "latency_ms": float(outcome.latency_ms),
                "model_latency_ms": float(outcome.latency_ms),
                "steps_used": float(outcome.steps_used),
                "search_calls": float(outcome.search_calls),
                "source_attempts": float(outcome.source_attempts),
                "source_successes": float(outcome.source_successes),
                "source_failures": float(outcome.source_failures),
                "source_success_rate": (
                    outcome.source_successes / outcome.source_attempts
                    if outcome.source_attempts
                    else 0.0
                ),
                "report_written": 1.0,
                "report_chars": float(len(outcome.report)),
                **task_metrics,
            }
        )

    async def _task_completion_metrics(
        self,
        *,
        question: EvaluationQuestion,
        report_text: str,
        model_calls_used: int,
    ) -> dict[str, float]:
        if self.task_judge is None:
            return {}
        result = await self.task_judge.evaluate(
            question=question,
            report_text=report_text,
            model_calls_used=model_calls_used,
        )
        return result.to_dict()

    def _build_clients(
        self,
        source_ids: tuple[str, ...],
    ) -> Mapping[str, SearchClient]:
        if self.source_snapshot is not None:
            return self.source_snapshot.clients_for(source_ids)
        return build_source_clients(self.http_client, source_ids, cache=self.cache)

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
        self,
        question: EvaluationQuestion,
        result: ResearchRunResult,
        usage: ModelUsage,
        task_metrics: dict[str, float],
    ) -> dict[str, float]:
        stored = set(result.retrieved_paper_keys)
        kept = stored - set(result.dropped_paper_keys)
        claims = load_claim_rows_checked(self.settings.db_path, result.run_id)
        contributing = {
            source for source, count in result.source_counts.items() if count > 0
        }

        dropped = set(result.dropped_paper_keys)
        ranked = [key for key in result.retrieved_paper_keys if key not in dropped]
        alias_map = dict(result.paper_aliases)
        extra_aliases = {
            alias
            for key in kept
            for alias in alias_map.get(key, ())
        }
        retrieval = retrieval_metrics(
            retrieved_keys=kept,
            gold_keys=set(question.gold_papers),
            extra_aliases=extra_aliases,
            ranked_keys=ranked,
            k=self.settings.max_results_per_source,
        )
        evidence = evidence_metrics(claims)
        coverage = source_coverage(
            contributing_sources=contributing,
            allowed_sources=set(result.source_counts),
        )
        source_attempts = len(result.source_counts)
        source_failures = len(result.source_errors)
        source_successes = source_attempts - source_failures
        source_success_rate = (
            source_successes / source_attempts if source_attempts else 0.0
        )
        return {
            **retrieval.to_dict(),
            **evidence.to_dict(),
            "source_coverage": coverage,
            "relevance_dropped": float(result.relevance_dropped),
            "relevance_failures": float(result.relevance_failures),
            **usage.to_dict(),
            "source_attempts": float(source_attempts),
            "source_successes": float(source_successes),
            "source_failures": float(source_failures),
            "source_success_rate": source_success_rate,
            **task_metrics,
            "retrieved_paper_count": float(result.paper_count),
            "stored_paper_count": float(len(stored)),
        }


def load_model_usage_checked(
    db_path: Path,
    run_id: str,
) -> ModelUsage:
    """Read model usage for a full-system run."""

    with connect_database(db_path) as conn:
        return load_model_usage(conn, run_id)


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
