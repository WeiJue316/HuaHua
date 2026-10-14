"""Local runtime checks for the doctor command.

Migrations run against a temporary database. Existing project databases are
left untouched. Environment values are never included in check details.
"""

from __future__ import annotations

import os
import sys
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from research_agent.storage.migrations import (
    MIGRATIONS_DIR,
    MigrationError,
    apply_migrations,
)

MINIMUM_PYTHON = (3, 12)
OPTIONAL_ENVIRONMENT_VARIABLES = (
    "DEEPSEEK_API_KEY",
    "OPENALEX_API_KEY",
    "RESEARCH_AGENT_CONTACT",
    "SEMANTIC_SCHOLAR_API_KEY",
)
_PROBE_NAME = ".doctor-write-probe"


@dataclass(frozen=True)
class DoctorCheck:
    """One doctor result. ``detail`` must not contain secret values."""

    name: str
    ok: bool
    detail: str


def doctor_exit_code(checks: tuple[DoctorCheck, ...]) -> int:
    """Return 0 when every check passed."""

    return 0 if all(check.ok for check in checks) else 1


def collect_doctor_checks(
    *,
    data_dir: Path,
    reports_dir: Path,
    version_info: tuple[int, int] | None = None,
    environ: Mapping[str, str] | None = None,
    migrations_dir: Path | None = None,
) -> tuple[DoctorCheck, ...]:
    """Check the Python version, directories, migrations, and optional variables."""

    version = (
        version_info
        if version_info is not None
        else (sys.version_info[0], sys.version_info[1])
    )
    environment: Mapping[str, str] = os.environ if environ is None else environ
    return (
        _python_check(version),
        _directory_check("data", data_dir),
        _directory_check("reports", reports_dir),
        _migration_check(migrations_dir or MIGRATIONS_DIR),
        *_environment_checks(environment),
    )


def _python_check(version: tuple[int, int]) -> DoctorCheck:
    label = f"{version[0]}.{version[1]}"
    required = f"{MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}"
    if version >= MINIMUM_PYTHON:
        return DoctorCheck("python", True, f"ok {label}")
    return DoctorCheck("python", False, f"failed {label} requires {required} or newer")


def _directory_check(name: str, path: Path) -> DoctorCheck:
    probe = path / _PROBE_NAME
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return DoctorCheck(name, False, f"failed {type(exc).__name__}")
    return DoctorCheck(name, True, "ok")


def _migration_check(migrations_dir: Path) -> DoctorCheck:
    try:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directory:
            version = apply_migrations(Path(directory) / "doctor.db", migrations_dir)
    except MigrationError as exc:
        return DoctorCheck("migrations", False, f"failed {exc}")
    except OSError as exc:
        return DoctorCheck("migrations", False, f"failed {type(exc).__name__}")
    if version < 1:
        return DoctorCheck("migrations", False, "failed no migrations")
    return DoctorCheck("migrations", True, f"ok {version}")


def _environment_checks(environment: Mapping[str, str]) -> tuple[DoctorCheck, ...]:
    checks: list[DoctorCheck] = []
    for name in OPTIONAL_ENVIRONMENT_VARIABLES:
        present = bool(environment.get(name, "").strip())
        checks.append(DoctorCheck(name, True, "set" if present else "unset"))
    return tuple(checks)
