"""Command-line entry point for the research agent."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import httpx
import typer

from . import __version__
from .doctor import collect_doctor_checks, doctor_exit_code
from .evaluator.bm25 import Bm25Index
from .evaluator.case_runner import (
    SYSTEM_VERSION,
    CaseRunnerSettings,
    ResearchCaseRunner,
)
from .evaluator.dataset import dataset_version_from_path, load_questions
from .evaluator.runner import (
    EvaluationRunner,
    EvaluationSummary,
    evaluation_exit_code,
)
from .evaluator.snapshot import SourceSnapshot
from .evaluator.systems import SYSTEMS
from .evidence.synthesis import ClaimSynthesizer
from .interfaces.app import LOCAL_API_HOSTS, serve_local_api
from .llm.deepseek import DeepSeekGateway, api_key_from_environment
from .llm.gateway import ModelGatewayError
from .mcp_servers.cache import ResponseCache
from .paths import project_root, resolve_project_path
from .planner.planner import ROUTING_BUDGET, ResearchPlan, plan_research
from .policy.relevance import RelevanceJudge
from .router.federation import search_sources
from .router.registry import (
    SUPPORTED_SOURCES,
    build_openalex_client,
    build_source_clients,
)
from .runtime.enrichment import OpenAlexAbstractResolver
from .runtime.research_service import (
    ResearchExecutionError,
    ResearchRunResult,
    run_federated_research,
)
from .storage.evaluation_repository import EvaluationRepository
from .storage.migrations import apply_migrations, connect_database

app = typer.Typer(
    name="research-agent",
    help="Traceable research agent for computer science and AI literature.",
    no_args_is_help=True,
    rich_markup_mode=None,
)


@dataclass(frozen=True)
class _ResearchModelUse:
    """How one research command should use the model provider."""

    relevance_filter: bool
    synthesis: bool
    relevance_notice: str | None = None
    error: str | None = None


def _option_was_explicit(ctx: typer.Context, name: str) -> bool:
    source = ctx.get_parameter_source(name)
    return source is not None and source.name != "DEFAULT"


def _research_model_use(
    *,
    relevance_filter: bool,
    relevance_filter_explicit: bool,
    synthesis: bool,
    api_key_present: bool,
) -> _ResearchModelUse:
    """Skip the default relevance filter when no model key is configured."""

    if api_key_present:
        return _ResearchModelUse(relevance_filter, synthesis)
    requested: list[str] = []
    if relevance_filter and relevance_filter_explicit:
        requested.append("--relevance-filter")
    if synthesis:
        requested.append("--synthesis")
    if requested:
        requested_text = " or ".join(requested)
        return _ResearchModelUse(
            relevance_filter,
            synthesis,
            error=(
                "DEEPSEEK_API_KEY is not set. "
                f"Set it before using {requested_text}."
            ),
        )
    if relevance_filter:
        return _ResearchModelUse(
            False,
            False,
            relevance_notice="relevance: skipped (DEEPSEEK_API_KEY is not set)",
        )
    return _ResearchModelUse(False, synthesis)


@app.command()
def version() -> None:
    """Print the installed package version."""

    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check Python, writable directories, migrations, and optional variables."""

    root = project_root()
    checks = collect_doctor_checks(
        data_dir=root / "data",
        reports_dir=root / "reports",
    )
    for check in checks:
        typer.echo(f"{check.name}: {check.detail}")
    exit_code = doctor_exit_code(checks)
    if exit_code:
        raise typer.Exit(code=exit_code)


