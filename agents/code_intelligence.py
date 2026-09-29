from __future__ import annotations

from typing import Any

from agents.runtime import AgentRuntime


class CodeIntelligenceAgent:
    def __init__(self):
        self.name = "code_intelligence"
        self.runtime = AgentRuntime(self.name)

    def inspect_repository(self, repository_summary: Any) -> dict[str, Any]:
        return self.runtime.run(
            "Interpret repository inspection data. Identify technologies, structure, important files, and engineering observations.",
            {"repository": repository_summary},
            self._fallback,
        )

    @staticmethod
    def _fallback(context: dict[str, Any]) -> dict[str, Any]:
        repository = context["repository"] or {}
        return {
            "repository_summary": repository,
            "technologies": repository.get("technologies", ["No repository supplied; use project brief"]),
            "project_structure": repository.get("project_structure", repository.get("top_level_entries", [])),
            "important_files": repository.get("important_files", []),
            "observations": repository.get("observations", ["Repository evidence is attached when a repository is supplied"]),
        }
