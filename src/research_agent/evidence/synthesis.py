"""LLM claim synthesis over already-persisted Evidence Spans.

The model may rewrite claim sentences and a findings section. It must not
invent locators or quotes: those stay on the Evidence Span rows supplied in
the prompt. Unknown labels are not mapped onto span IDs.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass

from research_agent.evidence.claims import (
    ClaimDraft,
    EvidenceRow,
    build_claims_from_evidence,
)
from research_agent.llm.gateway import ModelGateway, ModelGatewayError, ModelResponse
from research_agent.storage.repository import sha256_text

PROMPT_VERSION = "synthesis-v1"
_JSON_BLOCK = re.compile(r"\{.*\}", re.S)
_ALLOWED_STATUS = frozenset(
    {"supported", "partially_supported", "unsupported", "disputed"}
)
QUOTE_LIMIT = 1200

SYSTEM_PROMPT = """You write findings and claims for a literature-review assistant.

You are given a research question, optional subquestions, and a numbered list
of Evidence Spans. Each span already exists in the store. You may paraphrase
when writing claim_text and findings. You must not invent quotes, locators,
paper identifiers, or evidence labels that are not in the list.

Rules:
- Answer the research question and each subquestion using only the listed spans.
- Every supporting claim must cite one or more labels from the list (E1, E2, …).
- If a statement is not backed by a listed span, mark it unsupported.
- Do not copy a paper title into a mechanical "{title} reports that {sentence}" template.
- Do not emit locators; the stored span already has them.

