from __future__ import annotations

from typing import Any

from agents.runtime import AgentRuntime


class ArchitectAgent:
    def __init__(self):
        self.name = "architect"
        self.runtime = AgentRuntime(self.name)

    def produce_architecture(self, requirement_summary: Any) -> dict[str, Any]:
        return self.runtime.run(
            "Design a practical software architecture from the supplied requirements. Include components, data flow, and risks.",
            {"requirements": requirement_summary},
            self._fallback,
        )

    @staticmethod
    def _fallback(context: dict[str, Any]) -> dict[str, Any]:
        requirements = context["requirements"]
        return {
            "summary": "Layered architecture derived from the project requirements.",
            "components": ["React dashboard", "FastAPI API", "domain services", "PostgreSQL persistence", "background jobs"],
            "data_flow": ["client -> API -> domain services -> PostgreSQL", "jobs -> payment and notification providers"],
            "patterns": ["modular service", "API contracts", "event-driven integration where needed"],
            "requirements_covered": requirements.get("capabilities", []) if isinstance(requirements, dict) else [str(requirements)],
            "risks": ["payment idempotency", "authorization boundaries", "operational observability"],
        }
