from __future__ import annotations

from pathlib import Path

import pytest

from research_agent.paths import project_root, resolve_project_path, stored_project_path


def test_relative_paths_stay_under_the_project_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    root = project_root()

    assert (root / "pyproject.toml").is_file()
    assert resolve_project_path(Path("data/research_agent.db")) == (
        root / "data" / "research_agent.db"
    )
    assert resolve_project_path(Path("reports")) == root / "reports"
    absolute = tmp_path / "elsewhere.db"
    assert resolve_project_path(absolute) == absolute


def test_arxiv_artifact_dir_stays_under_the_project_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from research_agent.mcp_servers.arxiv.server import artifact_directory

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("RESEARCH_AGENT_ARTIFACT_DIR", raising=False)
    root = project_root()

    assert artifact_directory() == root / "data" / "cache" / "downloads"

    monkeypatch.setenv("RESEARCH_AGENT_ARTIFACT_DIR", "custom/downloads")
    assert artifact_directory() == root / "custom" / "downloads"

    monkeypatch.setenv("RESEARCH_AGENT_ARTIFACT_DIR", str(tmp_path / "abs"))
    assert artifact_directory() == tmp_path / "abs"


def test_stored_project_path_keeps_outside_and_empty_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.setattr("research_agent.paths.project_root", lambda: root)

    inside = root / "reports" / "run" / "report.md"
    outside = tmp_path / "elsewhere" / "report.md"

    assert stored_project_path(inside) == "reports/run/report.md"
    assert stored_project_path(outside.as_posix()) == outside.resolve().as_posix()
    assert stored_project_path("") == ""
    assert stored_project_path("reports/run/report.md") == "reports/run/report.md"
