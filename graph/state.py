from __future__ import annotations

from typing import Any, TypedDict, Annotated
import operator


class ProjectState(TypedDict, total=False):
    project_id: str
    project_name: str
    status: str
    user_input: str
    requirement_summary: str
    architecture_summary: str
    research_summary: str
    code_intelligence_summary: str
    implementation_summary: str
    testing_summary: str
    security_summary: str
    documentation_summary: str
    quality_review: str
    approval_status: str
    approval_feedback: str
    final_blueprint: str
    messages: Annotated[list[str], operator.add]
    repo_analysis: dict[str, Any]
    workflow_log: Annotated[list[str], operator.add]
