from typer.testing import CliRunner

from research_agent import __version__
from research_agent.cli import app

runner = CliRunner()


def test_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "version" in result.stdout
    assert "doctor" in result.stdout


def test_help_is_ascii_safe() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    result.stdout.encode("ascii")


def test_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_doctor() -> None:
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "environment: ok" in result.stdout