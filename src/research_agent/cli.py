"""Command-line entry point for the research agent."""

import asyncio
from pathlib import Path
from typing import Annotated

import httpx
import typer

from . import __version__
from .mcp_servers.arxiv.client import ArxivClient
from .mcp_servers.openalex.client import OpenAlexClient
from .router.federation import SearchClient
from .runtime.research_service import ResearchRunResult, run_federated_research

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
            help="Comma-separated source IDs: arxiv, openalex.",
        ),
    ] = "arxiv,openalex",
    download_pdf: Annotated[
        bool,
        typer.Option(
            "--download-pdf",
            help="Archive open arXiv PDFs and record File provenance.",
        ),
    ] = False,
) -> None:
    """Run the federated research flow and write a traceable report."""

    source_ids = [item.strip().lower() for item in sources.split(",") if item.strip()]
    supported = {"arxiv", "openalex"}
    unsupported = sorted(set(source_ids) - supported)
    if not source_ids:
        raise typer.BadParameter("at least one source is required")
    if unsupported:
        raise typer.BadParameter(f"unsupported sources: {', '.join(unsupported)}")

    async def run() -> ResearchRunResult:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            clients: dict[str, SearchClient] = {}
            if "arxiv" in source_ids:
                clients["arxiv"] = ArxivClient(http_client=http_client)
            if "openalex" in source_ids:
                clients["openalex"] = OpenAlexClient(http_client=http_client)
            return await run_federated_research(
                question=question,
                db_path=db,
                reports_root=reports_dir,
                clients=clients,
                max_results_per_source=max_results,
                download_pdf=download_pdf,
            )

    result = asyncio.run(run())
    summary = ", ".join(
        f"{source}={count}" for source, count in sorted(result.source_counts.items())
    )
    typer.echo(f"run_id: {result.run_id}")
    typer.echo(f"sources: {summary}")
    typer.echo(f"papers: {result.paper_count}")
    typer.echo(f"evidence: {result.evidence_count}")
    typer.echo(f"claims: {result.claim_count}")
    typer.echo(f"files: {result.file_count}")
    typer.echo(f"documents: {result.document_count}")
    typer.echo(f"report: {result.report_path}")


def main() -> None:
    """Run the CLI."""

    app()