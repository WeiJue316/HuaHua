from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_web  # noqa: E402


def test_check_web_skips_when_node_is_missing(monkeypatch, capsys) -> None:
    monkeypatch.setattr(check_web.shutil, "which", lambda _name: None)

    assert check_web.main() == 0
    assert "WEB_CHECKS_SKIPPED" in capsys.readouterr().out
