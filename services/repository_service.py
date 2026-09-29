from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import requests

from config import ALLOWED_PROJECT_ROOT, GITHUB_API_BASE


class RepositoryInputError(ValueError):
    """Raised when repository input is unsafe or malformed."""


def normalize_repository_url(repository_url: str | None) -> str | None:
    if not repository_url:
        return None
    candidate = repository_url.strip()
    parsed = urlparse(candidate if "://" in candidate else f"https://{candidate}")
    if parsed.netloc.lower() != "github.com":
        raise RepositoryInputError("Only public github.com repositories are supported.")
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) != 2 or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", part) for part in parts):
        raise RepositoryInputError("Repository URL must look like https://github.com/owner/repository.")
    return "/".join(parts)


def fetch_public_repo_summary(repository_url: str | None) -> dict:
    repo_path = normalize_repository_url(repository_url)
    if not repo_path:
        raise RepositoryInputError("A repository URL is required.")
    owner, repo = repo_path.split("/", 1)
    api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    response = requests.get(api_url, headers={"Accept": "application/vnd.github+json"}, timeout=15)
    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        return {"status": "unavailable", "repository": repo, "summary": "GitHub API rate limit reached; retry later."}
    if response.status_code != 200:
        return {"status": "unavailable", "repository": repo, "summary": f"GitHub API status: {response.status_code}", "details": {"owner": owner}}
    data = response.json()
    contents_response = requests.get(
        f"{api_url}/contents",
        headers={"Accept": "application/vnd.github+json"},
        timeout=15,
    )
    top_level_entries = []
    important_files = []
    if contents_response.status_code == 200 and isinstance(contents_response.json(), list):
        top_level_entries = [item.get("name") for item in contents_response.json() if item.get("name")]
        important_files = [
            name for name in top_level_entries
            if name.lower() in {"readme.md", "pyproject.toml", "package.json", "requirements.txt", "dockerfile", ".env.example"}
        ]
    languages_response = requests.get(f"{api_url}/languages", timeout=15)
    languages = languages_response.json() if languages_response.status_code == 200 else {}
    technologies = list(languages.keys())[:8]
    return {
        "status": "ok",
        "repository": repo,
        "owner": owner,
        "summary": data.get("description") or "No description provided.",
        "language": data.get("language") or "Unknown",
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "default_branch": data.get("default_branch", "main"),
        "topics": data.get("topics", [])[:10],
        "technologies": technologies or ([data.get("language")] if data.get("language") else []),
        "project_structure": top_level_entries,
        "important_files": important_files,
        "observations": [
            f"Public repository has {data.get('stargazers_count', 0)} stars and {data.get('forks_count', 0)} forks.",
            f"Default branch is {data.get('default_branch', 'main')}.",
            f"Top-level inspection found {len(top_level_entries)} entries.",
        ],
        "recommendations": [
            "Review the detected dependency and configuration files before implementation.",
            "Use the default branch as the baseline for architecture comparison.",
        ],
        "url": data.get("html_url"),
        "clone_url": data.get("clone_url"),
        "api_url": api_url,
    }


def analyze_local_repository(local_path: str | None) -> dict:
    if not local_path:
        raise RepositoryInputError("A local repository path is required.")
    path = Path(local_path).expanduser().resolve()
    try:
        path.relative_to(ALLOWED_PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise RepositoryInputError("Local repository path must stay within the project workspace.") from exc
    if not path.exists():
        return {"repository": path.name, "summary": "Local path does not exist."}
    if path.is_file():
        return {"repository": path.name, "summary": "Path points to a file, not a directory."}

    entries = []
    for child in sorted(path.iterdir())[:50]:
        entries.append(child.name)

    return {
        "repository": path.name,
        "summary": "Local repository inspected successfully.",
        "path": str(path),
        "entry_count": len(entries),
        "top_level_entries": entries,
        "language_hints": ["Python", "JavaScript", "TypeScript", "YAML", "Docker"],
    }
