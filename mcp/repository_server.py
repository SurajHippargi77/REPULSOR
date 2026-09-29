from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP
from tools.mcp_tools import inspect_repository_directory as _inspect_repository_directory

mcp = FastMCP("Repository MCP")


@mcp.tool()
def inspect_repository_directory(path: str) -> dict:
    """List files in a local repository while preventing path traversal beyond the workspace."""
    return _inspect_repository_directory(path)


if __name__ == "__main__":
    mcp.run()
