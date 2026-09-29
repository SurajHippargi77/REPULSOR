from __future__ import annotations


def architecture_snapshot(description: str) -> dict:
    return {
        "summary": description,
        "layers": ["API", "service", "domain", "data", "observation"],
        "recommended": ["modular boundaries", "dependency constraints", "quality gates"],
    }
