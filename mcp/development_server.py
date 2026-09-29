from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP
from tools.mcp_tools import validate_stack as _validate_stack

mcp = FastMCP("Development MCP")


@mcp.tool()
def validate_stack(requirements: str) -> dict:
    """Validate a software stack description and return safe recommendations."""
    return _validate_stack(requirements)


if __name__ == "__main__":
    mcp.run()
