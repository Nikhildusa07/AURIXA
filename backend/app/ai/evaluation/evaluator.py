from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationResult:
    score: float
    passed: bool
    metrics: dict[str, float]
    issues: list[str]


def evaluate_result(
    result: dict[str, Any],
    expected_request_type: str | None = None,
    minimum_confidence: float = 0.70,
) -> EvaluationResult:
    """
    Evaluate an AI orchestration result using simple,
    measurable quality metrics.
    """

    metrics: dict[str, float] = {}
    issues: list[str] = []

    # -----------------------------------
    # 1. Classification Accuracy
    # -----------------------------------

    request_type = result.get("request_type")

    if expected_request_type is not None:
        classification_score = (
            1.0
            if request_type == expected_request_type
            else 0.0
        )

        if classification_score == 0.0:
            issues.append(
                "Request classification does not match expected type."
            )
    else:
        classification_score = (
            1.0
            if request_type
            else 0.0
        )

    metrics["classification"] = classification_score

    # -----------------------------------
    # 2. Confidence Score
    # -----------------------------------

    confidence = result.get(
        "classification_confidence",
        0.0,
    )

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(
        0.0,
        min(confidence, 1.0),
    )

    confidence_score = (
        1.0
        if confidence >= minimum_confidence
        else confidence / minimum_confidence
    )

    if confidence < minimum_confidence:
        issues.append(
            f"Confidence below minimum threshold: "
            f"{minimum_confidence}"
        )

    metrics["confidence"] = confidence_score

    # -----------------------------------
    # 3. Validation Quality
    # -----------------------------------

    validation = result.get("validation")

    if isinstance(validation, dict):
        validation_valid = validation.get(
            "valid",
            False,
        )

        validation_score = (
            1.0
            if validation_valid
            else 0.0
        )

        if not validation_valid:
            issues.append(
                "Validation agent marked the result as invalid."
            )
    else:
        validation_score = 0.0

        issues.append(
            "Validation result is missing."
        )

    metrics["validation"] = validation_score

    # -----------------------------------
    # 4. Execution Trace
    # -----------------------------------

    execution_trace = result.get(
        "execution_trace",
        [],
    )

    trace_score = (
        1.0
        if isinstance(execution_trace, list)
        and len(execution_trace) > 0
        else 0.0
    )

    if trace_score == 0.0:
        issues.append(
            "Execution trace is missing."
        )

    metrics["trace"] = trace_score

    # -----------------------------------
    # Final Score
    # -----------------------------------

    score = round(
        sum(metrics.values()) / len(metrics),
        2,
    )

    passed = score >= 0.70

    return EvaluationResult(
        score=score,
        passed=passed,
        metrics=metrics,
        issues=issues,
    )