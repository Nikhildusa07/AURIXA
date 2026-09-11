import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.workflows.engine import (
    start_workflow_execution,
    complete_workflow_execution,
)


async def main():
    execution_id = UUID(
        "df8a16d5-f641-42df-8d2e-04d9de792a23"
    )

    async with AsyncSessionLocal() as db:
        execution = await start_workflow_execution(
            db,
            execution_id,
        )

        print("After start:", execution.status)

        execution = await complete_workflow_execution(
            db,
            execution_id,
            {"result": "Invoice workflow completed"},
        )

        print("After completion:", execution.status)
        print("State:", execution.state)


if __name__ == "__main__":
    asyncio.run(main())