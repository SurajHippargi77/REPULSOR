from __future__ import annotations

from typing import Any

from agents.runtime import AgentRuntime


class RepulsorCore:
    def __init__(self):
        self.name = "repulsor_core"
        self.runtime = AgentRuntime(self.name)

    def analyze_requirement(self, project_name: str, description: str) -> dict[str, Any]:
        context = {"project_name": project_name, "description": description.strip()}
        return self.runtime.run(
            "Extract the software project's goal, capabilities, constraints, and acceptance criteria.",
            context,
            self._fallback,
        )

    @staticmethod
    def _fallback(context: dict[str, Any]) -> dict[str, Any]:
        description = context["description"]
        lowered = description.lower()
        capabilities = [
            phrase for phrase in (
                "authentication", "product management", "shopping cart", "payments",
                "admin dashboard", "machine learning", "repository analysis",
            ) if phrase in lowered
        ]
        return {
            "project_name": context["project_name"],
            "goal": description,
            "capabilities": capabilities or ["Define domain capabilities from the project brief"],
            "constraints": ["Protect secrets", "Validate external repository and filesystem inputs"],
            "acceptance_criteria": ["Blueprint is structured", "Approval state is explicit", "Quality gates are documented"],
        }
