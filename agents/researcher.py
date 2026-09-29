from __future__ import annotations

from typing import Any

from agents.runtime import AgentRuntime


class ResearchAgent:
    def __init__(self):
        self.name = "research"
        self.runtime = AgentRuntime(self.name)

    def gather_research(self, project_name: str, description: str, repo_analysis: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.runtime.run(
            "Research the technology and repository context. Give concrete recommendations tied to the input.",
            {"project_name": project_name, "description": description, "repository": repo_analysis or {}},
            self._fallback,
        )

    @staticmethod
    def _fallback(context: dict[str, Any]) -> dict[str, Any]:
        description = context["description"].lower()
        technologies = [name for name in ("FastAPI", "PostgreSQL", "React", "Python", "TypeScript") if name.lower() in description]
        return {
            "project_name": context["project_name"],
            "technology_recommendations": technologies or ["Select technologies after requirements validation"],
            "research_findings": [
                "Use standards-supported libraries with active maintenance",
                "Verify authentication, payments, and data retention requirements",
                "Benchmark the critical path before committing to scale assumptions",
            ],
            "repository_context": context["repository"],
        }
