import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.workflows.tasks import (
    start_workflow_task,
    complete_workflow_task,
)


async def main():
    task_id = UUID("913a1ba1-3e94-40af-86dd-a45eee3a20d0")

    async with AsyncSessionLocal() as db:

        task = await start_workflow_task(
            db=db,
            task_id=task_id,
        )

        print("After start:", task.status)

        task = await complete_workflow_task(
            db=db,
            task_id=task_id,
            output_data={
                "invoice_number": "INV-001",
                "validation": "successful",
            },
        )

        print("After completion:", task.status)
        print("Output:", task.output_data)


if __name__ == "__main__":
    asyncio.run(main())