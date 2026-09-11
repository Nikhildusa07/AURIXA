from __future__ import annotations

from typing import Any

from app.ai.tools import tool_registry


def execute_tool(
    tool_name: str,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    tool = tool_registry.get(tool_name)

    if not isinstance(parameters, dict):
        raise ValueError("Tool parameters must be a dictionary.")

    try:
        result = tool.handler(parameters)
    except Exception as exc:
        return {
            "status": "failed",
            "tool_name": tool_name,
            "error": str(exc),
        }

    if not isinstance(result, dict):
        return {
            "status": "failed",
            "tool_name": tool_name,
            "error": "Tool returned an invalid response.",
        }

    return {
        "status": "success",
        "tool_name": tool_name,
        "result": result,
    }