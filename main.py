from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import BASE_DIR
from models import ProjectCreateRequest, AnalysisRequest, ApprovalRequest, HealthResponse
from services.project_service import (
    create_project,
    get_project,
    update_project,
    safe_project_response,
    redact_sensitive_text,
)
from services.repository_service import RepositoryInputError, fetch_public_repo_summary, analyze_local_repository
from graph.workflow import resume_approval, run_project_workflow

app = FastAPI(title="REPULSOR", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
app.mount("/assets", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="assets")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))


@app.get("/api/health", response_model=HealthResponse)
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": "REPULSOR", "version": "0.1.0"}


@app.post("/api/projects")
async def create_new_project(payload: ProjectCreateRequest):
    sanitized_payload = ProjectCreateRequest(
        name=redact_sensitive_text(payload.name.strip()),
        description=redact_sensitive_text(payload.description.strip()),
        github_url=payload.github_url,
        local_path=payload.local_path,
    )
    try:
        project = create_project(sanitized_payload)
        state = run_project_workflow(project)
    except (RepositoryInputError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _persist_workflow_state(project, state)
    return {"success": True, "project": safe_project_response(project)}


def _persist_workflow_state(project: Any, state: dict[str, Any]) -> None:
    update_project(
        project.project_id,
        status=state.get("status", project.status),
        requirements=state.get("requirement_summary", {}),
        research=state.get("research_summary", {}),
        architecture=state.get("architecture_summary", {}),
        implementation=state.get("implementation_summary", {}),
        testing=state.get("testing_summary", {}),
        security=state.get("security_summary", {}),
        documentation=state.get("documentation_summary", {}),
        quality_review=state.get("quality_review", {}),
        final_blueprint=state.get("final_blueprint", {}),
        repo_analysis=state.get("repo_analysis", {}),
        workflow={
            "status": state.get("status"),
            "approval_status": state.get("approval_status"),
            "approval_feedback": state.get("approval_feedback", ""),
            "log": state.get("workflow_log", []),
        },
        agent_states={
            name: "Complete" for name in (
                "architect", "research", "code_intelligence", "implementation",
                "testing", "security", "documentation", "quality_review",
            )
        } | {"human_approval": "Waiting" if state.get("status") == "waiting_for_approval" else "Complete"},
    )


@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "project": safe_project_response(project)}


@app.post("/api/projects/{project_id}/analyze")
async def analyze_project(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.workflow.get("log"):
        return {"success": True, "status": project.status, "analysis": project.requirements}
    state = run_project_workflow(project)
    _persist_workflow_state(project, state)
    return {"success": True, "status": project.status, "analysis": project.requirements}


@app.post("/api/projects/{project_id}/research")
async def research_project(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "status": project.status, "research": project.research}


@app.post("/api/projects/{project_id}/architecture")
async def architecture_project(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "status": project.status, "architecture": project.architecture}


@app.post("/api/projects/{project_id}/generate-plan")
async def generate_plan(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "status": project.status, "blueprint": project.final_blueprint}


@app.post("/api/projects/{project_id}/approve")
async def approve_project(project_id: str, payload: ApprovalRequest):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "waiting_for_approval":
        raise HTTPException(status_code=409, detail="Project is not waiting for approval.")
    if payload.decision == "revise":
        state = run_project_workflow(project, redact_sensitive_text(payload.feedback))
        _persist_workflow_state(project, state)
        update_project(project_id, approval={"decision": "revise", "feedback": payload.feedback})
        return {"success": True, "decision": "revise", "status": project.status, "project": safe_project_response(project)}
    state = dict(project.workflow)
    state.update({"final_blueprint": project.final_blueprint, "approval_status": payload.decision})
    resumed = resume_approval(state, payload.decision, payload.feedback)
    update_project(
        project_id,
        status=resumed["status"],
        approval={"decision": payload.decision, "feedback": payload.feedback},
        workflow={
            **project.workflow,
            "approval_status": payload.decision,
            "approval_feedback": payload.feedback,
            "log": project.workflow.get("log", []) + resumed.get("workflow_log", []),
        },
        agent_states={**project.agent_states, "human_approval": "Complete"},
    )
    return {"success": True, "decision": payload.decision, "status": resumed["status"], "project": safe_project_response(project)}


@app.post("/api/projects/{project_id}/revise")
async def revise_project(project_id: str, payload: ApprovalRequest):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "waiting_for_approval":
        raise HTTPException(status_code=409, detail="Project is not waiting for approval.")
    state = run_project_workflow(project, redact_sensitive_text(payload.feedback))
    _persist_workflow_state(project, state)
    update_project(project_id, approval={"decision": "revise", "feedback": payload.feedback})
    return {"success": True, "decision": "revise", "status": project.status, "project": safe_project_response(project)}


@app.post("/api/repository/analyze")
async def analyze_repository(payload: AnalysisRequest):
    repository_url = payload.repository_url
    local_path = payload.local_path
    if repository_url:
        try:
            data = fetch_public_repo_summary(repository_url)
        except RepositoryInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"success": True, "analysis": data}
    if local_path:
        try:
            data = analyze_local_repository(local_path)
        except RepositoryInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"success": True, "analysis": data}
    raise HTTPException(status_code=400, detail="Provide either a repository_url or local_path.")


@app.get("/api/projects/{project_id}/status")
async def project_status(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "project_id": project_id, "status": project.status, "agent_states": project.agent_states}


@app.get("/")
async def serve_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
