from __future__ import annotations

from typing import Any

from agents.runtime import AgentRuntime


class ImplementationAgent:
    def __init__(self):
        self.name = "implementation"
        self.runtime = AgentRuntime(self.name)

    def produce_implementation_plan(self, architecture: dict[str, Any], requirements: dict[str, Any]) -> dict[str, Any]:
        return self.runtime.run(
            "Turn the architecture and requirements into an ordered, concrete development plan with deliverables.",
            {"architecture": architecture, "requirements": requirements},
            self._fallback,
        )

    @staticmethod
    def _fallback(context: dict[str, Any]) -> dict[str, Any]:
        capabilities = context["requirements"].get("capabilities", [])
        return {
            "implementation_plan": [
                "Define domain entities, API contracts, and authorization rules",
                "Implement persistence, migrations, and service boundaries",
                f"Deliver capability modules: {', '.join(capabilities) or 'core product workflow'}",
                "Add integrations behind idempotent adapters",
                "Wire observability, deployment, and rollback procedures",
            ],
            "milestones": ["Foundation", "Core capabilities", "Integrations", "Quality and release"],
            "architecture_reference": context["architecture"],
        }
