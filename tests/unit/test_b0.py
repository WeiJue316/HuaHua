from __future__ import annotations

from pathlib import Path

import pytest

from research_agent.evaluator.b0 import B0Baseline
from research_agent.evaluator.bm25 import Bm25Document, Bm25Index
from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.llm.gateway import ModelGatewayError, ModelResponse


class StubSummaryGateway:
    def __init__(self, *, truncated: bool = False) -> None:
        self.truncated = truncated
        self.calls: list[tuple[str, str, int]] = []

    async def complete(
        self,
        *,
        prompt_hash: str,
        system: str,
        user: str,
        max_output_tokens: int = 900,
        temperature: float = 0.0,
        json_output: bool = False,
    ) -> ModelResponse:
        del system, temperature, json_output
        self.calls.append((prompt_hash, user, max_output_tokens))
        return ModelResponse(
            provider="stub",
            model="stub-summary",
            content="" if self.truncated else "A concise baseline report.",
            prompt_hash=prompt_hash,
            response_hash="stub",
            input_tokens=120,
            output_tokens=30,
            latency_ms=25,
            finish_reason="length" if self.truncated else "stop",
        )


def _question() -> EvaluationQuestion:
    return EvaluationQuestion(
        question_id="csai_test",
        question="How does dense retrieval compare with sparse retrieval?",
        subquestions=("What are the trade-offs?",),
        gold_papers=("doi:gold",),
    )


def _index() -> Bm25Index:
    return Bm25Index(
        [
            Bm25Document(
                paper_key="doi:gold",
                title="Dense and sparse retrieval trade-offs",
                abstract="We compare dense retrieval with sparse BM25 retrieval.",
            ),
            Bm25Document(
                paper_key="doi:other",
                title="Vision language alignment",
                abstract="A multimodal model.",
            ),
        ]
    )


@pytest.mark.asyncio
async def test_b0_writes_one_report_and_records_cost(tmp_path: Path) -> None:
    gateway = StubSummaryGateway()
    baseline = B0Baseline(
        index=_index(),
        gateway=gateway,
        reports_root=tmp_path / "reports",
        top_k=1,
    )

    result = await baseline.run(_question(), run_number=2)

    assert result.retrieved_keys == frozenset({"doi:gold"})
    assert len(gateway.calls) == 1
    assert "Dense and sparse retrieval trade-offs" in gateway.calls[0][1]
    assert result.input_tokens == 120
    assert result.output_tokens == 30
    assert result.latency_ms == 25
    assert result.report_path.is_file()
    assert "A concise baseline report." in result.report_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_b0_rejects_a_truncated_summary(tmp_path: Path) -> None:
    baseline = B0Baseline(
        index=_index(),
        gateway=StubSummaryGateway(truncated=True),
        reports_root=tmp_path / "reports",
        top_k=1,
    )

    with pytest.raises(ModelGatewayError, match="truncated"):
        await baseline.run(_question(), run_number=1)