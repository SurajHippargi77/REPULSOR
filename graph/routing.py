from __future__ import annotations

from typing import Any


def decide_next_step(state: dict[str, Any]) -> str:
    status = state.get("approval_status")
    if status == "rejected":
        return "end"
    if status == "revised":
        return "research"
    return "human_approval"