@app.command()
def research(
    ctx: typer.Context,
    question: Annotated[
        str,
        typer.Argument(help="Research question to investigate."),
    ],
    db: Annotated[
        Path,
        typer.Option("--db", help="SQLite database path."),
    ] = Path("data/research_agent.db"),
    reports_dir: Annotated[
        Path,
        typer.Option("--reports-dir", help="Directory for generated reports."),
    ] = Path("reports"),
    max_results: Annotated[
        int,
        typer.Option(
            "--max-results",
            min=1,
            max=200,
            help="Maximum results per source.",
        ),
    ] = 10,
    sources: Annotated[
        str,
        typer.Option(
            "--sources",
            help="auto, or comma-separated source IDs.",
        ),
    ] = "auto",
    download_pdf: Annotated[
        bool,
        typer.Option(
            "--download-pdf",
            help="Archive open arXiv PDFs and record File provenance.",
        ),
    ] = False,
    relevance_filter: Annotated[
        bool,
        typer.Option(
            "--relevance-filter/--no-relevance-filter",
            help="Judge candidate relevance with a language model before claims.",
        ),
    ] = True,
    relevance_threshold: Annotated[
        str,
        typer.Option(
            "--relevance-threshold",
            help="loose keeps in-scope papers; strict keeps only direct answers.",
        ),
    ] = "loose",
    synthesis: Annotated[
        bool,
        typer.Option(
            "--synthesis/--no-synthesis",
            help="Write claims with the model from stored evidence spans.",
        ),
    ] = False,
    cache_dir: Annotated[
        Path | None,
        typer.Option(
            "--cache-dir",
            help="Reuse source responses from this directory.",
        ),
    ] = None,
) -> None:
    """Run the federated research flow and write a traceable report."""

    db = resolve_project_path(db)
    reports_dir = resolve_project_path(reports_dir)
    if cache_dir is not None:
        cache_dir = resolve_project_path(cache_dir)

    source_text = sources.strip().lower()
    plan: ResearchPlan
    if source_text == "auto":
        plan = plan_research(
            question,
            available_sources=SUPPORTED_SOURCES,
            max_results_per_source=max_results,
            max_sources=ROUTING_BUDGET,
        )
        source_ids = list(plan.selected_sources)
    else:
        source_ids = [
            item.strip().lower() for item in source_text.split(",") if item.strip()
        ]
        supported = set(SUPPORTED_SOURCES)
        unsupported = sorted(set(source_ids) - supported)
        if not source_ids:
            raise typer.BadParameter("at least one source is required")
        if unsupported:
            raise typer.BadParameter(f"unsupported sources: {', '.join(unsupported)}")
        plan = plan_research(
            question,
            available_sources=tuple(source_ids),
            max_results_per_source=max_results,
            max_sources=len(source_ids),
        )
    if relevance_threshold not in {"loose", "strict"}:
        raise typer.BadParameter("relevance threshold must be loose or strict")
    model_use = _research_model_use(
        relevance_filter=relevance_filter,
        relevance_filter_explicit=_option_was_explicit(ctx, "relevance_filter"),
        synthesis=synthesis,
        api_key_present=api_key_from_environment() is not None,
    )
    if model_use.error is not None:
        typer.echo(model_use.error, err=True)
        raise typer.Exit(code=1)
    relevance_filter = model_use.relevance_filter
    synthesis = model_use.synthesis

    async def run() -> ResearchRunResult:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            cache = ResponseCache(cache_dir) if cache_dir is not None else None
            clients = build_source_clients(http_client, source_ids, cache=cache)
            abstract_resolver = OpenAlexAbstractResolver(
                build_openalex_client(http_client)
            )
            gateway = (
                DeepSeekGateway(http_client=http_client)
                if relevance_filter or synthesis
                else None
            )
            judge = RelevanceJudge(gateway) if relevance_filter and gateway else None
            synthesizer = ClaimSynthesizer(gateway) if synthesis and gateway else None
            return await run_federated_research(
                question=question,
                db_path=db,
                reports_root=reports_dir,
                clients=clients,
                max_results_per_source=max_results,
                download_pdf=download_pdf,
                plan=plan,
                abstract_resolver=abstract_resolver,
                relevance_judge=judge,
                claim_synthesizer=synthesizer,
                response_cache=cache,
                relevance_threshold=relevance_threshold,
            )

    try:
        result = asyncio.run(run())
    except ModelGatewayError as exc:
        typer.echo(
            f"model provider unavailable: {exc}\n"
            "Set DEEPSEEK_API_KEY, or pass --no-relevance-filter --no-synthesis.",
            err=True,
        )
        raise typer.Exit(code=1) from exc
    except ResearchExecutionError as exc:
        typer.echo(f"research run failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    summary = ", ".join(
        f"{source}={count}" for source, count in sorted(result.source_counts.items())
    )
    typer.echo(f"run_id: {result.run_id}")
    typer.echo(f"sources: {summary}")
    if result.source_errors:
        errors = "; ".join(
            f"{source}: {message}"
            for source, message in sorted(result.source_errors.items())
        )
        typer.echo(f"source_errors: {errors}")
    if result.variant_errors:
        variant_errors = "; ".join(
            f"{source}: {message}"
            for source, message in sorted(result.variant_errors.items())
        )
        typer.echo(f"variant_errors: {variant_errors}")
    typer.echo(f"papers: {result.paper_count}")
    typer.echo(f"evidence: {result.evidence_count}")
    typer.echo(f"claims: {result.claim_count}")
    typer.echo(f"files: {result.file_count}")
    typer.echo(f"documents: {result.document_count}")
    if model_use.relevance_notice is not None:
        typer.echo(model_use.relevance_notice)
    elif result.relevance_skipped:
        typer.echo("relevance: skipped (--no-relevance-filter)")
    else:
        typer.echo(
            f"relevance: judged={result.relevance_judged} "
            f"dropped={result.relevance_dropped} "
            f"failures={result.relevance_failures}"
        )
    typer.echo(f"report: {result.report_path}")
    for label, filename in (
        ("evidence_json", "evidence.json"),
        ("evidence_csv", "evidence.csv"),
        ("bibtex", "references.bib"),
    ):
        export_path = result.report_path.with_name(filename)
        if export_path.is_file():
            typer.echo(f"{label}: {export_path}")


