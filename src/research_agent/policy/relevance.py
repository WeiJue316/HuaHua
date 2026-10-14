"""Semantic relevance judgement for search candidates.

Keyword overlap can tell whether a paper is topically adjacent; it cannot tell
whether the paper bears on the question. Human review of the pilot dataset
showed the difference is not cosmetic: a chip-design paper, a speech dataset and
a biomedical retriever were all retrieved for questions they cannot answer.

This module applies two independent judgements, because the pilot experiment
showed a single scale conflates them:

- ``domain_scope`` separates papers from an unrelated field. On the pilot
  sample this axis was exact: every off-topic paper was flagged, no on-topic
  paper was.
- ``answer_role`` records whether the paper answers the question directly,
  supports it, or contributes nothing. This is a matter of degree, so it does
  not by itself remove a candidate.

A missing abstract is treated as its own case, never as evidence of
irrelevance: some sources publish metadata only, and rejecting those papers
would silently drop valid work.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from research_agent.identity import primary_identity
from research_agent.llm.gateway import ModelGateway, ModelGatewayError, ModelResponse
from research_agent.mcp_servers.common import PaperCandidate

PROMPT_VERSION = "relevance-v1"
BATCH_PROMPT_VERSION = "relevance-batch-v1"
RELEVANCE_BATCH_SIZE = 8
THRESHOLD_LOOSE = "loose"
THRESHOLD_STRICT = "strict"

DOMAIN_IN_SCOPE = "in_scope"
DOMAIN_OUT_OF_SCOPE = "out_of_scope"
DOMAIN_UNKNOWN = "unknown"

ROLE_DIRECT = "direct"
ROLE_SUPPORTING = "supporting"
ROLE_NONE = "none"
ROLE_UNKNOWN = "unknown"

SYSTEM_PROMPT = """You screen academic papers for a literature-review assistant.

You are given one research question, its subquestions, and one candidate
paper. Judge the paper on two independent axes and report the availability of
its abstract.

The paper may legitimately bear on a single subquestion without answering the
whole research question; judge against the subquestions as a set.

domain_scope:
- "in_scope": the paper belongs to the field the subquestion comes from.
- "out_of_scope": the paper belongs to a different field.
- "unknown": you cannot tell from the material provided.

answer_role:
- "direct": the abstract states evidence that answers the subquestion.
- "supporting": the abstract offers related evidence that helps answer the
  subquestion without answering it outright.
- "none": the abstract offers no evidence for this subquestion.
- "unknown": you cannot tell from the material provided.

Rules:
- Judge from the title and abstract only. Never infer content from the title.
- Read the whole abstract, including its final sentences.
- If the abstract contains no research content (for example it lists only
  authors and a publication venue), set abstract_available to false and both
  axes to "unknown". Do not treat missing text as evidence of irrelevance.

Reply with JSON only:
{"abstract_available": true, "domain_scope": "in_scope|out_of_scope|unknown",
 "answer_role": "direct|supporting|none|unknown", "reason": "<one short sentence>"}"""

BATCH_SYSTEM_PROMPT = """You screen academic papers for a literature-review assistant.

You are given one research question, its subquestions, and several candidate
papers. Judge each paper on two independent axes and report whether its
abstract is available. Use the same rules for every paper.

domain_scope:
- "in_scope": the paper belongs to the field the subquestion comes from.
- "out_of_scope": the paper belongs to a different field.
- "unknown": you cannot tell from the material provided.

answer_role:
- "direct": the abstract states evidence that answers the subquestion.
- "supporting": the abstract offers related evidence that helps answer the
  subquestion without answering it outright.
- "none": the abstract offers no evidence for this subquestion.
- "unknown": you cannot tell from the material provided.

Rules:
- Judge from the title and abstract only. Never infer content from the title.
- Read the whole abstract, including its final sentences.
- If the abstract contains no research content, set abstract_available to false
  and both axes to "unknown".
- paper_index is the number given with that candidate. Return every paper once.

