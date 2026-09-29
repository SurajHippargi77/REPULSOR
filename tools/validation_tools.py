from __future__ import annotations


def validate_input(value: str) -> dict:
    redacted = value.replace("sk_live_", "[REDACTED]").replace("ghp_", "[REDACTED]")
    return {"status": "ok", "sanitized": redacted}
