import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) and value.strip() else default


APP_NAME = "REPULSOR"
APP_VERSION = "0.1.0"
ENV_FILE = BASE_DIR / ".env"
GITHUB_API_BASE = "https://api.github.com"
ALLOWED_PROJECT_ROOT = BASE_DIR

SECRET_KEYS = {
    "OPENAI_API_KEY",
    "GROQ_API_KEY",
    "ANTHROPIC_API_KEY",
    "GITHUB_TOKEN",
    "DATABASE_URL",
    "SECRET_KEY",
}
