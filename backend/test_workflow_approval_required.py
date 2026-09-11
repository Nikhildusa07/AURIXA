import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.models.models import Request
from app.workflows.engine import (
    create_workflow_execution,
    execute_workflow,
)
from app.workflows.registry import (
    WorkflowDefinition,
    workflow_registry,
)


def approval_required_workflow():
    return {
        "request_type": "high_risk_invoice",
        "action": "process_high_value_invoice",
        "requires_approval": True,
        "reason": "High-value invoice requires human approval.",
        "amount": 500000,
    }


async def main():
    workflow_name = "approval_test_workflow"

    try:
        workflow_registry.register(
            WorkflowDefinition(
                name=workflow_name,
                description="Workflow used to test human approval.",
                handler=approval_required_workflow,
            )
        )
    except ValueError:
        pass

    async with AsyncSessionLocal() as db:
        request_id = UUID(
            "b73262a2-55b6-40e3-80e0-2f92e746ccf1"
        )

        request = await db.get(
            Request,
            request_id,
        )

        if request is None:
            print("Request not found.")
            return

        execution = await create_workflow_execution(
            db=db,
            workflow_name=workflow_name,
            request_id=request.id,
        )

        print("Execution ID:", execution.id)
        print("Initial Status:", execution.status)

        execution = await execute_workflow(
            db=db,
            execution_id=execution.id,
        )

        print("\nFinal Status:", execution.status)
        print("State:", execution.state)
        print("Error:", execution.error_message)

        if execution.status == "waiting_approval":
            print(
                "\nSUCCESS: Workflow is waiting for human approval."
            )
        else:
            print(
                "\nFAILED: Workflow did not enter "
                "waiting_approval state."
            )


if __name__ == "__main__":
    asyncio.run(main())