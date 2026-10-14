from pathlib import Path

from research_agent.doctor import collect_doctor_checks, doctor_exit_code


def test_doctor_checks_python_directories_and_migrations(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"

    checks = collect_doctor_checks(
        data_dir=data_dir,
        reports_dir=reports_dir,
        version_info=(3, 12),
        environ={},
    )
    by_name = {check.name: check for check in checks}

    assert by_name["python"].ok is True
    assert by_name["python"].detail == "ok 3.12"
    assert by_name["data"].ok is True
    assert by_name["reports"].ok is True
    assert data_dir.is_dir()
    assert reports_dir.is_dir()
    assert not (data_dir / ".doctor-write-probe").exists()
    assert not (reports_dir / ".doctor-write-probe").exists()
    assert by_name["migrations"].ok is True
    assert by_name["migrations"].detail.startswith("ok ")
    assert int(by_name["migrations"].detail.removeprefix("ok ")) >= 1
    assert doctor_exit_code(checks) == 0


def test_doctor_rejects_python_older_than_3_12(tmp_path: Path) -> None:
    checks = collect_doctor_checks(
        data_dir=tmp_path / "data",
        reports_dir=tmp_path / "reports",
        version_info=(3, 11),
        environ={},
    )

    python = next(check for check in checks if check.name == "python")
    assert python.ok is False
    assert python.detail == "failed 3.11 requires 3.12 or newer"
    assert doctor_exit_code(checks) == 1


def test_doctor_reports_an_unwritable_directory(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.write_text("blocked", encoding="utf-8")

    checks = collect_doctor_checks(
        data_dir=data_dir,
        reports_dir=tmp_path / "reports",
        version_info=(3, 12),
        environ={},
    )
    data = next(check for check in checks if check.name == "data")
    reports = next(check for check in checks if check.name == "reports")

    assert data.ok is False
    assert data.detail == "failed FileExistsError"
    assert reports.ok is True
    assert doctor_exit_code(checks) == 1


def test_doctor_reports_migration_failure(tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "not-a-migration.sql").write_text("SELECT 1;", encoding="utf-8")

    checks = collect_doctor_checks(
        data_dir=tmp_path / "data",
        reports_dir=tmp_path / "reports",
        version_info=(3, 12),
        environ={},
        migrations_dir=migrations_dir,
    )
    migrations = next(check for check in checks if check.name == "migrations")

    assert migrations.ok is False
    assert "not-a-migration.sql" in migrations.detail
    assert doctor_exit_code(checks) == 1


def test_doctor_reports_optional_environment_without_values(tmp_path: Path) -> None:
    secret = "super-secret-token"
    checks = collect_doctor_checks(
        data_dir=tmp_path / "data",
        reports_dir=tmp_path / "reports",
        version_info=(3, 12),
        environ={
            "DEEPSEEK_API_KEY": secret,
            "OPENALEX_API_KEY": "   ",
            "RESEARCH_AGENT_CONTACT": "",
        },
    )
    rendered = "\n".join(f"{check.name}: {check.detail}" for check in checks)
    by_name = {check.name: check for check in checks}

    assert secret not in rendered
    assert by_name["DEEPSEEK_API_KEY"].detail == "set"
    assert by_name["OPENALEX_API_KEY"].detail == "unset"
    assert by_name["RESEARCH_AGENT_CONTACT"].detail == "unset"
    assert by_name["SEMANTIC_SCHOLAR_API_KEY"].detail == "unset"
    assert all(
        by_name[name].ok
        for name in (
            "DEEPSEEK_API_KEY",
            "OPENALEX_API_KEY",
            "RESEARCH_AGENT_CONTACT",
            "SEMANTIC_SCHOLAR_API_KEY",
        )
    )
    assert doctor_exit_code(checks) == 0
