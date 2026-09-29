# REPULSOR

Reasoning & Engineering Platform for Unified Software Operations and Research

## Problem
Software teams often need a coordinated way to turn an idea, repository, or vague requirement into an actionable engineering blueprint. They need architecture guidance, repository intelligence, research synthesis, implementation planning, testing validation, security review, and human oversight without losing control of the workflow.

## Solution
REPULSOR is a multi-agent engineering platform built with FastAPI, LangGraph, MCP, and structured project state. A project request runs through a compiled graph of specialist agents and stops at a real human approval gate before it can be finalized.

## Architecture
REPULSOR is organized around a shared project workflow and specialized agents:

- Core orchestrator: manages the lifecycle and state transitions.
- Architect agent: proposes structure, components, and system boundaries.
- Research agent: gathers domain and repository insights.
- Code intelligence agent: inspects code and repository signals.
- Implementation agent: converts architecture into engineering tasks.
- Test engine agent: defines validation and regression checks.
- Security agent: reviews risk and guardrails.
- Documentation agent: writes maintainable operational documentation.

## Agents
Each agent receives the prior state and returns structured JSON. When `GROQ_API_KEY` is configured, the agent calls `ChatGroq`; otherwise it uses an explicit, input-derived development fallback and records that mode in `_execution`. No fallback is presented as an LLM response.

## LangGraph
The workflow is a compiled `StateGraph` in `graph/workflow.py`. Its execution path is:

```text
User -> Core -> Architect -> Research -> Code Intelligence -> Implementation
  -> Testing -> Security -> Documentation -> Review -> Approval -> Finalize
```

The initial graph stops at `waiting_for_approval`. Approval resumes a second graph: approve finalizes, reject stops, and revise re-runs the main graph with feedback.

It supports:

- requirement analysis
- architecture review
- research and repository intelligence
- implementation planning
- testing
- security
- documentation
- quality review
- approval

## MCP
REPULSOR includes MCP server components for developer workflows:

- Research MCP: research and ecosystem-oriented tool calls.
- Repository MCP: safe repository inspection and directory listing.
- Development MCP: stack validation and implementation guidance.

The workflow calls the reusable implementations behind these registered tools. Servers can be started directly with `python mcp/research_server.py`, `python mcp/repository_server.py`, or `python mcp/development_server.py`. All MCP access is constrained to safe operations and avoids destructive commands.

## Repository Intelligence
The application supports both:

- public GitHub URL analysis
- local repository inspection

It calls the GitHub REST API for repository metadata, languages, and top-level contents. The result includes owner, repository name, description, language, default branch, technologies, important files, structure, observations, and recommendations. API errors and rate limits are reported without fabricated repository data.

## Human-in-the-Loop
The human approval step is a first-class part of the workflow. The engineer can:

- approve the proposal
- reject it
- request changes with feedback

The result changes the workflow state and prevents the system from silently continuing after a rejected or revised plan.

## Guardrails
REPULSOR includes practical safeguards:

- redact secret-bearing text before persistence, workflow execution, or output
- restrict destructive operations and path traversal
- avoid exposing secrets in generated summaries
- validate user input and repository paths before processing

## API
The server exposes developer-oriented endpoints:

- GET /api/health
- POST /api/projects
- GET /api/projects/{project_id}
- POST /api/projects/{project_id}/analyze
- POST /api/projects/{project_id}/research
- POST /api/projects/{project_id}/architecture
- POST /api/projects/{project_id}/generate-plan
- POST /api/projects/{project_id}/approve
- POST /api/projects/{project_id}/revise
- POST /api/repository/analyze
- GET /api/projects/{project_id}/status

## Frontend
The frontend is a lightweight dashboard that surfaces:

- dashboard overview
- project creation
- repository intelligence
- agent activity
- approval center
- final blueprint summary

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the FastAPI app:

```bash
python main.py
```

4. Access the dashboard at:

```text
http://127.0.0.1:8000/
```

## Environment variables
Copy `.env.example` to a local `.env` or export the variables directly. `GROQ_API_KEY` enables the real LLM path; without it, the development fallback remains executable and is labeled in every agent result. Do not hard-code secrets.

## Usage
Example:

```json
{
  "name": "Network Intrusion Detection API",
  "description": "I want to build a network intrusion detection API using Python, FastAPI and machine learning."
}
```

You can also provide a public repository URL for analysis:

```json
{
  "repository_url": "https://github.com/microsoft/vscode"
}
```

## Testing
Run the automated test suite:

```bash
pytest -q
```

## Project structure

```text
REPULSOR/
├── main.py
├── config.py
├── models.py
├── requirements.txt
├── README.md
├── agents/
├── graph/
├── mcp/
├── tools/
├── api/
├── services/
├── frontend/
├── tests/
└── ...
```

## Current limitations
- Project storage is in-memory and is lost when the process stops.
- LLM execution requires a valid `GROQ_API_KEY`; fallback mode is deterministic and not a substitute for model evaluation.
- GitHub analysis uses unauthenticated REST requests and is subject to rate limits.
- Repository inspection is metadata and top-level contents analysis, not full static analysis.
- The dashboard is a lightweight development UI, not an authenticated production console.
