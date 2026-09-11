from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.ai.agents.classifier import classify_request
from app.ai.agents.research import research_knowledge
from app.ai.policies.invoice_policy import evaluate_invoice_policy
from app.services.notification_service import send_email_notification


@dataclass
class EmailTicketWorkflowResult:
    classification: dict[str, Any]
    urgency: str
    intent: str
    entities: dict[str, Any]
    knowledge: dict[str, Any] | None
    draft: str
    policy_valid: bool
    requires_approval: bool
    auto_sent: bool
    execution_trace: list[str]


def detect_urgency(
    title: str,
    content: str,
) -> str:
    text = f"{title} {content}".lower()

    high_keywords = [
        "urgent",
        "critical",
        "immediately",
        "emergency",
        "asap",
        "blocked",
        "failure",
    ]

    medium_keywords = [
        "important",
        "soon",
        "issue",
        "problem",
    ]

    if any(keyword in text for keyword in high_keywords):
        return "high"

    if any(keyword in text for keyword in medium_keywords):
        return "medium"

    return "low"


def detect_intent(
    request_type: str,
    title: str,
    content: str,
) -> str:
    text = f"{title} {content}".lower()

    if "refund" in text:
        return "refund_request"

    if "support" in text or "help" in text:
        return "support_request"

    if "complaint" in text:
        return "complaint"

    if request_type == "knowledge_qa":
        return "knowledge_request"

    if request_type == "invoice_processing":
        return "invoice_request"

    return "general_request"


def extract_entities(
    title: str,
    content: str,
) -> dict[str, Any]:
    text = f"{title}\n{content}"

    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
    )

    invoice_numbers = re.findall(
        r"\b(?:INV|Invoice)[-\s#]*([A-Za-z0-9-]+)",
        text,
        flags=re.IGNORECASE,
    )

    amounts = re.findall(
        r"(?:₹|\$|INR|USD)?\s?(\d+(?:,\d{3})*(?:\.\d{2})?)",
        text,
        flags=re.IGNORECASE,
    )

    return {
        "emails": emails,
        "invoice_numbers": invoice_numbers,
        "amounts": amounts,
    }


def create_draft(
    intent: str,
    urgency: str,
    title: str,
    knowledge_context: str | None = None,
) -> str:
    draft = (
        f"Subject: Re: {title}\n\n"
        "Hello,\n\n"
        f"We have received your {intent.replace('_', ' ')}. "
        f"Priority level: {urgency}.\n\n"
    )

    if knowledge_context:
        draft += (
            "Relevant information:\n"
            f"{knowledge_context}\n\n"
        )

    draft += (
        "Our AURIXA AI workflow has processed your request. "
        "We will take the appropriate next action.\n\n"
        "Regards,\n"
        "AURIXA Enterprise AI"
    )

    return draft


def validate_email_policy(
    urgency: str,
    intent: str,
) -> dict[str, Any]:
    high_risk_intents = [
        "refund_request",
        "complaint",
    ]

    requires_approval = (
        urgency == "high"
        or intent in high_risk_intents
    )

    return {
        "valid": True,
        "requires_approval": requires_approval,
        "reason": (
            "Human approval required for high-risk workflow."
            if requires_approval
            else "Safe for automated processing."
        ),
    }


def process_email_ticket(
    title: str,
    content: str,
    recipient_email: str | None = None,
) -> EmailTicketWorkflowResult:
    execution_trace: list[str] = []

    # Step 1: Classification
    classification = classify_request(
        title=title,
        content=content,
    )

    execution_trace.append(
        f"Classification: {classification.request_type}"
    )

    # Step 2: Urgency detection
    urgency = detect_urgency(
        title=title,
        content=content,
    )

    execution_trace.append(
        f"Urgency: {urgency}"
    )

    # Step 3: Intent detection
    intent = detect_intent(
        request_type=classification.request_type,
        title=title,
        content=content,
    )

    execution_trace.append(
        f"Intent: {intent}"
    )

    # Step 4: Entity extraction
    entities = extract_entities(
        title=title,
        content=content,
    )

    execution_trace.append(
        "EntityExtraction: completed"
    )

    # Step 5: Knowledge retrieval
    knowledge = None
    knowledge_context = None

    if classification.request_type == "knowledge_qa":
        research = research_knowledge(
            query=f"{title} {content}",
        )

        knowledge = {
            "query": research.query,
            "context": research.context,
            "sources": research.sources,
            "confidence": research.confidence,
            "answer_allowed": research.answer_allowed,
        }

        knowledge_context = research.context

        execution_trace.append(
            "KnowledgeRetrieval: completed"
        )

    # Step 6: Draft response
    draft = create_draft(
        intent=intent,
        urgency=urgency,
        title=title,
        knowledge_context=knowledge_context,
    )

    execution_trace.append(
        "DraftGeneration: completed"
    )

    # Step 7: Policy validation
    policy = validate_email_policy(
        urgency=urgency,
        intent=intent,
    )

    execution_trace.append(
        "PolicyValidation: completed"
    )

    requires_approval = policy["requires_approval"]
    auto_sent = False

    # Step 8: Auto-send or human approval
    if (
        not requires_approval
        and recipient_email
    ):
        email_result = send_email_notification(
            recipient_email=recipient_email,
            subject=f"Re: {title}",
            message=draft,
        )

        auto_sent = email_result.get(
            "success",
            False,
        )

        execution_trace.append(
            "EmailAutomation: auto-send attempted"
        )

    elif requires_approval:
        execution_trace.append(
            "HumanApproval: required"
        )

    else:
        execution_trace.append(
            "EmailAutomation: draft created"
        )

    return EmailTicketWorkflowResult(
        classification={
            "request_type": classification.request_type,
            "confidence": classification.confidence,
            "reasoning": classification.reasoning,
        },
        urgency=urgency,
        intent=intent,
        entities=entities,
        knowledge=knowledge,
        draft=draft,
        policy_valid=policy["valid"],
        requires_approval=requires_approval,
        auto_sent=auto_sent,
        execution_trace=execution_trace,
    )