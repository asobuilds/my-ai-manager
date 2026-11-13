"""Multi-provider LLM client with fallback for Agnes AI."""

from __future__ import annotations

import logging

from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FallbackLLMClient:
    """Try multiple LLM providers in order, returning on first success."""

    def __init__(self) -> None:
        self.providers: list[dict[str, object]] = []

        # Primary: Agnes (OpenAI-compatible hub)
        agnes_key = settings.AGNES_API_KEY
        if agnes_key:
            self.providers.append(
                {
                    "name": "agnes",
                    "client": OpenAI(
                        api_key=agnes_key,
                        base_url="https://apihub.agnes-ai.com/v1",
                        timeout=30.0,
                    ),
                    "model": "agnes-2.5-flash",
                }
            )

        # Fallback 1: Groq (OpenAI-compatible)
        groq_key = settings.GROQ_API_KEY
        if groq_key:
            self.providers.append(
                {
                    "name": "groq",
                    "client": OpenAI(
                        api_key=groq_key,
                        base_url="https://api.groq.com/openai/v1",
                        timeout=30.0,
                    ),
                    "model": "llama-3.3-70b-versatile",
                }
            )

        # Fallback 2: Gemini (OpenAI-compatible endpoint)
        gemini_key = settings.GEMINI_API_KEY
        if gemini_key:
            self.providers.append(
                {
                    "name": "gemini",
                    "client": OpenAI(
                        api_key=gemini_key,
                        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                        timeout=30.0,
                    ),
                    "model": "gemini-2.5-flash",
                }
            )

    def _call_provider(self, provider: dict[str, object], messages: list[dict[str, str]], tools: list[dict] | None = None) -> dict:
        """Make a single chat_completion call to a provider."""
        client = provider["client"]
        model = provider["model"]

        params: dict[str, object] = {
            "model": model,
            "messages": messages,
        }
        if tools is not None:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        resp = client.chat.completions.create(**params)
        # Return a dict compatible with the existing code's expectations
        choice = resp.choices[0]
        return {
            "id": resp.id,
            "object": resp.object,
            "created": resp.created,
            "model": resp.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content,
                        "tool_calls": choice.message.tool_calls or [],
                    },
                    "finish_reason": choice.finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
                "total_tokens": resp.usage.total_tokens,
            },
            "system_fingerprint": getattr(resp, "system_fingerprint", None),
        }

    def chat_completion(self, messages: list[dict[str, str]], tools: list[dict] | None = None) -> dict:
        """Try each provider in order; return the first successful response dict.

    Expected response shape (OpenAI-style):
        {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "...", "tool_calls": [...]},
                }
            ]
        }
    """
        last_exception: Exception | None = None

        for provider in self.providers:
            try:
                logger.info(f"Trying LLM provider: {provider['name']}")
                data = self._call_provider(provider, messages, tools)
                logger.info(f"Provider {provider['name']} succeeded")
                return data
            except Exception as exc:
                logger.warning(f"Provider {provider['name']} failed: {exc}")
                last_exception = exc

        # All providers failed
        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_exception}"
        )