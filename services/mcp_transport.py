from __future__ import annotations

import asyncio
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import BASE_DIR

SERVER_SCRIPTS = {
    "research": BASE_DIR / "mcp" / "research_server.py",
    "repository": BASE_DIR / "mcp" / "repository_server.py",
    "development": BASE_DIR / "mcp" / "development_server.py",
}


async def _call_mcp_tool(server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
    script = SERVER_SCRIPTS[server_name]
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(script)],
        cwd=BASE_DIR,
    )
    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                tool_name,
                arguments=arguments,
                read_timeout_seconds=timedelta(seconds=30),
            )
            if result.isError:
                raise RuntimeError(f"MCP tool {tool_name} returned an error")
            if result.structuredContent is not None:
                value = result.structuredContent
                if isinstance(value, dict) and set(value) == {"result"}:
                    return value["result"]
                return value
            if len(result.content) == 1 and hasattr(result.content[0], "text"):
                text = result.content[0].text
                try:
                    return json.loads(text)
                except (TypeError, json.JSONDecodeError):
                    return text
            return [item.model_dump() for item in result.content]


def call_mcp_tool(server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
    """Call a local MCP server over official stdio transport from sync workflow code."""
    if server_name not in SERVER_SCRIPTS:
        raise ValueError(f"Unknown MCP server: {server_name}")
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_call_mcp_tool(server_name, tool_name, arguments))
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, _call_mcp_tool(server_name, tool_name, arguments)).result()
