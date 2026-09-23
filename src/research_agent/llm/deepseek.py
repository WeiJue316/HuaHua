"""DeepSeek implementation of the model gateway.

DeepSeek exposes an OpenAI-compatible chat completions endpoint. The model
spends part of its output budget on internal reasoning before emitting any
content, so the default output budget is deliberately generous: a small budget
returns ``finish_reason="length"`` with an empty body.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from research_agent.llm.gateway import ModelGatewayError, ModelResponse

DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY_ENV_VAR = "DEEPSEEK_API_KEY"
DEEPSEEK_DEFAULT_MODEL = "deepseek-v4-flash"
RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
MIN_OUTPUT_TOKENS = 900

SleepFn = Callable[[float], Awaitable[None]]


def api_key_from_environment() -> str | None:
    """Return the configured DeepSeek API key, if any."""

    value = os.environ.get(DEEPSEEK_API_KEY_ENV_VAR, "").strip()
    return value or None


class DeepSeekGateway:
    """Async client for DeepSeek chat completions."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        api_key: str | None = None,
        model: str = DEEPSEEK_DEFAULT_MODEL,
        api_url: str = DEEPSEEK_API_URL,
        max_attempts: int = 3,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        key = api_key or api_key_from_environment()
        if not key:
            raise ModelGatewayError(
                f"{DEEPSEEK_API_KEY_ENV_VAR} is not set; the semantic relevance "
                "filter needs a model provider"
            )
        self.api_key = key
        self.model = model
        self.api_url = api_url.rstrip("/")
        self.http_client = http_client
        self.max_attempts = max(1, max_attempts)
        self.sleep = sleep

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def complete(
        self,
        *,
        prompt_hash: str,
        system: str,
        user: str,
        max_output_tokens: int = MIN_OUTPUT_TOKENS,
        temperature: float = 0.0,
        json_output: bool = False,
    ) -> ModelResponse:
        """Run one chat completion and return the served model's answer."""

        body: dict[str, Any] = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max(max_output_tokens, MIN_OUTPUT_TOKENS),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_output:
            body["response_format"] = {"type": "json_object"}

        last_error: str | None = None
        for attempt in range(1, self.max_attempts + 1):
            started = time.monotonic()
            try:
                response = await self.http_client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self._headers(),
                    json=body,
                )
            except httpx.HTTPError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt >= self.max_attempts:
                    raise ModelGatewayError(
                        f"DeepSeek request failed: {last_error}"
                    ) from exc
                await self.sleep(self._delay(attempt))
                continue

            elapsed_ms = int((time.monotonic() - started) * 1000)
            if response.status_code in RETRYABLE_STATUS_CODES and (
                attempt < self.max_attempts
            ):
                last_error = f"status {response.status_code}"
                await self.sleep(self._retry_after(response, attempt))
                continue
            if response.status_code >= 400:
                raise ModelGatewayError(
                    f"DeepSeek request failed with status {response.status_code}",
                    status_code=response.status_code,
                )

            try:
                payload = response.json()
            except json.JSONDecodeError as exc:
                raise ModelGatewayError(
                    f"DeepSeek response is not JSON: {exc}"
                ) from exc
            return self._to_model_response(payload, prompt_hash, elapsed_ms)

        raise ModelGatewayError(f"DeepSeek request failed: {last_error}")

    @staticmethod
    def _delay(attempt: int) -> float:
        # 1 << n keeps the type an int; 2 ** n is Any because a negative
        # exponent would yield a float.
        return min(8.0, 0.5 * float(1 << max(0, attempt - 1)))

    def _retry_after(self, response: httpx.Response, attempt: int) -> float:
        header = response.headers.get("retry-after")
        if header:
            try:
                return max(0.0, float(header))
            except ValueError:
                pass
        return self._delay(attempt)

    def _to_model_response(
        self,
        payload: dict[str, Any],
        prompt_hash: str,
        elapsed_ms: int,
    ) -> ModelResponse:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ModelGatewayError("DeepSeek response contains no choices")
        choice = choices[0]
        if not isinstance(choice, dict):
            raise ModelGatewayError("DeepSeek choice is not an object")
        message = choice.get("message")
        content = ""
        if isinstance(message, dict):
            raw = message.get("content")
            if isinstance(raw, str):
                content = raw
        usage = payload.get("usage")
        input_tokens = output_tokens = None
        if isinstance(usage, dict):
            prompt_tokens = usage.get("prompt_tokens")
            completion_tokens = usage.get("completion_tokens")
            input_tokens = prompt_tokens if isinstance(prompt_tokens, int) else None
            output_tokens = (
                completion_tokens if isinstance(completion_tokens, int) else None
            )
        finish_reason = choice.get("finish_reason")
        served_model = payload.get("model")
        return ModelResponse(
            provider="deepseek",
            model=str(served_model or self.model),
            content=content,
            prompt_hash=prompt_hash,
            response_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=elapsed_ms,
            finish_reason=str(finish_reason) if finish_reason else None,
        )