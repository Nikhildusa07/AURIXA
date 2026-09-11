import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.workflows.engine import execute_workflow


async def main():
    execution_id = UUID(
        "01657d21-c917-47e1-a5f5-3003e40291b5"
    )

    async with AsyncSessionLocal() as db:
        execution = await db.get(
            __import__(
                "app.models.models",
                fromlist=["WorkflowExecution"],
            ).WorkflowExecution,
            execution_id,
        )

        # Reset only for this test if necessary
        if execution.status != "pending":
            execution.status = "pending"
            execution.current_step = 0
            execution.error_message = None
            execution.completed_at = None
            await db.commit()

        execution = await execute_workflow(
            db=db,
            execution_id=execution_id,
        )

        print("Execution ID:", execution.id)
        print("Status:", execution.status)
        print("Current Step:", execution.current_step)
        print("State:", execution.state)
        print("Error:", execution.error_message)


if __name__ == "__main__":
    asyncio.run(main())