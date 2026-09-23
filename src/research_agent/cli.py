"""Command-line entry point for the research agent."""

import asyncio
from pathlib import Path
from typing import Annotated

import httpx
import typer

from . import __version__
from .mcp_servers.arxiv.client import ArxivClient, ArxivClientError
from .runtime.research_service import ResearchRunResult, run_arxiv_research

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
            help="Maximum number of arXiv results.",
        ),
    ] = 10,
) -> None:
    """Run the M1 arXiv research flow and write a traceable report."""

    async def run() -> ResearchRunResult:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            client = ArxivClient(http_client=http_client)
            return await run_arxiv_research(
                question=question,
                db_path=db,
                reports_root=reports_dir,
                client=client,
                max_results=max_results,
            )

    try:
        result = asyncio.run(run())
    except ArxivClientError as exc:
        typer.echo(f"arXiv request failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"run_id: {result.run_id}")
    typer.echo(f"papers: {result.paper_count}")
    typer.echo(f"evidence: {result.evidence_count}")
    typer.echo(f"report: {result.report_path}")


def main() -> None:
    """Run the CLI."""

    app()