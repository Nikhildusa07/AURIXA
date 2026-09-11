import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.models.models import Request
from app.workflows.engine import (
    create_workflow_execution,
    execute_workflow,
)


async def main():
    async with AsyncSessionLocal() as db:

        # Get an existing request
        request = await db.get(
            Request,
            UUID("b73262a2-55b6-40e3-80e0-2f92e746ccf1"),
        )

        if request is None:
            print("Request not found.")
            return

        # Create a fresh workflow execution
        execution = await create_workflow_execution(
            db=db,
            workflow_name="invoice_processing",
            request_id=request.id,
        )

        print("New Execution ID:", execution.id)
        print("Initial Status:", execution.status)

        # Execute the fresh workflow
        result = await execute_workflow(
            db=db,
            execution_id=execution.id,
        )

        print("\nExecution ID:", result.id)
        print("Workflow Status:", result.status)
        print("State:", result.state)

        if result.status == "waiting_approval":
            print("\nSUCCESS: Human approval was created.")
            print("Approval ID:", result.state.get("approval_id"))
            print("Approval Status:", result.state.get("approval_status"))
        else:
            print("\nWorkflow completed automatically.")


if __name__ == "__main__":
    asyncio.run(main())