"""Command-line entry point for the research agent."""

import asyncio
from pathlib import Path
from typing import Annotated

import httpx
import typer

from . import __version__
from .evaluator.bm25 import Bm25Index
from .evaluator.case_runner import (
    SYSTEM_VERSION,
    CaseRunnerSettings,
    ResearchCaseRunner,
)
from .evaluator.dataset import dataset_version_from_path, load_questions
from .evaluator.runner import EvaluationRunner, EvaluationSummary
from .evaluator.systems import SYSTEMS
from .llm.deepseek import DeepSeekGateway
from .llm.gateway import ModelGatewayError
from .mcp_servers.cache import ResponseCache
from .planner.planner import ResearchPlan, plan_research
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


@app.command()
def version() -> None:
    """Print the installed package version."""

    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check the minimum local runtime requirements."""

    typer.echo("environment: ok")


@app.command()
def research(
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
    cache_dir: Annotated[
        Path | None,
        typer.Option(
            "--cache-dir",
            help="Reuse source responses from this directory.",
        ),
    ] = None,
) -> None:
    """Run the federated research flow and write a traceable report."""

    source_text = sources.strip().lower()
    plan: ResearchPlan
    if source_text == "auto":
        plan = plan_research(
            question,
            available_sources=SUPPORTED_SOURCES,
            max_results_per_source=max_results,
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

    async def run() -> ResearchRunResult:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            cache = ResponseCache(cache_dir) if cache_dir is not None else None
            clients = build_source_clients(http_client, source_ids, cache=cache)
            abstract_resolver = OpenAlexAbstractResolver(
                build_openalex_client(http_client)
            )
            judge = (
                RelevanceJudge(DeepSeekGateway(http_client=http_client))
                if relevance_filter
                else None
            )
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
                response_cache=cache,
            )

    try:
        result = asyncio.run(run())
    except ModelGatewayError as exc:
        typer.echo(
            f"relevance filter unavailable: {exc}\n"
            "Set DEEPSEEK_API_KEY, or pass --no-relevance-filter to run without it.",
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
    if result.relevance_skipped:
        typer.echo("relevance: skipped (--no-relevance-filter)")
    else:
        typer.echo(
            f"relevance: judged={result.relevance_judged} "
            f"dropped={result.relevance_dropped} "
            f"failures={result.relevance_failures}"
        )
    typer.echo(f"report: {result.report_path}")


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
        int,
        typer.Option(
            "--model-call-budget",
            min=1,
            max=200,
            help="Maximum system model calls for baseline-neutral task completion.",
        ),
    ] = 20,
) -> None:
    """Run an evaluation matrix over a frozen question set."""

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
    b0_index = None
    if "B0" in system_ids:
        if not b0_corpus.is_file():
            typer.echo(f"B0 corpus not found: {b0_corpus}", err=True)
            raise typer.Exit(code=1)
        b0_index = Bm25Index.from_jsonl(b0_corpus)

    async def run() -> EvaluationSummary:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            gateway = DeepSeekGateway(http_client=http_client)
            apply_migrations(db)
            case_runner = ResearchCaseRunner(
                questions=questions,
                settings=settings,
                http_client=http_client,
                gateway=gateway,
                cache=cache,
                b0_index=b0_index,
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
                        "cache_dir": cache_dir.as_posix(),
                        "b0_corpus": b0_corpus.as_posix(),
                        "b0_corpus_hash": (
                            b0_index.corpus_hash if b0_index is not None else None
                        ),
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


def main() -> None:
    """Run the CLI."""

    app()