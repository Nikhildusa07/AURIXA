from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any


# Simple in-memory analytics storage.
# For production, this can later be replaced with database storage.
analytics_records: list[dict[str, Any]] = []


def start_performance_timer() -> float:
    """Start measuring execution time."""
    return perf_counter()


def record_ai_execution(
    operation: str,
    start_time: float,
    model: str = "local",
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost: float = 0.0,
    success: bool = True,
) -> dict[str, Any]:
    """Record AI execution performance and estimated cost."""

    execution_time_ms = round(
        (perf_counter() - start_time) * 1000,
        2,
    )

    record = {
        "operation": operation,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "estimated_cost": estimated_cost,
        "execution_time_ms": execution_time_ms,
        "success": success,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    analytics_records.append(record)

    return record


def get_performance_summary() -> dict[str, Any]:
    """Return cost and performance analytics summary."""

    total_operations = len(analytics_records)

    if total_operations == 0:
        return {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_execution_time_ms": 0.0,
            "total_estimated_cost": 0.0,
            "total_tokens": 0,
        }

    successful_operations = sum(
        1
        for record in analytics_records
        if record["success"]
    )

    failed_operations = (
        total_operations - successful_operations
    )

    total_execution_time = sum(
        record["execution_time_ms"]
        for record in analytics_records
    )

    total_cost = sum(
        record["estimated_cost"]
        for record in analytics_records
    )

    total_tokens = sum(
        record["total_tokens"]
        for record in analytics_records
    )

    return {
        "total_operations": total_operations,
        "successful_operations": successful_operations,
        "failed_operations": failed_operations,
        "average_execution_time_ms": round(
            total_execution_time / total_operations,
            2,
        ),
        "total_estimated_cost": round(
            total_cost,
            6,
        ),
        "total_tokens": total_tokens,
    }


def get_analytics_records() -> list[dict[str, Any]]:
    """Return all recorded analytics events."""

    return analytics_records.copy()