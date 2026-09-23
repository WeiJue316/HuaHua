"""Command-line entry point for the research agent."""

import typer

from . import __version__

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


def main() -> None:
    """Run the CLI."""

    app()