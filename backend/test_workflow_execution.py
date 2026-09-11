import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.models.models import Request
from app.workflows.engine import create_workflow_execution


async def main():
    async with AsyncSessionLocal() as db:
        request = await db.get(
            Request,
            UUID("b73262a2-55b6-40e3-80e0-2f92e746ccf1"),
        )

        if request is None:
            print("Request not found")
            return

        execution = await create_workflow_execution(
            db=db,
            workflow_name="invoice_processing",
            request_id=request.id,
        )

        print({
            "execution_id": str(execution.id),
            "workflow_id": str(execution.workflow_id),
            "request_id": str(execution.request_id),
            "status": execution.status,
            "state": execution.state,
        })


if __name__ == "__main__":
    asyncio.run(main())