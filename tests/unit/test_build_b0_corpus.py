from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_b0_corpus import extract_papers  # noqa: E402


def test_extract_papers_reads_openalex_search_response() -> None:
    payload = json.loads(
        (ROOT / "tests" / "fixtures" / "openalex_search.json").read_text(
            encoding="utf-8"
        )
    )

    papers = extract_papers(payload)

    assert len(papers) == 1
    assert papers[0].doi == "10.1000/example"
    assert papers[0].title == "Traceable Retrieval for Scientific Agents"


def test_extract_papers_ignores_non_work_payloads() -> None:
    assert extract_papers({"meta": {"count": 0}, "results": []}) == []
    assert extract_papers({"error": "not found"}) == []