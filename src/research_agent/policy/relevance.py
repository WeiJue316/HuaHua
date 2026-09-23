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

from research_agent.llm.gateway import ModelGateway, ModelGatewayError, ModelResponse
from research_agent.mcp_servers.common import PaperCandidate

PROMPT_VERSION = "relevance-v1"

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

_JSON_BLOCK = re.compile(r"\{.*\}", re.S)


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
        removed.
        """

        if self.failed or not self.abstract_available:
            return True
        return self.domain_scope != DOMAIN_OUT_OF_SCOPE


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


class RelevanceJudge:
    """Judge candidates with a model gateway."""

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


def paper_key(paper: PaperCandidate) -> str:
    """Stable identifier used in verdicts and audit records."""

    if paper.doi:
        return f"doi:{paper.doi}"
    return f"{paper.source}:{paper.source_record_id}"