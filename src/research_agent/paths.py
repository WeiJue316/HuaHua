"""Project-root path resolution.

Configuration paths are relative to the repository root, not the process
working directory. Absolute configuration paths are left unchanged. New
database rows store a path under the project as a relative POSIX path.
"""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the directory that contains this project's pyproject.toml."""

    start = Path(__file__).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise RuntimeError("could not find the project root from the installed package")


def resolve_project_path(path: Path) -> Path:
    """Resolve a configured path against the project root."""

    if path.is_absolute():
        return path
    return project_root() / path


def stored_project_path(path: str | Path) -> str:
    """Return a project-relative POSIX path for a new database row.

    Paths outside the project stay absolute. An empty path stays empty.
    """

    text = path.as_posix() if isinstance(path, Path) else path
    if text == "":
        return ""
    candidate = Path(text)
    if not candidate.is_absolute():
        return candidate.as_posix()
    resolved = candidate.resolve()
    try:
        return resolved.relative_to(project_root()).as_posix()
    except ValueError:
        return resolved.as_posix()
