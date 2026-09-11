import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.workflows.engine import retry_workflow_execution


async def main():
    execution_id = UUID(
        "df8a16d5-f641-42df-8d2e-04d9de792a23"
    )

    async with AsyncSessionLocal() as db:
        execution = await retry_workflow_execution(
            db=db,
            execution_id=execution_id,
        )

        print("Status after retry:", execution.status)
        print("Current step:", execution.current_step)
        print("Error:", execution.error_message)
        print("Completed at:", execution.completed_at)


if __name__ == "__main__":
    asyncio.run(main())