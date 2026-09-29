from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, ConfigDict


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    github_url: str | None = None
    local_path: str | None = None


class AnalysisRequest(BaseModel):
    repository_url: str | None = None
    local_path: str | None = None


class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject", "revise"]
    feedback: str = ""


class ProjectRecord(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    project_id: str
    name: str
    description: str
    github_url: str | None = None
    local_path: str | None = None
    status: str = "draft"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    requirements: dict[str, Any] = Field(default_factory=dict)
    research: dict[str, Any] = Field(default_factory=dict)
    architecture: dict[str, Any] = Field(default_factory=dict)
    implementation: dict[str, Any] = Field(default_factory=dict)
    testing: dict[str, Any] = Field(default_factory=dict)
    security: dict[str, Any] = Field(default_factory=dict)
    documentation: dict[str, Any] = Field(default_factory=dict)
    quality_review: dict[str, Any] = Field(default_factory=dict)
    approval: dict[str, Any] = Field(default_factory=dict)
    final_blueprint: dict[str, Any] = Field(default_factory=dict)
    workflow: dict[str, Any] = Field(default_factory=dict)
    agent_states: dict[str, str] = Field(default_factory=dict)
    repo_analysis: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "REPULSOR"
    version: str = "0.1.0"
