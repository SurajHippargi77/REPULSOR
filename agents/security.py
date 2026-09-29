from __future__ import annotations

from typing import Any

from agents.runtime import AgentRuntime


class SecurityAgent:
    def __init__(self):
        self.name = "security"
        self.runtime = AgentRuntime(self.name)

    def assess_security(self, project_name: str, requirements: Any) -> dict[str, Any]:
        return self.runtime.run(
            "Assess security risks in the supplied software project and propose concrete mitigations.",
            {"project_name": project_name, "requirements": requirements},
            self._fallback,
        )

    @staticmethod
    def _fallback(context: dict[str, Any]) -> dict[str, Any]:
        return {
            "project_name": context["project_name"],
            "threats": ["credential leakage", "broken access control", "payment abuse", "injection and unsafe integrations"],
            "controls": [
                "Redact credentials before persistence and responses",
                "Use role-based authorization with deny-by-default policies",
                "Validate repository URLs, local paths, and tool arguments",
                "Use idempotency keys and provider-side verification for payments",
                "Audit security events without storing secrets",
            ],
        }
