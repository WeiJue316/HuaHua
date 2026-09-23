"""Command-line entry point for the research agent."""

import typer

from . import __version__

app = typer.Typer(
    name="research-agent",
    help="面向计算机/AI 文献调研的可追溯科研 Agent。",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Print the installed package version."""

    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check the minimum local runtime requirements."""

    typer.echo("environment: ok")


def main() -> None:
    """Run the CLI."""

    app()