"""Provider-neutral contract for large language model calls.

Semantic steps depend only on this protocol. Concrete providers live in their
own modules and are injected by the runtime, so adding or replacing a model
never touches policy, planner or evidence code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ModelGatewayError(RuntimeError):
    """Raised when a model call cannot be completed."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class ModelResponse:
    """One completed model call, with the metadata the audit trail needs."""

    provider: str
    model: str
    content: str
    prompt_hash: str
    response_hash: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None

    @property
    def truncated(self) -> bool:
        """True when the provider stopped because it ran out of output budget.

        A truncated response has no usable content, which is why callers must
        check this instead of treating an empty body as "nothing to say".
        """

        return self.finish_reason == "length"

    finish_reason: str | None = None


class ModelGateway(Protocol):
    """Minimal interface every model provider must satisfy."""

    async def complete(
        self,
        *,
        prompt_hash: str,
        system: str,
        user: str,
        max_output_tokens: int = 900,
        temperature: float = 0.0,
        json_output: bool = False,
    ) -> ModelResponse: ...