from __future__ import annotations

from typing import Any

from agents.runtime import AgentRuntime


class TestEngineAgent:
    def __init__(self):
        self.name = "testing"
        self.runtime = AgentRuntime(self.name)

    def generate_test_plan(self, feature_summary: Any, architecture: Any) -> dict[str, Any]:
        return self.runtime.run(
            "Create a layered testing strategy tied to the requirements and architecture, including failure and security cases.",
            {"requirements": feature_summary, "architecture": architecture},
            self._fallback,
        )

    @staticmethod
    def _fallback(context: dict[str, Any]) -> dict[str, Any]:
        return {
            "test_levels": ["unit", "API contract", "integration", "end-to-end", "load", "security"],
            "critical_cases": [
                "authentication and authorization boundaries",
                "payment idempotency and failure recovery",
                "cart consistency under concurrent updates",
                "invalid input, secrets, and path traversal",
            ],
            "release_gates": ["all critical tests pass", "security review has no unresolved high-risk issue", "migration rollback verified"],
            "context": context["requirements"],
        }
