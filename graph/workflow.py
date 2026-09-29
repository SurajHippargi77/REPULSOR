from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from agents.architect import ArchitectAgent
from agents.code_intelligence import CodeIntelligenceAgent
from agents.core import RepulsorCore
from agents.documentation import DocumentationAgent
from agents.implementation import ImplementationAgent
from agents.researcher import ResearchAgent
from agents.security import SecurityAgent
from agents.testing import TestEngineAgent
from graph.state import ProjectState
from services.repository_service import fetch_public_repo_summary
from services.mcp_transport import call_mcp_tool

core_agent = RepulsorCore()
architect_agent = ArchitectAgent()
research_agent = ResearchAgent()
code_agent = CodeIntelligenceAgent()
implementation_agent = ImplementationAgent()
testing_agent = TestEngineAgent()
security_agent = SecurityAgent()
documentation_agent = DocumentationAgent()


def core_node(state: ProjectState) -> dict[str, Any]:
    result = core_agent.analyze_requirement(state["project_name"], state["user_input"])
    return {"requirement_summary": result, "workflow_log": ["core: requirements analyzed"]}


def architect_node(state: ProjectState) -> dict[str, Any]:
    result = architect_agent.produce_architecture(state["requirement_summary"])
    return {"architecture_summary": result, "workflow_log": ["architect: architecture produced"]}


def research_node(state: ProjectState) -> dict[str, Any]:
    result = research_agent.gather_research(
        state["project_name"],
        state["user_input"],
        state.get("repo_analysis", {}),
    )
    try:
        result["mcp_research"] = call_mcp_tool(
            "research",
            "fetch_research_summary",
            {"topic": state["user_input"]},
        )
    except Exception as exc:
        result["mcp_research_error"] = f"Research MCP unavailable: {type(exc).__name__}"
    return {"research_summary": result, "workflow_log": ["research: findings gathered with Research MCP"]}


def code_intelligence_node(state: ProjectState) -> dict[str, Any]:
    result = code_agent.inspect_repository(state.get("repo_analysis", {}))
    return {"code_intelligence_summary": result, "workflow_log": ["code_intelligence: repository signals inspected"]}


def implementation_node(state: ProjectState) -> dict[str, Any]:
    result = implementation_agent.produce_implementation_plan(
        state["architecture_summary"],
        state["requirement_summary"],
    )
    try:
        result["stack_validation"] = call_mcp_tool(
            "development",
            "validate_stack",
            {"requirements": state["user_input"]},
        )
    except Exception as exc:
        result["stack_validation_error"] = f"Development MCP unavailable: {type(exc).__name__}"
    return {"implementation_summary": result, "workflow_log": ["implementation: development plan produced"]}


def testing_node(state: ProjectState) -> dict[str, Any]:
    result = testing_agent.generate_test_plan(
        state["requirement_summary"],
        state["architecture_summary"],
    )
    return {"testing_summary": result, "workflow_log": ["testing: validation strategy produced"]}


def security_node(state: ProjectState) -> dict[str, Any]:
    result = security_agent.assess_security(
        state["project_name"],
        state["requirement_summary"],
    )
    return {"security_summary": result, "workflow_log": ["security: controls assessed"]}


def documentation_node(state: ProjectState) -> dict[str, Any]:
    result = documentation_agent.produce_docs(
        state["project_name"],
        state["architecture_summary"],
    )
    return {"documentation_summary": result, "workflow_log": ["documentation: plan produced"]}


def review_node(state: ProjectState) -> dict[str, Any]:
    blueprint = {
        "requirements": state["requirement_summary"],
        "architecture": state["architecture_summary"],
        "research": state["research_summary"],
        "code_intelligence": state["code_intelligence_summary"],
        "development_plan": state["implementation_summary"],
        "testing_strategy": state["testing_summary"],
        "security_considerations": state["security_summary"],
        "documentation_plan": state["documentation_summary"],
        "review": {
            "checks": ["requirements present", "architecture present", "quality gates present"],
            "result": "approval requested",
        },
    }
    return {
        "quality_review": blueprint["review"],
        "final_blueprint": blueprint,
        "workflow_log": ["review: structured blueprint assembled"],
    }


def approval_node(state: ProjectState) -> dict[str, Any]:
    return {
        "status": "waiting_for_approval",
        "approval_status": "pending",
        "workflow_log": ["approval: waiting for human decision"],
    }


def finalize_node(state: ProjectState) -> dict[str, Any]:
    return {
        "status": "approved",
        "workflow_log": ["approval: approved; workflow finalized"],
    }


def rejected_node(state: ProjectState) -> dict[str, Any]:
    return {
        "status": "rejected",
        "workflow_log": ["approval: rejected; workflow stopped"],
    }


def revised_node(state: ProjectState) -> dict[str, Any]:
    return {
        "status": "revision_requested",
        "workflow_log": ["approval: changes requested; proposal requires revision"],
    }


def build_workflow():
    graph = StateGraph(ProjectState)
    graph.add_node("core", core_node)
    graph.add_node("architect", architect_node)
    graph.add_node("research", research_node)
    graph.add_node("code_intelligence", code_intelligence_node)
    graph.add_node("implementation", implementation_node)
    graph.add_node("testing", testing_node)
    graph.add_node("security", security_node)
    graph.add_node("documentation", documentation_node)
    graph.add_node("review", review_node)
    graph.add_node("approval", approval_node)
    graph.add_edge(START, "core")
    graph.add_edge("core", "architect")
    graph.add_edge("architect", "research")
    graph.add_edge("research", "code_intelligence")
    graph.add_edge("code_intelligence", "implementation")
    graph.add_edge("implementation", "testing")
    graph.add_edge("testing", "security")
    graph.add_edge("security", "documentation")
    graph.add_edge("documentation", "review")
    graph.add_edge("review", "approval")
    graph.add_edge("approval", END)
    return graph.compile()


def build_approval_workflow():
    graph = StateGraph(ProjectState)
    graph.add_node("finalize", finalize_node)
    graph.add_node("rejected", rejected_node)
    graph.add_node("revised", revised_node)
    graph.add_conditional_edges(
        START,
        lambda state: state.get("approval_status", "reject"),
        {"approve": "finalize", "approved": "finalize", "revise": "revised", "reject": "rejected"},
    )
    graph.add_edge("finalize", END)
    graph.add_edge("rejected", END)
    graph.add_edge("revised", END)
    return graph.compile()


WORKFLOW = build_workflow()
APPROVAL_WORKFLOW = build_approval_workflow()


def run_project_workflow(project: Any, revision_feedback: str = "") -> ProjectState:
    repo_analysis = {}
    if project.github_url:
        repo_analysis = fetch_public_repo_summary(project.github_url)
    elif project.local_path:
        from services.repository_service import analyze_local_repository
        repo_analysis = analyze_local_repository(project.local_path)

    initial: ProjectState = {
        "project_id": project.project_id,
        "project_name": project.name,
        "user_input": project.description + (f" Revision feedback: {revision_feedback}" if revision_feedback else ""),
        "repo_analysis": repo_analysis,
        "status": "running",
        "approval_status": "not_started",
        "messages": [],
        "workflow_log": [],
    }
    return WORKFLOW.invoke(initial)


def resume_approval(state: ProjectState, decision: str, feedback: str) -> ProjectState:
    resumed = dict(state)
    resumed["approval_status"] = "approved" if decision == "approve" else decision
    resumed["approval_feedback"] = feedback
    return APPROVAL_WORKFLOW.invoke(resumed)
