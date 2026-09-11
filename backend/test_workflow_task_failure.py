import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.workflows.tasks import (
    create_workflow_task,
    start_workflow_task,
    fail_workflow_task,
    retry_workflow_task,
)


async def main():
    execution_id = UUID(
        "01657d21-c917-47e1-a5f5-3003e40291b5"
    )

    async with AsyncSessionLocal() as db:

        # Create a new task for failure testing
        task = await create_workflow_task(
            db=db,
            execution_id=execution_id,
            task_name="Invoice External API Check",
            task_type="api_call",
        )

        print("Created:", task.status)
        print("Task ID:", task.id)

        # Start the task
        task = await start_workflow_task(
            db=db,
            task_id=task.id,
        )

        print("After start:", task.status)

        # Simulate failure
        task = await fail_workflow_task(
            db=db,
            task_id=task.id,
            error_message="External invoice API unavailable.",
        )

        print("After failure:", task.status)
        print("Error:", task.error_message)

        # Retry the failed task
        task = await retry_workflow_task(
            db=db,
            task_id=task.id,
        )

        print("After retry:", task.status)
        print("Retry count:", task.retry_count)
        print("Error after retry:", task.error_message)


if __name__ == "__main__":
    asyncio.run(main())