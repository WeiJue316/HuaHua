from pathlib import Path

import pytest
from typer.testing import CliRunner

from research_agent import __version__
from research_agent.cli import app
from research_agent.doctor import DoctorCheck
from research_agent.runtime.research_service import ResearchRunResult

runner = CliRunner()


def test_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "version" in result.stdout
    assert "doctor" in result.stdout
    assert "research" in result.stdout


def test_help_is_ascii_safe() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    result.stdout.encode("ascii")


def test_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_doctor_reports_checks_without_printing_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "super-secret-token"
    monkeypatch.setenv("DEEPSEEK_API_KEY", secret)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "python: ok" in result.stdout
    assert "data: ok" in result.stdout
    assert "reports: ok" in result.stdout
    assert "migrations: ok" in result.stdout
    assert "DEEPSEEK_API_KEY: set" in result.stdout
    assert secret not in result.stdout
    assert secret not in (result.stderr or "")


def test_doctor_exits_when_a_required_check_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "research_agent.cli.collect_doctor_checks",
        lambda **_kwargs: (
            DoctorCheck("python", False, "failed 3.11 requires 3.12 or newer"),
        ),
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 1
    assert "python: failed 3.11 requires 3.12 or newer" in result.stdout

def test_research_help_lists_sources() -> None:
    result = runner.invoke(app, ["research", "--help"])

    assert result.exit_code == 0
    assert "--sources" in result.stdout
    assert "--download-pdf" in result.stdout

def test_only_a6_can_run_without_a_model() -> None:
    from research_agent.evaluator.systems import SYSTEMS

    assert SYSTEMS["A6"].needs_model is False
    assert SYSTEMS["B0"].needs_model is True
    assert SYSTEMS["B2"].needs_model is True
    assert SYSTEMS["B3"].needs_model is True


def test_evaluate_help_lists_source_allowlist() -> None:
    result = runner.invoke(app, ["evaluate", "--help"])

    assert result.exit_code == 0
    assert "--sources" in result.stdout
    assert "--source-snapshot" in result.stdout
    result = runner.invoke(app, ["evaluate", "--help"])

    assert result.exit_code == 0
    assert "--sources" in result.stdout


def _research_result(tmp_path: Path, *, skipped: bool) -> ResearchRunResult:
    return ResearchRunResult(
        run_id="run-1",
        report_path=tmp_path / "report.md",
        paper_count=0,
        evidence_count=0,
        claim_count=0,
        file_count=0,
        document_count=0,
        source_counts={},
        source_errors={},
        variant_errors={},
        relevance_skipped=skipped,
    )


def _invoke_research(tmp_path: Path, *extra: str):
    return runner.invoke(
        app,
        [
            "research",
            "evidence chain",
            "--sources",
            "arxiv",
            "--db",
            str(tmp_path / "research.db"),
            "--reports-dir",
            str(tmp_path / "reports"),
            *extra,
        ],
    )


def test_research_without_an_api_key_skips_relevance_and_says_so(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    seen: list[object] = []

    async def fake_run(**kwargs: object) -> ResearchRunResult:
        seen.append(kwargs["relevance_judge"])
        return _research_result(tmp_path, skipped=True)

    monkeypatch.setattr("research_agent.cli.run_federated_research", fake_run)

    result = _invoke_research(tmp_path)
    output = f"{result.stdout}\n{result.stderr or ''}"

    assert result.exit_code == 0
    assert seen == [None]
    assert "relevance: skipped (DEEPSEEK_API_KEY is not set)" in output
    assert "model provider unavailable" not in output


def test_blank_api_key_skips_relevance_the_same_way(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "   ")
    seen: list[object] = []

    async def fake_run(**kwargs: object) -> ResearchRunResult:
        seen.append(kwargs["relevance_judge"])
        return _research_result(tmp_path, skipped=True)

    monkeypatch.setattr("research_agent.cli.run_federated_research", fake_run)

    result = _invoke_research(tmp_path)
    output = f"{result.stdout}\n{result.stderr or ''}"

    assert result.exit_code == 0
    assert seen == [None]
    assert "relevance: skipped (DEEPSEEK_API_KEY is not set)" in output


def test_explicit_relevance_filter_without_an_api_key_stops_before_the_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    called = False

    async def fake_run(**_kwargs: object) -> ResearchRunResult:
        nonlocal called
        called = True
        return _research_result(tmp_path, skipped=False)

    monkeypatch.setattr("research_agent.cli.run_federated_research", fake_run)

    result = _invoke_research(tmp_path, "--relevance-filter")
    output = f"{result.stdout}\n{result.stderr or ''}"

    assert result.exit_code == 1
    assert called is False
    assert "DEEPSEEK_API_KEY is not set" in output
    assert "--relevance-filter" in output
    assert "model provider unavailable" not in output


def test_synthesis_without_an_api_key_stops_before_the_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    called = False

    async def fake_run(**_kwargs: object) -> ResearchRunResult:
        nonlocal called
        called = True
        return _research_result(tmp_path, skipped=True)

    monkeypatch.setattr("research_agent.cli.run_federated_research", fake_run)

    result = _invoke_research(tmp_path, "--no-relevance-filter", "--synthesis")
    output = f"{result.stdout}\n{result.stderr or ''}"

    assert result.exit_code == 1
    assert called is False
    assert "DEEPSEEK_API_KEY is not set" in output
    assert "--synthesis" in output
    assert "model provider unavailable" not in output


def test_research_keeps_the_relevance_filter_when_the_api_key_is_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "test-key-not-a-real-secret"
    monkeypatch.setenv("DEEPSEEK_API_KEY", secret)
    seen: list[object] = []

    async def fake_run(**kwargs: object) -> ResearchRunResult:
        seen.append(kwargs["relevance_judge"])
        return _research_result(tmp_path, skipped=False)

    monkeypatch.setattr("research_agent.cli.run_federated_research", fake_run)

    result = _invoke_research(tmp_path)
    output = f"{result.stdout}\n{result.stderr or ''}"

    assert result.exit_code == 0
    assert seen[0] is not None
    assert "relevance: judged=0" in output
    assert secret not in output