Reply with a JSON array only:
[{"paper_index": 1, "abstract_available": true,
  "domain_scope": "in_scope|out_of_scope|unknown",
  "answer_role": "direct|supporting|none|unknown",
  "reason": "<one short sentence>"}]"""

_JSON_BLOCK = re.compile(r"\{.*\}", re.S)
_JSON_ARRAY = re.compile(r"\[.*\]", re.S)


def build_prompt_hash(
    question: str,
    subquestions: Sequence[str],
    paper: PaperCandidate,
) -> str:
    """Return a stable hash of the judgement inputs."""

    from research_agent.storage.repository import sha256_text

    return sha256_text(
        "\x00".join(
            [
                PROMPT_VERSION,
                question,
                *subquestions,
                paper.source,
                paper.source_record_id,
                paper.title,
                paper.abstract or "",
            ]
        )
    )


@dataclass(frozen=True)
class RelevanceVerdict:
    """The outcome of judging one candidate against one subquestion."""

    paper_key: str
    domain_scope: str
    answer_role: str
    abstract_available: bool
    reason: str
    failed: bool = False

    @property
    def keep(self) -> bool:
        """Whether the candidate stays in the candidate set.

        Fails open: a judgement that could not be made, or a paper whose
        abstract the source does not publish, must never be dropped on that
        basis alone. Only a paper positively placed in another field is
        removed. This is the loose threshold.
        """

        return kept_under(self, THRESHOLD_LOOSE)


def kept_under(verdict: RelevanceVerdict, threshold: str) -> bool:
    """Apply the loose or strict keep rule. Both fail open.

    Loose keeps every in-scope paper, including supporting evidence that does
    not answer the question outright. Strict keeps only a direct answer.
    """

    if threshold not in {THRESHOLD_LOOSE, THRESHOLD_STRICT}:
        raise ValueError(f"unknown relevance threshold: {threshold}")
    if verdict.failed or not verdict.abstract_available:
        return True
    if verdict.domain_scope == DOMAIN_OUT_OF_SCOPE:
        return False
    if threshold == THRESHOLD_STRICT:
        return verdict.answer_role == ROLE_DIRECT
    return True


def parse_verdict(paper_key: str, content: str) -> RelevanceVerdict:
    """Parse one model reply, tolerating prose around the JSON object."""

    match = _JSON_BLOCK.search(content or "")
    if not match:
        return RelevanceVerdict(
            paper_key=paper_key,
            domain_scope=DOMAIN_UNKNOWN,
            answer_role=ROLE_UNKNOWN,
            abstract_available=True,
            reason="model reply contained no JSON object",
            failed=True,
        )
    try:
        payload: Any = json.loads(match.group(0))
    except json.JSONDecodeError:
        return RelevanceVerdict(
            paper_key=paper_key,
            domain_scope=DOMAIN_UNKNOWN,
            answer_role=ROLE_UNKNOWN,
            abstract_available=True,
            reason="model reply was not valid JSON",
            failed=True,
        )
    if not isinstance(payload, dict):
        return RelevanceVerdict(
            paper_key=paper_key,
            domain_scope=DOMAIN_UNKNOWN,
            answer_role=ROLE_UNKNOWN,
            abstract_available=True,
            reason="model reply was not a JSON object",
            failed=True,
        )

    available = payload.get("abstract_available")
    if not isinstance(available, bool):
        available = True
    domain = payload.get("domain_scope")
    role = payload.get("answer_role")
    reason = payload.get("reason")
    return RelevanceVerdict(
        paper_key=paper_key,
        domain_scope=str(domain)
        if domain in {DOMAIN_IN_SCOPE, DOMAIN_OUT_OF_SCOPE, DOMAIN_UNKNOWN}
        else DOMAIN_UNKNOWN,
        answer_role=str(role)
        if role in {ROLE_DIRECT, ROLE_SUPPORTING, ROLE_NONE, ROLE_UNKNOWN}
        else ROLE_UNKNOWN,
        abstract_available=available,
        reason=str(reason) if isinstance(reason, str) else "",
    )


def parse_batch_verdicts(
    papers: Sequence[PaperCandidate],
    content: str,
) -> list[RelevanceVerdict]:
    """Align a JSON array of judgements with the papers in one batch."""

    def failed(paper: PaperCandidate, reason: str) -> RelevanceVerdict:
        return RelevanceVerdict(
            paper_key=paper_key(paper),
            domain_scope=DOMAIN_UNKNOWN,
            answer_role=ROLE_UNKNOWN,
            abstract_available=bool(paper.abstract),
            reason=reason,
            failed=True,
        )

    match = _JSON_ARRAY.search(content or "")
    payload: Any = None
    if match:
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            payload = None
    by_index: dict[int, RelevanceVerdict] = {}
    if isinstance(payload, list):
        for item in payload:
            if not isinstance(item, dict):
                continue
            index = item.get("paper_index")
            if isinstance(index, bool) or not isinstance(index, int):
                continue
            if index < 1 or index > len(papers) or index in by_index:
                continue
            by_index[index] = parse_verdict(paper_key(papers[index - 1]), json.dumps(item))
    verdicts: list[RelevanceVerdict] = []
    for index, paper in enumerate(papers, start=1):
        verdicts.append(
            by_index.get(index)
            or failed(paper, "model reply omitted this paper")
        )
    if not isinstance(payload, list):
        return [failed(paper, "model reply contained no JSON array") for paper in papers]
    return verdicts


class RelevanceJudge:
    """Judge candidates with a model gateway."""

    def __init__(
        self,
        gateway: ModelGateway,
        *,
        system_prompt: str = SYSTEM_PROMPT,
        prompt_version: str = PROMPT_VERSION,
        batch_prompt_version: str = BATCH_PROMPT_VERSION,
        batch_size: int = RELEVANCE_BATCH_SIZE,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        self.gateway = gateway
        self.system_prompt = system_prompt
        self.prompt_version = prompt_version
        self.batch_prompt_version = batch_prompt_version
        self.batch_size = batch_size

    def build_user_message(
        self,
        *,
        question: str,
        subquestions: Sequence[str],
        paper: PaperCandidate,
    ) -> str:
        abstract = paper.abstract or "(the source provides no abstract)"
        if subquestions:
            rendered = "\n".join(
                f"  {index}. {text}" for index, text in enumerate(subquestions, 1)
            )
            subquestion_block = f"Subquestions:\n{rendered}"
        else:
            subquestion_block = (
                "Subquestions: (none supplied; judge against the research question)"
            )
        return (
            f"Research question: {question}\n"
            f"{subquestion_block}\n\n"
            f"Candidate paper\n"
            f"Title: {paper.title}\n"
            f"Year: {paper.year if paper.year is not None else 'unknown'}\n"
            f"Abstract: {abstract}"
        )

    async def judge(
        self,
        *,
        question: str,
        subquestions: Sequence[str],
        paper: PaperCandidate,
    ) -> tuple[RelevanceVerdict, ModelResponse | None]:
        """Judge one paper, returning the verdict and the raw call metadata."""

        key = paper_key(paper)
        user = self.build_user_message(
            question=question, subquestions=subquestions, paper=paper
        )
        try:
            response = await self.gateway.complete(
                prompt_hash=build_prompt_hash(question, subquestions, paper),
                system=self.system_prompt,
                user=user,
                json_output=True,
            )
        except ModelGatewayError as exc:
            return (
                RelevanceVerdict(
                    paper_key=key,
                    domain_scope=DOMAIN_UNKNOWN,
                    answer_role=ROLE_UNKNOWN,
                    abstract_available=bool(paper.abstract),
                    reason=f"model call failed: {exc}",
                    failed=True,
                ),
                None,
            )

        if response.truncated:
            return (
                RelevanceVerdict(
                    paper_key=key,
                    domain_scope=DOMAIN_UNKNOWN,
                    answer_role=ROLE_UNKNOWN,
                    abstract_available=bool(paper.abstract),
                    reason="model ran out of output budget before answering",
                    failed=True,
                ),
                response,
            )
        return parse_verdict(key, response.content), response

    def build_batch_user_message(
        self,
        *,
        question: str,
        subquestions: Sequence[str],
        papers: Sequence[PaperCandidate],
    ) -> str:
        blocks = [
            self.build_user_message(
                question=question, subquestions=subquestions, paper=paper
            )
            for paper in papers
        ]
        numbered = []
        for index, block in enumerate(blocks, start=1):
            body = block.split("\n\nCandidate paper\n", 1)[-1]
            numbered.append(f"Paper index: {index}\n{body}")
        header = blocks[0].split("\n\nCandidate paper\n", 1)[0]
        return header + "\n\n" + "\n\n".join(numbered)

    async def judge_batch(
        self,
        *,
        question: str,
        subquestions: Sequence[str],
        papers: Sequence[PaperCandidate],
    ) -> list[tuple[list[RelevanceVerdict], ModelResponse | None]]:
        """Judge papers in chunks. Each chunk is one model call."""

        batch: list[tuple[list[RelevanceVerdict], ModelResponse | None]] = []
        pending = list(papers)
        while pending:
            chunk = pending[: self.batch_size]
            pending = pending[self.batch_size :]
            batch.append(
                await self._judge_chunk(
                    question=question, subquestions=subquestions, papers=chunk
                )
            )
        return batch

    async def _judge_chunk(
        self,
        *,
        question: str,
        subquestions: Sequence[str],
        papers: Sequence[PaperCandidate],
    ) -> tuple[list[RelevanceVerdict], ModelResponse | None]:
        user = self.build_batch_user_message(
            question=question, subquestions=subquestions, papers=papers
        )
        prompt_hash = build_batch_prompt_hash(question, subquestions, papers)

        def failed(reason: str) -> list[RelevanceVerdict]:
            return [
                RelevanceVerdict(
                    paper_key=paper_key(paper),
                    domain_scope=DOMAIN_UNKNOWN,
                    answer_role=ROLE_UNKNOWN,
                    abstract_available=bool(paper.abstract),
                    reason=reason,
                    failed=True,
                )
                for paper in papers
            ]

        try:
            response = await self.gateway.complete(
                prompt_hash=prompt_hash,
                system=BATCH_SYSTEM_PROMPT,
                user=user,
                max_output_tokens=900 * len(papers),
                json_output=True,
            )
        except ModelGatewayError as exc:
            return failed(f"model call failed: {exc}"), None
        if response.truncated:
            return failed("model ran out of output budget before answering"), response
        return parse_batch_verdicts(papers, response.content), response


def build_batch_prompt_hash(
    question: str,
    subquestions: Sequence[str],
    papers: Sequence[PaperCandidate],
) -> str:
    """Return a stable hash of one batch judgement."""

    from research_agent.storage.repository import sha256_text

    parts = [BATCH_PROMPT_VERSION, question, *subquestions]
    for paper in papers:
        parts.extend(
            [paper.source, paper.source_record_id, paper.title, paper.abstract or ""]
        )
    return sha256_text("\x00".join(parts))


def paper_key(paper: PaperCandidate) -> str:
    """Stable identifier used in verdicts and audit records."""

    return primary_identity(paper)