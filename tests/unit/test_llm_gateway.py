"""Offline tests for the DeepSeek model gateway."""

from __future__ import annotations

import json

import httpx
import pytest

from research_agent.llm.deepseek import (
    MIN_OUTPUT_TOKENS,
    DeepSeekGateway,
)
from research_agent.llm.gateway import ModelGatewayError


def _client(handler: httpx.MockTransport) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=handler, timeout=5.0)


def test_gateway_requires_an_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    with pytest.raises(ModelGatewayError, match="DEEPSEEK_API_KEY"):
        DeepSeekGateway(http_client=httpx.AsyncClient(transport=transport))


@pytest.mark.asyncio
async def test_complete_returns_content_and_usage() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["model"] == "deepseek-v4-flash"
        assert body["temperature"] == 0.0
        assert request.headers["authorization"].startswith("Bearer ")
        return httpx.Response(
            200,
            json={
                "model": "deepseek-flash",
                "choices": [
                    {
                        "message": {"role": "assistant", "content": '{"ok": true}'},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 120, "completion_tokens": 40},
            },
        )

    async with _client(httpx.MockTransport(handler)) as http_client:
        gateway = DeepSeekGateway(http_client=http_client, api_key="test-key")
        response = await gateway.complete(
            prompt_hash="abc123", system="sys", user="usr"
        )

    assert response.content == '{"ok": true}'
    assert response.input_tokens == 120
    assert response.output_tokens == 40
    assert response.latency_ms is not None
    assert response.finish_reason == "stop"
    assert response.truncated is False


@pytest.mark.asyncio
async def test_served_model_name_is_recorded_not_the_requested_alias() -> None:
    """DeepSeek serves 'deepseek-flash' when 'deepseek-v4-flash' is requested."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "deepseek-flash",
                "choices": [
                    {"message": {"content": "{}"}, "finish_reason": "stop"}
                ],
            },
        )

    async with _client(httpx.MockTransport(handler)) as http_client:
        gateway = DeepSeekGateway(http_client=http_client, api_key="test-key")
        response = await gateway.complete(prompt_hash="p", system="s", user="u")

    assert response.model == "deepseek-flash"


@pytest.mark.asyncio
async def test_truncated_response_is_flagged() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "deepseek-flash",
                "choices": [
                    {"message": {"content": ""}, "finish_reason": "length"}
                ],
                "usage": {"prompt_tokens": 500, "completion_tokens": 900},
            },
        )

    async with _client(httpx.MockTransport(handler)) as http_client:
        gateway = DeepSeekGateway(http_client=http_client, api_key="test-key")
        response = await gateway.complete(prompt_hash="p", system="s", user="u")

    assert response.truncated is True
    assert response.content == ""


@pytest.mark.asyncio
async def test_output_budget_is_never_below_the_measured_minimum() -> None:
    seen: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content)["max_tokens"])
        return httpx.Response(
            200,
            json={
                "model": "deepseek-flash",
                "choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}],
            },
        )

    async with _client(httpx.MockTransport(handler)) as http_client:
        gateway = DeepSeekGateway(http_client=http_client, api_key="test-key")
        await gateway.complete(
            prompt_hash="p", system="s", user="u", max_output_tokens=64
        )

    assert seen == [MIN_OUTPUT_TOKENS]


@pytest.mark.asyncio
async def test_rate_limit_is_retried_then_succeeds() -> None:
    attempts: list[int] = []
    delays: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        delays.append(seconds)

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(1)
        if len(attempts) == 1:
            return httpx.Response(429, headers={"retry-after": "0.1"}, json={})
        return httpx.Response(
            200,
            json={
                "model": "deepseek-flash",
                "choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}],
            },
        )

    async with _client(httpx.MockTransport(handler)) as http_client:
        gateway = DeepSeekGateway(
            http_client=http_client, api_key="test-key", sleep=fake_sleep
        )
        response = await gateway.complete(prompt_hash="p", system="s", user="u")

    assert len(attempts) == 2
    assert delays == [0.1]
    assert response.content == "{}"


@pytest.mark.asyncio
async def test_repeated_rate_limits_surface_as_gateway_error() -> None:
    async def fake_sleep(seconds: float) -> None:
        return None

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={})

    async with _client(httpx.MockTransport(handler)) as http_client:
        gateway = DeepSeekGateway(
            http_client=http_client,
            api_key="test-key",
            max_attempts=2,
            sleep=fake_sleep,
        )
        with pytest.raises(ModelGatewayError):
            await gateway.complete(prompt_hash="p", system="s", user="u")


@pytest.mark.asyncio
async def test_json_output_requests_structured_response() -> None:
    seen: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "model": "deepseek-flash",
                "choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}],
            },
        )

    async with _client(httpx.MockTransport(handler)) as http_client:
        gateway = DeepSeekGateway(http_client=http_client, api_key="test-key")
        await gateway.complete(
            prompt_hash="p", system="s", user="u", json_output=True
        )

    assert seen[0]["response_format"] == {"type": "json_object"}