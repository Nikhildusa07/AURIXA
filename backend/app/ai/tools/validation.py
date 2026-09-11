from __future__ import annotations

from typing import Any


def validate_tool_parameters(
    parameters: dict[str, Any],
) -> bool:
    return isinstance(parameters, dict)


def validate_tool_result(
    result: Any,
) -> bool:
    return isinstance(result, dict)