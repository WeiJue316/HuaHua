from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _step_body(workflow: str, name: str) -> str:
    marker = f"- name: {name}\n"
    body = workflow.split(marker, 1)[1]
    return body.split("\n      - name:", 1)[0]


def test_lint_step_runs_ruff_check_and_is_not_called_formatting() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    local = (ROOT / "scripts" / "check_all.py").read_text(encoding="utf-8")

    assert "Check formatting" not in workflow
    assert "Check formatting" not in local
    assert "uv run ruff check ." in _step_body(workflow, "Lint")
    assert '("Lint", ["ruff", "check", "."])' in local


def test_typecheck_covers_source_and_scripts() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    local = (ROOT / "scripts" / "check_all.py").read_text(encoding="utf-8")

    assert "uv run mypy src scripts" in _step_body(workflow, "Type check")
    assert '("Type check", ["mypy", "src", "scripts"])' in local


def test_ci_checks_the_web_app() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    local = (ROOT / "scripts" / "check_all.py").read_text(encoding="utf-8")

    assert "actions/setup-node@v4" in workflow
    assert "node-version-file: web/.nvmrc" in workflow
    assert "uv run python scripts/check_web.py" in _step_body(workflow, "Check web")
    assert '("Check web", ["python", "scripts/check_web.py"])' in local
