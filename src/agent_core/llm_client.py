"""Minimal OpenAI Responses API client with a no-key fallback path."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def load_project_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue

        key, value = clean.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


class LLMClient:
    def __init__(self) -> None:
        load_project_env()
        self.provider = os.environ.get("LLM_PROVIDER", "openai").strip().lower()
        if self.provider == "deepseek":
            self.api_key = os.environ.get("DEEPSEEK_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
            self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
            self.base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        else:
            self.provider = "openai"
            self.api_key = os.environ.get("OPENAI_API_KEY", "")
            self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def extract_json(self, *, schema_name: str, schema: dict, system_prompt: str, user_prompt: str) -> tuple[dict[str, Any] | None, str]:
        """Return parsed JSON and status.

        The status is included so the demo can show whether a result came from
        GPT or from the local fallback parser.
        """
        if not self.enabled:
            return None, "fallback_no_api_key"

        if self.provider == "deepseek":
            return self._extract_json_deepseek(
                schema_name=schema_name,
                schema=schema,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            },
        }

        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
            text = self._extract_output_text(data)
            return json.loads(text), "gpt_structured_output"
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            return {"_llm_error": str(exc)}, "fallback_llm_error"

    def _extract_json_deepseek(self, *, schema_name: str, schema: dict, system_prompt: str, user_prompt: str) -> tuple[dict[str, Any] | None, str]:
        schema_hint = json.dumps(schema, ensure_ascii=False)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"{system_prompt}\n\n"
                        f"Return a single valid JSON object for schema `{schema_name}`. "
                        "Do not wrap it in markdown. Do not include explanatory text. "
                        f"Schema:\n{schema_hint}"
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
            text = data["choices"][0]["message"]["content"]
            return json.loads(text), "deepseek_json_output"
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            return {"_llm_error": str(exc)}, "fallback_llm_error"

    def generate_json(self, *, schema_name: str, schema: dict, system_prompt: str, user_prompt: str) -> tuple[dict[str, Any] | None, str]:
        return self.extract_json(
            schema_name=schema_name,
            schema=schema,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def _extract_output_text(self, response: dict[str, Any]) -> str:
        if response.get("output_text"):
            return response["output_text"]

        for item in response.get("output", []):
            for content in item.get("content", []):
                if "text" in content:
                    return content["text"]

        raise KeyError("No output text found in OpenAI response")
