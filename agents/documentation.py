from __future__ import annotations

from typing import Any

from agents.runtime import AgentRuntime


class DocumentationAgent:
    def __init__(self):
        self.name = "documentation"
        self.runtime = AgentRuntime(self.name)

    def produce_docs(self, project_name: str, architecture: Any) -> dict[str, Any]:
        return self.runtime.run(
            "Create a documentation plan for the project and architecture, including operator and developer needs.",
            {"project_name": project_name, "architecture": architecture},
            self._fallback,
        )

    @staticmethod
    def _fallback(context: dict[str, Any]) -> dict[str, Any]:
        return {
            "project_name": context["project_name"],
            "documentation_plan": [
                "product and domain overview",
                "architecture and data-flow decision record",
                "local setup and environment variables",
                "API contracts and authentication guide",
                "testing, release, and rollback runbook",
                "security and incident response guidance",
            ],
            "architecture_reference": context["architecture"],
        }
