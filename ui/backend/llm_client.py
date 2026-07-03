"""LLM client — configurable provider (OpenAI / Anthropic / local)."""

import json
import os

import httpx
import httpx_sse
from pydantic import BaseModel


class LLMClient(BaseModel):
    """Thin async wrapper around LLM chat completion APIs."""

    provider: str = "openai"

    class Config:
        arbitrary_types_allowed = True

    def _api_base(self) -> str:
        if self.provider == "openai":
            return os.getenv("OPENAI_API_BASE", "https://api.openai.com")
        if self.provider == "anthropic":
            return "https://api.anthropic.com"
        return os.getenv("LLM_API_BASE", "http://localhost:8000/v1")

    def _api_key(self) -> str:
        return (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("LLM_API_KEY", "")
        )

    def _default_model(self) -> str:
        return os.getenv("LLM_MODEL", "gpt-4o")

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
        model: str | None = None,
    ) -> str:
        """Send a chat completion request and return the assistant text."""

        model = model or self._default_model()
        headers = {
            "Content-Type": "application/json",
        }

        if self.provider == "anthropic":
            headers["x-api-key"] = self._api_key()
            headers["anthropic-version"] = "2023-06-01"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
                "max_tokens": 8192,
            }
        else:
            headers["Authorization"] = f"Bearer {self._api_key()}"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
            }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._api_base()}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            body = resp.json()

        if self.provider == "anthropic":
            return body.get("content", [{}])[0].get("text", "")
        return body["choices"][0]["message"]["content"]

    async def generate_stream(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
        model: str | None = None,
    ):
        """Yield partial text tokens via SSE-style generator."""
        model = model or self._default_model()
        headers = {"Content-Type": "application/json"}

        if self.provider == "anthropic":
            headers["x-api-key"] = self._api_key()
            headers["anthropic-version"] = "2023-06-01"
        else:
            headers["Authorization"] = f"Bearer {self._api_key()}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self._api_base()}/chat/completions",
                headers=headers,
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = (
                                data.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content", "")
                            )
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            pass
