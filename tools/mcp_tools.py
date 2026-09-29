from __future__ import annotations

from pathlib import Path
from typing import Any


def fetch_research_summary(topic: str) -> str:
    topic = topic.strip()
    if not topic or len(topic) > 500:
        raise ValueError("topic must contain between 1 and 500 characters")
    return (
        f"Research scope for '{topic}': evaluate ecosystem fit, architecture trade-offs, "
        "development velocity, security exposure, maintenance health, and testing strategy."
    )


def inspect_repository_directory(path: str) -> dict[str, Any]:
    root = Path(path).expanduser().resolve()
    allowed_root = Path.cwd().resolve()
    try:
        root.relative_to(allowed_root)
    except ValueError:
        return {"status": "blocked", "reason": "Path traversal is not allowed."}
    if not root.exists() or not root.is_dir():
        return {"status": "error", "reason": "Directory does not exist."}
    entries = [p.name for p in sorted(root.iterdir())[:50]]
    return {"status": "ok", "repository": root.name, "entries": entries}


def validate_stack(requirements: str) -> dict[str, Any]:
    if not isinstance(requirements, str) or not requirements.strip() or len(requirements) > 5000:
        return {"status": "error", "reason": "requirements must contain between 1 and 5000 characters"}
    stack = requirements.lower()
    recommendations = []
    if "fastapi" in stack:
        recommendations.append("Use FastAPI with Pydantic models and dependency injection")
    if "postgresql" in stack:
        recommendations.append("Use SQLAlchemy or asyncpg for persistence and migrations")
    if "machine learning" in stack or "machine-learning" in stack:
        recommendations.append("Separate training pipeline from serving API with model versioning")
    if "react" in stack:
        recommendations.append("Use typed API contracts and query-state management in the React client")
    if not recommendations:
        recommendations.append("Baseline on a modular service architecture and add testing gates")
    return {"status": "ok", "recommendations": recommendations}
