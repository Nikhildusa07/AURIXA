from types import SimpleNamespace
from unittest.mock import patch

from app.ai.agents.orchestrator import orchestrate_request


def test_general_request_orchestration():
    result = orchestrate_request(
        title="General Request",
        content="Please process this request.",
    )

    assert result.request_type is not None
    assert result.action is not None
    assert isinstance(result.execution_trace, list)
    assert len(result.execution_trace) > 0


@patch("app.ai.agents.orchestrator.evaluate_invoice_policy")
@patch("app.ai.agents.orchestrator.analyze_document")
def test_invoice_request_uses_document_and_policy_agents(
    mock_document,
    mock_policy,
):
    mock_document.return_value = SimpleNamespace(
        document_type="invoice",
        extracted_fields={
            "invoice_number": "INV-001",
            "total": 500,
        },
        confidence=0.95,
        missing_fields=[],
        valid=True,
    )

    mock_policy.return_value = SimpleNamespace(
        invoice_number="INV-001",
        total=500,
        threshold=1000,
        requires_approval=False,
        action="auto_process",
        reason="Invoice is within the approval threshold.",
    )

    result = orchestrate_request(
        title="Invoice INV-001",
        content="Invoice total is 500",
    )

    assert result.request_type == "invoice_processing"
    assert result.document_result is not None
    assert result.policy_result is not None

    mock_document.assert_called_once()
    mock_policy.assert_called_once()


@patch("app.ai.agents.orchestrator.evaluate_invoice_policy")
@patch("app.ai.agents.orchestrator.analyze_document")
def test_high_value_invoice_requires_approval(
    mock_document,
    mock_policy,
):
    mock_document.return_value = SimpleNamespace(
        document_type="invoice",
        extracted_fields={
            "invoice_number": "INV-999",
            "total": 10000,
        },
        confidence=0.95,
        missing_fields=[],
        valid=True,
    )

    mock_policy.return_value = SimpleNamespace(
        invoice_number="INV-999",
        total=10000,
        threshold=1000,
        requires_approval=True,
        action="human_approval",
        reason="Invoice exceeds the approval threshold.",
    )

    result = orchestrate_request(
        title="High Value Invoice",
        content="Invoice INV-999 total is 10000",
    )

    assert result.requires_approval is True
    assert result.policy_result is not None
    assert result.policy_result["requires_approval"] is True

    assert "Orchestrator: human approval required" in (
        result.execution_trace
    )


def test_knowledge_request_uses_research_agent():
    result = orchestrate_request(
        title="Company Knowledge",
        content="What information is available in the knowledge base?",
    )

    assert result.request_type == "knowledge_qa"
    assert result.research_result is not None

    assert any(
        "ResearchAgent" in step
        for step in result.execution_trace
    )


def test_complete_orchestration_has_validation_and_trace():
    result = orchestrate_request(
        title="Process Request",
        content="Please classify and process this request.",
    )

    assert "valid" in result.validation
    assert "confidence" in result.validation
    assert "issues" in result.validation
    assert "requires_human" in result.validation

    assert any(
        "ClassifierAgent" in step
        for step in result.execution_trace
    )

    assert any(
        "AutomationAgent" in step
        for step in result.execution_trace
    )

    assert any(
        "ValidationAgent" in step
        for step in result.execution_trace
    )