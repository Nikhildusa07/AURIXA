from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class PromptGuardResult:
    safe: bool
    risk_level: str
    blocked: bool
    reasons: list[str]
    sanitized_text: str


INJECTION_PATTERNS = [
    (
        "ignore_previous_instructions",
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    ),
    (
        "system_prompt_extraction",
        r"(show|reveal|print|give|tell).{0,50}(system\s+prompt|hidden\s+instructions)",
    ),
    (
        "role_override",
        r"(you\s+are\s+now|act\s+as|pretend\s+to\s+be).{0,50}(system|developer|administrator|root)",
    ),
    (
        "instruction_override",
        r"disregard\s+(all\s+)?(rules|instructions|policies)",
    ),
    (
        "prompt_injection",
        r"(override|bypass|disable)\s+(security|safety|rules|restrictions)",
    ),
]


def check_prompt(text: str) -> PromptGuardResult:
    if not isinstance(text, str):
        raise ValueError("Prompt must be a string.")

    cleaned_text = text.strip()

    if not cleaned_text:
        return PromptGuardResult(
            safe=True,
            risk_level="none",
            blocked=False,
            reasons=[],
            sanitized_text="",
        )

    reasons: list[str] = []

    for pattern_name, pattern in INJECTION_PATTERNS:
        if re.search(
            pattern,
            cleaned_text,
            flags=re.IGNORECASE,
        ):
            reasons.append(pattern_name)

    blocked = len(reasons) > 0

    if blocked:
        risk_level = "high"
    else:
        risk_level = "none"

    return PromptGuardResult(
        safe=not blocked,
        risk_level=risk_level,
        blocked=blocked,
        reasons=reasons,
        sanitized_text=cleaned_text,
    )


def validate_prompt(text: str) -> str:
    result = check_prompt(text)

    if result.blocked:
        raise ValueError(
            "Potential prompt injection detected: "
            + ", ".join(result.reasons)
        )

    return result.sanitized_text