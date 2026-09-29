from __future__ import annotations


def analyze_project_intent(description: str) -> dict:
    return {
        "intent": description,
        "likely_stack": ["Python", "FastAPI"],
        "core_workstreams": ["API design", "data model", "security", "testing"],
    }
