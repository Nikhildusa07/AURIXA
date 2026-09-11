from __future__ import annotations

from typing import Any

from app.ai.tools.executor import execute_tool


def execute_with_retry(
    tool_name: str,
    parameters: dict[str, Any],
    max_attempts: int = 3,
) -> dict[str, Any]:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    last_result: dict[str, Any] = {}

    for attempt in range(1, max_attempts + 1):
        last_result = execute_tool(
            tool_name=tool_name,
            parameters=parameters,
        )

        if last_result.get("status") == "success":
            return {
                **last_result,
                "attempts": attempt,
            }

    return {
        **last_result,
        "attempts": max_attempts,
    }