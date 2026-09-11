from __future__ import annotations

from dataclasses import dataclass

from app.ai.agents.automation import decide_automation
from app.ai.agents.classifier import classify_request
from app.ai.agents.document import analyze_document
from app.ai.agents.research import research_knowledge
from app.ai.agents.validation import validate_result
from app.ai.evaluation.evaluator import evaluate_result
from app.ai.policies.invoice_policy import evaluate_invoice_policy
from app.ai.security.prompt_guard import validate_prompt
from app.ai.tools.runtime import execute_with_retry


@dataclass
class OrchestrationResult:
    request_type: str
    classification_confidence: float
    classification_reasoning: str
    action: str
    tool_name: str | None
    tool_result: dict | None
    research_result: dict | None
    document_result: dict | None
    policy_result: dict | None
    requires_approval: bool
    validation: dict
    evaluation: dict
    execution_trace: list[str]


def orchestrate_request(
    title: str,
    content: str,
) -> OrchestrationResult:

    # Security: validate input before AI processing
    title = validate_prompt(title)
    content = validate_prompt(content)

    execution_trace: list[str] = []

    # Step 1: Classifier Agent
    classification = classify_request(
        title=title,
        content=content,
    )

    execution_trace.append(
        f"ClassifierAgent: {classification.request_type}"
    )

    # Step 2: Automation Agent
    decision = decide_automation(
        request_type=classification.request_type,
        confidence=classification.confidence,
    )

    execution_trace.append(
        f"AutomationAgent: {decision.action}"
    )

    tool_result = None
    research_result = None
    document_result = None
    policy_result = None

    # Step 3: Document Agent
    if classification.request_type == "invoice_processing":

        document_analysis = analyze_document(
            text=content,
            document_type="invoice",
        )

        document_result = {
            "document_type": document_analysis.document_type,
            "extracted_fields": document_analysis.extracted_fields,
            "confidence": document_analysis.confidence,
            "missing_fields": document_analysis.missing_fields,
            "valid": document_analysis.valid,
        }

        execution_trace.append(
            "DocumentAgent: invoice analysis completed"
        )

        # Step 4: Invoice Policy Agent
        policy = evaluate_invoice_policy(
            extracted_fields=document_analysis.extracted_fields,
        )

        policy_result = {
            "invoice_number": policy.invoice_number,
            "total": policy.total,
            "threshold": policy.threshold,
            "requires_approval": policy.requires_approval,
            "action": policy.action,
            "reason": policy.reason,
        }

        execution_trace.append(
            f"InvoicePolicy: {policy.action}"
        )

        # Policy overrides automation decision
        if policy.requires_approval:

            decision.requires_approval = True
            decision.action = policy.action
            decision.tool_name = None

            execution_trace.append(
                "InvoicePolicy: human approval required"
            )

    # Step 5: Research Agent / RAG
    if classification.request_type == "knowledge_qa":

        research = research_knowledge(
            query=f"{title} {content}",
        )

        research_result = {
            "query": research.query,
            "context": research.context,
            "sources": research.sources,
            "confidence": research.confidence,
            "answer_allowed": research.answer_allowed,
        }

        execution_trace.append(
            "ResearchAgent: knowledge retrieval completed"
        )

    # Step 6: Tool Execution
    if (
        decision.tool_name
        and not decision.requires_approval
    ):

        parameters = decision.parameters.copy()

        # Use actual extracted invoice values
        if (
            decision.tool_name == "invoice_validation"
            and document_result
        ):

            extracted_fields = document_result[
                "extracted_fields"
            ]

            parameters.update(
                {
                    "invoice_number": extracted_fields.get(
                        "invoice_number",
                        "UNKNOWN",
                    ),
                    "total": extracted_fields.get(
                        "total",
                        0,
                    ),
                }
            )

        tool_result = execute_with_retry(
            tool_name=decision.tool_name,
            parameters=parameters,
        )

        execution_trace.append(
            f"ToolRuntime: {decision.tool_name} executed"
        )

    # Step 7: Validation Agent
    validation_input = {
        "action": decision.action,
        "tool_name": decision.tool_name,
        "tool_result": tool_result,
        "research_result": research_result,
        "document_result": document_result,
        "policy_result": policy_result,
    }

    validation = validate_result(
        result=validation_input,
        confidence=classification.confidence,
    )

    execution_trace.append(
        "ValidationAgent: "
        f"{'passed' if validation.valid else 'human review required'}"
    )

    # Final approval decision
    requires_approval = (
        decision.requires_approval
        or validation.requires_human
    )

    if (
        policy_result
        and policy_result["requires_approval"]
    ):
        requires_approval = True

    if requires_approval:
        execution_trace.append(
            "Orchestrator: human approval required"
        )
    else:
        execution_trace.append(
            "Orchestrator: workflow can continue automatically"
        )

    # Step 8: Evaluation Framework
    evaluation_input = {
        "request_type": classification.request_type,
        "classification_confidence": classification.confidence,
        "validation": {
            "valid": validation.valid,
        },
        "execution_trace": execution_trace,
    }

    evaluation = evaluate_result(
        result=evaluation_input,
    )

    execution_trace.append(
        f"EvaluationFramework: score={evaluation.score}"
    )

    return OrchestrationResult(
        request_type=classification.request_type,
        classification_confidence=classification.confidence,
        classification_reasoning=classification.reasoning,
        action=decision.action,
        tool_name=decision.tool_name,
        tool_result=tool_result,
        research_result=research_result,
        document_result=document_result,
        policy_result=policy_result,
        requires_approval=requires_approval,
        validation={
            "valid": validation.valid,
            "confidence": validation.confidence,
            "issues": validation.issues,
            "requires_human": validation.requires_human,
        },
        evaluation={
            "score": evaluation.score,
            "passed": evaluation.passed,
            "metrics": evaluation.metrics,
            "issues": evaluation.issues,
        },
        execution_trace=execution_trace,
    )