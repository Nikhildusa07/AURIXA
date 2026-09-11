from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class WorkflowDefinition:
    name: str
    description: str
    handler: Callable[..., Any]


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows: dict[
            str,
            WorkflowDefinition,
        ] = {}

    def register(
        self,
        workflow: WorkflowDefinition,
    ) -> None:
        if workflow.name in self._workflows:
            raise ValueError(
                f"Workflow already registered: "
                f"{workflow.name}"
            )

        self._workflows[workflow.name] = workflow

    def get(
        self,
        name: str,
    ) -> WorkflowDefinition:
        workflow = self._workflows.get(name)

        if workflow is None:
            raise KeyError(
                f"Unknown workflow: {name}"
            )

        return workflow

    def list_workflows(
        self,
    ) -> list[WorkflowDefinition]:
        return list(self._workflows.values())


workflow_registry = WorkflowRegistry()


def enterprise_request_workflow() -> dict[str, Any]:
    """
    Default AURIXA enterprise automation workflow.
    """

    return {
        "workflow": "enterprise_request_workflow",
        "status": "processed",
        "request_type": "general",
        "classification_confidence": 0.95,
        "requires_approval": False,
        "actions": [
            {
                "step": 1,
                "action": "request_classification",
                "status": "completed",
            },
            {
                "step": 2,
                "action": "priority_analysis",
                "status": "completed",
            },
            {
                "step": 3,
                "action": "automation_processing",
                "status": "completed",
            },
            {
                "step": 4,
                "action": "result_generation",
                "status": "completed",
            },
        ],
        "result": {
            "message": (
                "Enterprise request processed "
                "successfully by AURIXA."
            ),
            "automation_status": "completed",
        },
    }


def high_priority_workflow() -> dict[str, Any]:
    """
    Workflow for high and critical priority requests.
    """

    return {
        "workflow": "high_priority_workflow",
        "status": "processed",
        "request_type": "priority",
        "classification_confidence": 0.98,
        "requires_approval": True,
        "actions": [
            {
                "step": 1,
                "action": "priority_detection",
                "status": "completed",
            },
            {
                "step": 2,
                "action": "risk_analysis",
                "status": "completed",
            },
            {
                "step": 3,
                "action": "automation_processing",
                "status": "completed",
            },
            {
                "step": 4,
                "action": "human_approval",
                "status": "pending",
            },
        ],
        "result": {
            "message": (
                "High-priority request requires "
                "human approval."
            ),
            "automation_status": "waiting_approval",
        },
    }


workflow_registry.register(
    WorkflowDefinition(
        name="default_workflow",
        description=(
            "Default AURIXA enterprise workflow "
            "for automated request processing."
        ),
        handler=enterprise_request_workflow,
    )
)


workflow_registry.register(
    WorkflowDefinition(
        name="high_priority_workflow",
        description=(
            "AURIXA workflow for high-priority "
            "and critical enterprise requests "
            "requiring human approval."
        ),
        handler=high_priority_workflow,
    )
)