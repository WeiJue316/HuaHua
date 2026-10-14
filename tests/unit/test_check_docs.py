from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from check_docs import check_directory_tree, directory_tree_files  # noqa: E402

TREE = """
## 4. 目录规范

```text
.
├── src/research_agent/
│   ├── cli.py
│   ├── missing_module.py
│   └── storage/
│       └── migrations/
│           └── NNNN_*.sql
├── docs/adr/
│   └── NNNN-kebab-case.md
└── web/                          # 尚未创建
    └── App.tsx
```
"""


def test_directory_tree_requires_listed_files_and_skips_placeholders(
    tmp_path: Path,
) -> None:
    package = tmp_path / "src" / "research_agent"
    package.mkdir(parents=True)
    (package / "cli.py").write_text("", encoding="utf-8")
    errors: list[str] = []

    check_directory_tree(errors, root=tmp_path, text=TREE)

    assert errors == ["missing tree file: src/research_agent/missing_module.py"]


def test_agents_directory_tree_files_exist() -> None:
    listed = directory_tree_files((ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    errors: list[str] = []

    check_directory_tree(errors, root=ROOT)

    assert "src/research_agent/cli.py" in listed
    assert "src/research_agent/doctor.py" in listed
    assert "src/research_agent/mcp_servers/dblp/server.py" in listed
    assert "web/package.json" in listed
    assert "web/src/App.tsx" in listed
    assert not any("NNNN" in path for path in listed)
    assert errors == []
