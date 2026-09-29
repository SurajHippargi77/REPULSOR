from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from models import ProjectRecord, ProjectCreateRequest
from config import ALLOWED_PROJECT_ROOT

PROJECT_STORE: dict[str, ProjectRecord] = {}

SECRET_PATTERNS = [
    r"(?i)(?:api[_-]?key|token|secret|password|passphrase|private[_-]?key)\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{8,})",
    r"(?i)\b(?:sk_live_[A-Za-z0-9]+|ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|AKIA[0-9A-Z]{16})\b",
]


def redact_sensitive_text(text: str) -> str:
    cleaned = text
    for pattern in SECRET_PATTERNS:
        cleaned = re.sub(pattern, "[REDACTED]", cleaned)
    return cleaned


def create_project(payload: ProjectCreateRequest) -> ProjectRecord:
    local_path = payload.local_path
    if local_path:
        candidate = Path(local_path).expanduser().resolve()
        try:
            candidate.relative_to(ALLOWED_PROJECT_ROOT.resolve())
        except ValueError as exc:
            raise ValueError("Local repository path must stay within the project workspace.") from exc
        local_path = str(candidate)
    project_id = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    record = ProjectRecord(
        project_id=project_id,
        name=payload.name.strip(),
        description=redact_sensitive_text(payload.description.strip()),
        github_url=payload.github_url,
        local_path=local_path,
        status="created",
        created_at=now,
        updated_at=now,
        agent_states={
            "architect": "Idle",
            "research": "Idle",
            "code_intelligence": "Idle",
            "implementation": "Idle",
            "testing": "Idle",
            "security": "Idle",
            "documentation": "Idle",
            "quality_review": "Idle",
            "human_approval": "Idle",
        },
        requirements={
            "summary": redact_sensitive_text(payload.description.strip()),
            "project_name": redact_sensitive_text(payload.name.strip()),
            "source": "user_input",
        },
    )
    PROJECT_STORE[project_id] = record
    return record


def get_project(project_id: str) -> ProjectRecord | None:
    return PROJECT_STORE.get(project_id)


def update_project(project_id: str, **kwargs: Any) -> ProjectRecord:
    project = PROJECT_STORE[project_id]
    for key, value in kwargs.items():
        if value is not None:
            setattr(project, key, value)
    project.updated_at = datetime.now(timezone.utc)
    PROJECT_STORE[project_id] = project
    return project


def mark_agent_state(project_id: str, agent_name: str, state: str) -> None:
    project = PROJECT_STORE[project_id]
    project.agent_states[agent_name] = state
    project.updated_at = datetime.now(timezone.utc)


def safe_project_response(project: ProjectRecord) -> dict[str, Any]:
    def redact(value: Any) -> Any:
        if isinstance(value, str):
            return redact_sensitive_text(value)
        if isinstance(value, dict):
            return {key: redact(item) for key, item in value.items()}
        if isinstance(value, list):
            return [redact(item) for item in value]
        return value

    return redact(project.model_dump())
