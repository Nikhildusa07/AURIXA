from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AutomationDecision:
    action: str
    tool_name: str | None
    parameters: dict
    confidence: float
    requires_approval: bool


def decide_automation(
    request_type: str,
    confidence: float,
    requires_approval: bool = False,
    policy_action: str | None = None,
    parameters: dict | None = None,
) -> AutomationDecision:
    parameters = parameters or {}

    if confidence < 0.70:
        return AutomationDecision(
            action="request_human_review",
            tool_name=None,
            parameters=parameters,
            confidence=confidence,
            requires_approval=True,
        )

    if request_type == "invoice_processing":
        if requires_approval:
            return AutomationDecision(
                action=(
                    policy_action
                    or "request_human_approval"
                ),
                tool_name=None,
                parameters=parameters,
                confidence=confidence,
                requires_approval=True,
            )

        return AutomationDecision(
            action=(
                policy_action
                or "process_invoice"
            ),
            tool_name="invoice_validation",
            parameters=parameters,
            confidence=confidence,
            requires_approval=False,
        )

    if request_type == "customer_support":
        return AutomationDecision(
            action="draft_customer_response",
            tool_name="customer_response",
            parameters=parameters,
            confidence=confidence,
            requires_approval=True,
        )

    if request_type == "knowledge_qa":
        return AutomationDecision(
            action="retrieve_knowledge",
            tool_name=None,
            parameters=parameters,
            confidence=confidence,
            requires_approval=False,
        )

    return AutomationDecision(
        action="request_human_review",
        tool_name=None,
        parameters=parameters,
        confidence=confidence,
        requires_approval=True,
    )