@app.command()
def evaluate(
    dataset: Annotated[
        Path,
        typer.Option("--dataset", help="Frozen JSONL question set."),
    ] = Path("evaluation/datasets/pilot_questions.v2.jsonl"),
    systems: Annotated[
        str,
        typer.Option("--systems", help="Comma-separated system identifiers."),
    ] = "B3,A6",
    sources: Annotated[
        str,
        typer.Option(
            "--sources",
            help="Comma-separated source allowlist, or 'all'.",
        ),
    ] = "all",
    repeats: Annotated[
        int,
        typer.Option("--repeats", min=1, max=10, help="Runs per question."),
    ] = 1,
    db: Annotated[
        Path,
        typer.Option("--db", help="SQLite database for runs and results."),
    ] = Path("data/research_agent.db"),
    reports_dir: Annotated[
        Path,
        typer.Option("--reports-dir", help="Directory for generated reports."),
    ] = Path("reports/evaluation"),
    max_results: Annotated[
        int,
        typer.Option("--max-results", min=1, max=200),
    ] = 10,
    cache_dir: Annotated[
        Path,
        typer.Option(
            "--cache-dir",
            help="Frozen response cache shared by every system.",
        ),
    ] = Path("data/cache/http"),
    b0_corpus: Annotated[
        Path,
        typer.Option("--b0-corpus", help="Frozen JSONL corpus for the BM25 baseline."),
    ] = Path("evaluation/corpora/pilot_v2_b0.jsonl"),
    model_call_budget: Annotated[
        int | None,
        typer.Option(
            "--model-call-budget",
            min=1,
            max=500,
            help="Override the estimated model-call budget. Omit to use the formula.",
        ),
    ] = None,
    source_snapshot: Annotated[
        Path | None,
        typer.Option(
            "--source-snapshot",
            help="Frozen JSONL source snapshot for controlled comparisons.",
        ),
    ] = None,
) -> None:
    """Run an evaluation matrix over a frozen question set."""

    dataset = resolve_project_path(dataset)
    db = resolve_project_path(db)
    reports_dir = resolve_project_path(reports_dir)
    cache_dir = resolve_project_path(cache_dir)
    b0_corpus = resolve_project_path(b0_corpus)
    if source_snapshot is not None:
        source_snapshot = resolve_project_path(source_snapshot)

    if not dataset.is_file():
        typer.echo(f"dataset not found: {dataset}", err=True)
        raise typer.Exit(code=1)
    questions = load_questions(dataset)
    system_ids = [item.strip() for item in systems.split(",") if item.strip()]
    unknown = [item for item in system_ids if item not in SYSTEMS]
    if unknown:
        typer.echo(f"unknown systems: {', '.join(unknown)}", err=True)
        raise typer.Exit(code=1)

    allowed_sources: tuple[str, ...] | None
    if sources.strip().lower() == "all":
        allowed_sources = None
    else:
        allowed_sources = tuple(
            item.strip() for item in sources.split(",") if item.strip()
        )
        if not allowed_sources:
            typer.echo("--sources must name at least one source or be 'all'", err=True)
            raise typer.Exit(code=1)
        unknown_sources = [
            source for source in allowed_sources if source not in SUPPORTED_SOURCES
        ]
        if unknown_sources:
            typer.echo(
                f"unknown sources: {', '.join(unknown_sources)}",
                err=True,
            )
            raise typer.Exit(code=1)

    settings = CaseRunnerSettings(
        db_path=db,
        reports_root=reports_dir,
        max_results_per_source=max_results,
        dataset_version=dataset_version_from_path(dataset),
        allowed_sources=allowed_sources,
        model_call_budget=model_call_budget,
    )
    # Evaluation never lets an entry expire: the same key must always return
    # the same bytes, or the arms are not comparable.
    cache = ResponseCache(cache_dir, ttl_seconds=None)
    snapshot = None
    if source_snapshot is not None:
        if not source_snapshot.is_file():
            typer.echo(f"source snapshot not found: {source_snapshot}", err=True)
            raise typer.Exit(code=1)
        snapshot = SourceSnapshot.from_jsonl(source_snapshot)

    b0_index = None
    if "B0" in system_ids:
        if not b0_corpus.is_file():
            typer.echo(f"B0 corpus not found: {b0_corpus}", err=True)
            raise typer.Exit(code=1)
        b0_index = Bm25Index.from_jsonl(b0_corpus)

    needs_model = any(SYSTEMS[system_id].needs_model for system_id in system_ids)

    async def run() -> EvaluationSummary:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            gateway = DeepSeekGateway(http_client=http_client) if needs_model else None
            apply_migrations(db)
            case_runner = ResearchCaseRunner(
                questions=questions,
                settings=settings,
                http_client=http_client,
                gateway=gateway,
                cache=cache,
                b0_index=b0_index,
                source_snapshot=snapshot,
            )
            with connect_database(db) as conn:
                runner = EvaluationRunner(EvaluationRepository(conn))
                return await runner.run(
                    questions=questions,
                    systems=system_ids,
                    repeats=repeats,
                    run_case=case_runner,
                    dataset_version=settings.dataset_version,
                    system_version=SYSTEM_VERSION,
                    config={
                        "systems": system_ids,
                        "repeats": repeats,
                        "max_results_per_source": max_results,
                        "allowed_sources": allowed_sources,
                        "model_call_budget": model_call_budget,
                        "model_call_budget_rule": (
                            "k * sources when relevance filtering is on, "
                            "plus 1 when synthesis is on, "
                            "plus 8 * 2 for the ReAct baseline, otherwise 1"
                        ),
                        "cache_dir": cache_dir.as_posix(),
                        "b0_corpus": b0_corpus.as_posix(),
                        "b0_corpus_hash": (
                            b0_index.corpus_hash if b0_index is not None else None
                        ),
                        "source_snapshot": (
                            source_snapshot.as_posix() if source_snapshot else None
                        ),
                        "source_snapshot_hash": (
                            snapshot.snapshot_hash if snapshot is not None else None
                        ),
                        "claim_synthesis": "synthesis-v1",
                    },
                )

    try:
        summary = asyncio.run(run())
    except ModelGatewayError as exc:
        typer.echo(f"evaluation needs a model provider: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"evaluation_run_id: {summary.evaluation_run_id}")
    typer.echo(f"status: {summary.status}")
    typer.echo(
        f"cases: {summary.case_count} completed={summary.completed_count} "
        f"failed={summary.failed_count}"
    )
    typer.echo(f"cache_entries: {cache.entry_count()}")
    typer.echo(f"cache_hash: {cache.directory_hash()}")
    if evaluation_exit_code(summary):
        raise typer.Exit(code=1)


@app.command()
def warm_cache(
    dataset: Annotated[
        Path,
        typer.Option("--dataset", help="Frozen JSONL question set."),
    ] = Path("evaluation/datasets/pilot_questions.v2.jsonl"),
    cache_dir: Annotated[
        Path,
        typer.Option("--cache-dir", help="Directory to fill with responses."),
    ] = Path("data/cache/http"),
    sources: Annotated[
        str,
        typer.Option("--sources", help="comma-separated source IDs, or 'all'."),
    ] = "all",
    max_results: Annotated[
        int,
        typer.Option("--max-results", min=1, max=200),
    ] = 10,
) -> None:
    """Fill the response cache so every evaluation arm sees identical input."""

    dataset = resolve_project_path(dataset)
    cache_dir = resolve_project_path(cache_dir)

    if not dataset.is_file():
        typer.echo(f"dataset not found: {dataset}", err=True)
        raise typer.Exit(code=1)
    questions = load_questions(dataset)
    source_ids = (
        list(SUPPORTED_SOURCES)
        if sources.strip().lower() == "all"
        else [item.strip() for item in sources.split(",") if item.strip()]
    )
    unsupported = sorted(set(source_ids) - set(SUPPORTED_SOURCES))
    if unsupported:
        typer.echo(f"unsupported sources: {', '.join(unsupported)}", err=True)
        raise typer.Exit(code=1)

    # no TTL: the cache is frozen after this command and must not expire
    cache = ResponseCache(cache_dir, ttl_seconds=None)

    async def fill() -> None:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            clients = build_source_clients(http_client, source_ids, cache=cache)
            for question in questions:
                plan = plan_research(
                    question.question,
                    available_sources=tuple(source_ids),
                    max_results_per_source=max_results,
                    max_sources=len(source_ids),
                )
                await search_sources(
                    {source: clients[source] for source in plan.selected_sources},
                    query=question.question,
                    query_variants=plan.query_variants,
                    max_results_per_source=max_results,
                    max_concurrency=plan.max_concurrency,
                )

    asyncio.run(fill())
    typer.echo(f"cache_entries: {cache.entry_count()}")
    typer.echo(f"cache_hash: {cache.directory_hash()}")
    typer.echo(f"hits={cache.stats.hits} misses={cache.stats.misses}")


@app.command()
def serve(
    db: Annotated[
        Path,
        typer.Option("--db", help="SQLite database path."),
    ] = Path("data/research_agent.db"),
    host: Annotated[
        str,
        typer.Option("--host", help="Bind address. Must stay on this machine."),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", min=1, max=65535),
    ] = 8765,
) -> None:
    """Serve the local read-only evidence API."""

    if host not in LOCAL_API_HOSTS:
        raise typer.BadParameter("API host must stay on the local machine")
    serve_local_api(resolve_project_path(db), host=host, port=port)


def main() -> None:
    """Run the CLI."""

    app()