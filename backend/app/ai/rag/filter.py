from __future__ import annotations


def filter_results(
    results: list[dict],
    max_distance: float = 1.0,
    min_confidence: float = 0.15,
) -> list[dict]:
    filtered = [
        result
        for result in results
        if result.get("text", "").strip()
        and result.get("distance", float("inf")) <= max_distance
        and result.get("confidence", 0.0) >= min_confidence
    ]

    return sorted(
        filtered,
        key=lambda item: item.get("distance", float("inf")),
    )