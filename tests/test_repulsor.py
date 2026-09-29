from fastapi.testclient import TestClient

from main import app
from tools.mcp_tools import inspect_repository_directory, validate_stack


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "REPULSOR"


def test_create_project():
    response = client.post(
        "/api/projects",
        json={
            "name": "Network Intrusion Detection API",
            "description": "I want to build a network intrusion detection API using Python, FastAPI and machine learning.",
            "github_url": None,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["project"]["name"] == "Network Intrusion Detection API"
    assert "project_id" in payload["project"]


def test_repository_analysis():
    response = client.post(
        "/api/repository/analyze",
        json={"repository_url": "https://github.com/microsoft/vscode"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["analysis"]["repository"] == "vscode"


def test_approval_workflow_rejects_secret_input():
    response = client.post(
        "/api/projects",
        json={
            "name": "Secret Handling API",
            "description": "Build an API with a secret key like sk_live_1234567890 and expose it in logs.",
        },
    )
    assert response.status_code == 200
    project = response.json()["project"]
    analyze = client.post(f"/api/projects/{project['project_id']}/analyze")
    assert analyze.status_code == 200
    approval = client.post(
        f"/api/projects/{project['project_id']}/approve",
        json={"decision": "approve", "feedback": ""},
    )
    assert approval.status_code == 200
    payload = approval.json()
    assert payload["success"] is True
    assert payload["decision"] in {"approve", "reject", "revise"}


def test_human_approval_reject_flow():
    response = client.post(
        "/api/projects",
        json={
            "name": "Billing Service",
            "description": "Design a billing service for an e-commerce platform.",
        },
    )
    project_id = response.json()["project"]["project_id"]
    client.post(f"/api/projects/{project_id}/analyze")
    response = client.post(
        f"/api/projects/{project_id}/approve",
        json={"decision": "reject", "feedback": "Please remove the payment service from the plan."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["decision"] == "reject"
    assert payload["status"] == "rejected"


def test_full_workflow_returns_structured_blueprint_and_trace():
    response = client.post(
        "/api/projects",
        json={
            "name": "ML Intrusion Detection Platform",
            "description": "Build a machine-learning based network intrusion detection platform with a FastAPI backend, PostgreSQL database and React dashboard.",
        },
    )
    assert response.status_code == 200
    project = response.json()["project"]
    assert project["status"] == "waiting_for_approval"
    assert project["workflow"]["approval_status"] == "pending"
    blueprint = project["final_blueprint"]
    for section in ("requirements", "architecture", "research", "development_plan", "testing_strategy", "security_considerations", "documentation_plan"):
        assert blueprint[section]
    assert project["workflow"]["log"][:2] == [
        "core: requirements analyzed",
        "architect: architecture produced",
    ]
    assert project["workflow"]["log"][-1] == "approval: waiting for human decision"


def test_revision_reruns_workflow_with_feedback():
    created = client.post(
        "/api/projects",
        json={"name": "Revision Service", "description": "Build a FastAPI service."},
    ).json()["project"]
    response = client.post(
        f"/api/projects/{created['project_id']}/revise",
        json={"decision": "revise", "feedback": "Add rate limiting."},
    )
    project = response.json()["project"]
    assert response.status_code == 200
    assert project["status"] == "waiting_for_approval"
    assert "rate limiting" in project["requirements"]["goal"]


def test_safety_and_mcp_tools():
    secret = "sk_live_1234567890"
    response = client.post(
        "/api/projects",
        json={"name": "Secret Service", "description": f"Never expose {secret} in output."},
    )
    assert response.status_code == 200
    assert secret not in response.text
    assert client.post("/api/repository/analyze", json={"repository_url": "https://example.com/nope"}).status_code == 400
    assert client.post("/api/projects", json={"name": "Unsafe", "description": "x", "local_path": "C:/Windows"}).status_code == 400
    assert inspect_repository_directory("../")["status"] == "blocked"
    assert validate_stack("FastAPI PostgreSQL")["status"] == "ok"
    assert validate_stack("")["status"] == "error"