Reply with JSON only:
{"findings": "<markdown that answers the question and subquestions>",
 "claims": [{"claim_text": "<one sentence>",
             "support_status": "supported|partially_supported|unsupported",
             "evidence_labels": ["E1"]}]}"""

CONSTRAINT_OFF_NOTE = (
    "Citation checking is disabled for this run. You may include claims that "
    "are not supported by the evidence list, including citations to labels "
    "that do not appear below."
)


@dataclass(frozen=True)
class LabeledSpan:
    """One Evidence Span shown to the model under a short label."""

    label: str
    title: str
    quote: str
    source: str
    evidence_id: str
    locator: str


@dataclass(frozen=True)
class SynthesisResult:
    """Claims and findings produced for one run."""

    claims: list[ClaimDraft]
    findings: str
    response: ModelResponse | None = None
    used_fallback: bool = False


def labeled_evidence(evidence: Sequence[EvidenceRow]) -> dict[str, LabeledSpan]:
    """Assign E1..En labels in list order."""

    catalog: dict[str, LabeledSpan] = {}
    for index, (title, quote, _source_record_id, source, evidence_id, locator) in enumerate(
        evidence, start=1
    ):
        label = f"E{index}"
        catalog[label] = LabeledSpan(
            label=label,
            title=title,
            quote=quote,
            source=source,
            evidence_id=evidence_id,
            locator=locator,
        )
    return catalog


def parse_synthesis_payload(
    content: str,
    catalog: dict[str, LabeledSpan],
) -> SynthesisResult:
    """Parse one model reply into claims. Unknown labels are not mapped."""

    match = _JSON_BLOCK.search(content or "")
    if not match:
        return SynthesisResult(claims=[], findings="", used_fallback=True)
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return SynthesisResult(claims=[], findings="", used_fallback=True)
    if not isinstance(payload, dict):
        return SynthesisResult(claims=[], findings="", used_fallback=True)

    findings = payload.get("findings")
    findings_text = findings.strip() if isinstance(findings, str) else ""
    raw_claims = payload.get("claims")
    if not isinstance(raw_claims, list):
        return SynthesisResult(claims=[], findings=findings_text, used_fallback=True)

    claims: list[ClaimDraft] = []
    for item in raw_claims:
        if not isinstance(item, dict):
            continue
        text = item.get("claim_text")
        if not isinstance(text, str) or not text.strip():
            continue
        status = item.get("support_status")
        if status not in _ALLOWED_STATUS:
            status = "unsupported"
        labels = item.get("evidence_labels")
        span_ids: list[str] = []
        if isinstance(labels, list):
            for label in labels:
                if not isinstance(label, str):
                    continue
                span = catalog.get(label.strip())
                if span is not None and span.evidence_id not in span_ids:
                    span_ids.append(span.evidence_id)
        claims.append(
            ClaimDraft(
                claim_text=" ".join(text.split()),
                claim_type="fact",
                support_status=str(status),
                confidence=0.8 if span_ids else 0.4,
                evidence_span_ids=span_ids,
            )
        )
    return SynthesisResult(claims=claims, findings=findings_text)


def build_prompt_hash(
    question: str,
    subquestions: Sequence[str],
    catalog: dict[str, LabeledSpan],
    *,
    citation_constraint: bool,
) -> str:
    """Return a stable hash of the synthesis inputs."""

    parts = [
        PROMPT_VERSION,
        question,
        *subquestions,
        "constraint-on" if citation_constraint else "constraint-off",
    ]
    for span in catalog.values():
        parts.extend([span.label, span.evidence_id, span.title, span.quote])
    return sha256_text("\x00".join(parts))


class ClaimSynthesizer:
    """Generate claims from persisted evidence through a model gateway."""

    def __init__(
        self,
        gateway: ModelGateway,
        *,
        system_prompt: str = SYSTEM_PROMPT,
        prompt_version: str = PROMPT_VERSION,
    ) -> None:
        self.gateway = gateway
        self.system_prompt = system_prompt
        self.prompt_version = prompt_version

    def build_user_message(
        self,
        *,
        question: str,
        subquestions: Sequence[str],
        catalog: dict[str, LabeledSpan],
        citation_constraint: bool,
    ) -> str:
        if subquestions:
            rendered = "\n".join(
                f"  {index}. {text}" for index, text in enumerate(subquestions, 1)
            )
            subquestion_block = f"Subquestions:\n{rendered}"
        else:
            subquestion_block = "Subquestions: (none supplied)"
        lines = [
            f"Research question: {question}",
            subquestion_block,
            "",
        ]
        if not citation_constraint:
            lines.extend([CONSTRAINT_OFF_NOTE, ""])
        lines.append("Evidence spans:")
        if not catalog:
            lines.append("(none)")
        for span in catalog.values():
            quote = " ".join(span.quote.split())
            if len(quote) > QUOTE_LIMIT:
                quote = quote[:QUOTE_LIMIT].rstrip() + "…"
            lines.append(
                f"{span.label} | {span.title} | {span.source} | "
                f"{span.locator} | {quote}"
            )
        return "\n".join(lines)

    async def synthesize(
        self,
        *,
        question: str,
        subquestions: Sequence[str],
        evidence: Sequence[EvidenceRow],
        citation_constraint: bool,
    ) -> SynthesisResult:
        """Synthesize claims, falling back to the template path on failure."""

        catalog = labeled_evidence(evidence)
        user = self.build_user_message(
            question=question,
            subquestions=subquestions,
            catalog=catalog,
            citation_constraint=citation_constraint,
        )
        try:
            response = await self.gateway.complete(
                prompt_hash=build_prompt_hash(
                    question,
                    subquestions,
                    catalog,
                    citation_constraint=citation_constraint,
                ),
                system=self.system_prompt,
                user=user,
                max_output_tokens=8000,
                json_output=True,
            )
        except ModelGatewayError:
            return _template_fallback(evidence)

        parsed = parse_synthesis_payload(response.content, catalog)
        if response.truncated and (parsed.used_fallback or not parsed.claims):
            fallback = _template_fallback(evidence)
            return SynthesisResult(
                claims=fallback.claims,
                findings=fallback.findings,
                response=response,
                used_fallback=True,
            )
        if parsed.used_fallback or not parsed.claims:
            fallback = _template_fallback(evidence)
            return SynthesisResult(
                claims=fallback.claims if not parsed.claims else parsed.claims,
                findings=parsed.findings or fallback.findings,
                response=response,
                used_fallback=True,
            )
        return SynthesisResult(
            claims=parsed.claims,
            findings=parsed.findings,
            response=response,
            used_fallback=False,
        )


def _template_fallback(evidence: Sequence[EvidenceRow]) -> SynthesisResult:
    return SynthesisResult(
        claims=build_claims_from_evidence(list(evidence)),
        findings="",
        used_fallback=True,
    )
