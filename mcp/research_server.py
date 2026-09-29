from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP
from tools.mcp_tools import fetch_research_summary as _fetch_research_summary

mcp = FastMCP("Research MCP")


@mcp.tool()
def fetch_research_summary(topic: str) -> str:
    """Return a concise research summary for a software engineering topic."""
    return _fetch_research_summary(topic)


if __name__ == "__main__":
    mcp.run()
