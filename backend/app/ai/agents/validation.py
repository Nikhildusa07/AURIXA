from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    confidence: float
    issues: list[str]
    requires_human: bool


def validate_result(
    result: dict,
    confidence: float,
) -> ValidationResult:
    issues: list[str] = []

    if not isinstance(result, dict):
        issues.append("Result must be a dictionary.")

    if isinstance(result, dict) and not result:
        issues.append("Result is empty.")

    if confidence < 0.70:
        issues.append("Confidence is below the safe threshold.")

    valid = not issues

    return ValidationResult(
        valid=valid,
        confidence=confidence,
        issues=issues,
        requires_human=not valid,
    )