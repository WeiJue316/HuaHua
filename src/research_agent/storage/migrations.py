"""Versioned SQLite migration runner.

The runner is intentionally small and uses only the Python standard library.
Migrations are forward-only; rollback is performed by restoring the backup
created before a migration batch.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).with_name("migrations")
MIGRATION_PATTERN = re.compile(r"^(?P<version>\d{4})_(?P<name>.+)\.sql$")


class MigrationError(RuntimeError):
    """Raised when the migration history is unsafe or inconsistent."""


@dataclass(frozen=True)
class Migration:
    """One immutable SQL migration file."""

    version: int
    name: str
    path: Path
    sql: str
    sha256: str


@contextmanager
def connect_database(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Open a connection with the project's SQLite safety settings."""

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute("PRAGMA busy_timeout = 5000")
        yield connection
    finally:
        connection.close()


def get_schema_version(connection: sqlite3.Connection) -> int:
    """Return the current SQLite user_version value."""

    row = connection.execute("PRAGMA user_version").fetchone()
    if row is None:
        return 0
    return int(row[0])


def discover_migrations(migrations_dir: Path = MIGRATIONS_DIR) -> list[Migration]:
    """Load and validate migration files in ascending version order."""

    migrations_dir = Path(migrations_dir)
    if not migrations_dir.is_dir():
        raise MigrationError(f"migration directory does not exist: {migrations_dir}")

    migrations: list[Migration] = []
    for path in sorted(migrations_dir.glob("*.sql")):
        match = MIGRATION_PATTERN.match(path.name)
        if match is None:
            raise MigrationError(f"invalid migration filename: {path.name}")
        sql = path.read_text(encoding="utf-8")
        migrations.append(
            Migration(
                version=int(match.group("version")),
                name=match.group("name"),
                path=path,
                sql=sql,
                sha256=hashlib.sha256(sql.encode("utf-8")).hexdigest(),
            )
        )

    versions = [migration.version for migration in migrations]
    expected = list(range(1, len(migrations) + 1))
    if versions != expected:
        raise MigrationError(
            f"migration versions must be continuous from 0001: {versions}"
        )
    return migrations


def iter_sql_statements(sql: str) -> Iterator[str]:
    """Yield complete SQLite statements without breaking trigger bodies."""

    buffer = ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            statement = buffer.strip()
            if statement:
                yield statement
            buffer = ""
    if buffer.strip():
        raise MigrationError("migration contains an incomplete SQL statement")


def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {str(row[0]) for row in rows}


def _ensure_migration_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )


def _applied_migrations(connection: sqlite3.Connection) -> dict[int, sqlite3.Row]:
    rows = connection.execute(
        "SELECT version, name, sha256, applied_at FROM schema_migrations ORDER BY version"
    ).fetchall()
    return {int(row["version"]): row for row in rows}


def _backup_database(
    connection: sqlite3.Connection,
    db_path: Path,
    backup_dir: Path,
) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    backup_path = backup_dir / f"{timestamp}-{db_path.name}"
    with sqlite3.connect(backup_path) as backup_connection:
        connection.backup(backup_connection)
    return backup_path


def _validate_applied(
    applied: dict[int, sqlite3.Row],
    migrations_by_version: dict[int, Migration],
) -> None:
    for version, row in applied.items():
        migration = migrations_by_version.get(version)
        if migration is None:
            raise MigrationError(f"applied migration {version:04d} is missing from disk")
        if migration.sha256 != str(row["sha256"]):
            raise MigrationError(
                f"migration {version:04d} hash mismatch: "
                f"database={row['sha256']} file={migration.sha256}"
            )


def apply_migrations(
    db_path: Path,
    migrations_dir: Path = MIGRATIONS_DIR,
    backup_dir: Path | None = None,
) -> int:
    """Apply all pending migrations and return the resulting schema version."""

    db_path = Path(db_path)
    migrations = discover_migrations(migrations_dir)
    migrations_by_version = {migration.version: migration for migration in migrations}
    had_existing_database = db_path.exists() and db_path.stat().st_size > 0

    with connect_database(db_path) as connection:
        existing_tables = _table_names(connection)
        _ensure_migration_table(connection)
        applied = _applied_migrations(connection)
        _validate_applied(applied, migrations_by_version)

        unversioned_tables = existing_tables - {"schema_migrations"}
        if unversioned_tables and not applied:
            raise MigrationError(
                "refusing to adopt unversioned non-empty database: "
                f"{sorted(unversioned_tables)}"
            )

        pending = [
            migration
            for migration in migrations
            if migration.version not in applied
        ]
        if not pending:
            return get_schema_version(connection)

        if had_existing_database:
            target_backup_dir = backup_dir or db_path.parent / "backups"
            _backup_database(connection, db_path, target_backup_dir)

        for migration in pending:
            try:
                connection.execute("BEGIN IMMEDIATE")
                for statement in iter_sql_statements(migration.sql):
                    connection.execute(statement)
                foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
                if foreign_key_errors:
                    raise MigrationError(
                        f"foreign key check failed after {migration.version:04d}: "
                        f"{foreign_key_errors}"
                    )
                integrity_row = connection.execute("PRAGMA integrity_check").fetchone()
                if integrity_row is None or str(integrity_row[0]) != "ok":
                    raise MigrationError(
                        f"integrity check failed after {migration.version:04d}"
                    )
                connection.execute(
                    """
                    INSERT INTO schema_migrations (version, name, sha256, applied_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        migration.version,
                        migration.name,
                        migration.sha256,
                        datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    ),
                )
                connection.execute(f"PRAGMA user_version = {migration.version}")
                connection.commit()
            except Exception as exc:
                connection.rollback()
                if isinstance(exc, MigrationError):
                    raise
                raise MigrationError(
                    f"migration {migration.version:04d} failed: {exc}"
                ) from exc

        return get_schema_version(connection)


def reset_for_tests(db_path: Path) -> None:
    """Delete a test database and its SQLite sidecar files."""

    for suffix in ("", "-wal", "-shm"):
        candidate = Path(f"{db_path}{suffix}")
        if candidate.exists():
            candidate.unlink()


__all__ = [
    "MIGRATIONS_DIR",
    "Migration",
    "MigrationError",
    "apply_migrations",
    "connect_database",
    "discover_migrations",
    "get_schema_version",
    "iter_sql_statements",
    "reset_for_tests",
]