from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from typing import Any


class AgentRuntime:
    """Use a configured LLM when available and a transparent local fallback otherwise."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.model_name = os.getenv("REPULSOR_LLM_MODEL", "llama-3.1-8b-instant")

    def run(
        self,
        system_prompt: str,
        context: dict[str, Any],
        fallback: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                from langchain_groq import ChatGroq

                model = ChatGroq(model=self.model_name, temperature=0, api_key=api_key)
                response = model.invoke([
                    ("system", system_prompt + " Return only valid JSON."),
                    ("human", json.dumps(context, default=str)),
                ])
                parsed = self._parse_json(response.content)
                parsed["_execution"] = {"mode": "llm", "agent": self.agent_name, "model": self.model_name}
                return parsed
            except Exception as exc:
                result = fallback(context)
                result["_execution"] = {
                    "mode": "development_fallback",
                    "agent": self.agent_name,
                    "reason": f"LLM unavailable: {type(exc).__name__}",
                }
                return result

        result = fallback(context)
        result["_execution"] = {
            "mode": "development_fallback",
            "agent": self.agent_name,
            "reason": "GROQ_API_KEY is not configured",
        }
        return result

    @staticmethod
    def _parse_json(content: Any) -> dict[str, Any]:
        text = str(content).strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if fenced:
            text = fenced.group(1)
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError("LLM response must be a JSON object")
        return parsed
