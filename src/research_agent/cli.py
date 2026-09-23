"""Command-line entry point for the research agent."""

import asyncio
from pathlib import Path
from typing import Annotated

import httpx
import typer

from . import __version__
from .llm.deepseek import DeepSeekGateway
from .llm.gateway import ModelGatewayError
from .planner.planner import ResearchPlan, plan_research
from .policy.relevance import RelevanceJudge
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
            clients = build_source_clients(http_client, source_ids)
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


def main() -> None:
    """Run the CLI."""

    app()