from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClassificationResult:
    request_type: str
    confidence: float
    reasoning: str


def classify_request(
    title: str,
    content: str,
) -> ClassificationResult:
    text = f"{title} {content}".lower()

    # Knowledge and policy questions must be checked first.
    if any(
        keyword in text
        for keyword in (
            "policy",
            "procedure",
            "knowledge",
            "information",
            "what is",
            "what are",
            "how does",
            "how do",
        )
    ):
        return ClassificationResult(
            request_type="knowledge_qa",
            confidence=0.90,
            reasoning=(
                "Request appears to ask for enterprise knowledge "
                "or policy information."
            ),
        )

    # Financial processing requests.
    if any(
        keyword in text
        for keyword in (
            "invoice",
            "billing",
            "payment",
            "purchase order",
        )
    ):
        return ClassificationResult(
            request_type="invoice_processing",
            confidence=0.95,
            reasoning=(
                "Request contains financial document or "
                "payment-related terms."
            ),
        )

    # Customer support requests.
    if any(
        keyword in text
        for keyword in (
            "customer",
            "support",
            "complaint",
            "ticket",
        )
    ):
        return ClassificationResult(
            request_type="customer_support",
            confidence=0.90,
            reasoning=(
                "Request contains customer support-related terms."
            ),
        )

    return ClassificationResult(
        request_type="general",
        confidence=0.60,
        reasoning="No specialized request category matched.",
    )