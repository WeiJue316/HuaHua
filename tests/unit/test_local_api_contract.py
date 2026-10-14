from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[2] / "docs" / "local-api.md"


def test_local_api_contract_covers_the_viewer_resources() -> None:
    text = CONTRACT.read_text(encoding="utf-8")

    for endpoint in (
        "GET /v1/runs",
        "GET /v1/runs/{run_id}/steps",
        "GET /v1/runs/{run_id}/sources",
        "GET /v1/runs/{run_id}/papers",
        "GET /v1/runs/{run_id}/claims",
        "GET /v1/evidence-spans/{evidence_span_id}",
        "GET /v1/source-records/{source_record_id}",
        "GET /v1/files/{file_id}",
        "GET /v1/documents/{document_id}",
    ):
        assert endpoint in text
    for field_name in (
        "api_version",
        "claim_text",
        "support_status",
        "evidence_level",
        "source_record_id",
        "text_path",
    ):
        assert f"`{field_name}`" in text
    assert '"code": "not_found"' in text
    assert '"limit": 20' in text
    assert "127.0.0.1" in text
    assert "C:\\" not in text
    assert "/Users/" not in text
