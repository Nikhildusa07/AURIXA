from app.workflows.registry import (
    WorkflowDefinition,
    workflow_registry,
)

from app.ai.agents.orchestrator import orchestrate_request


def invoice_workflow() -> dict:
    """
    Execute the invoice processing workflow using
    the AURIXA AI orchestrator.
    """

    result = orchestrate_request(
        title="Invoice Processing Request",
        content="Please verify and process the customer invoice.",
    )

    return {
        "request_type": result.request_type,
        "classification_confidence": result.classification_confidence,
        "action": result.action,
        "tool_name": result.tool_name,
        "tool_result": result.tool_result,
        "requires_approval": result.requires_approval,
        "validation": result.validation,
    }


workflow_registry.register(
    WorkflowDefinition(
        name="invoice_processing",
        description=(
            "Processes and validates an invoice request "
            "using the AI orchestrator."
        ),
        handler=invoice_workflow,
    )
)