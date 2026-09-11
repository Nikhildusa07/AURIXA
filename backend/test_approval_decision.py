import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.models.models import Approval, WorkflowExecution
from app.services.approval_service import (
    approve_approval,
    reject_approval,
)


async def main():
    async with AsyncSessionLocal() as db:

        # Replace this with a real pending approval ID
        approval_id = UUID(
            "23adcc2f-c6fa-4a61-a2e0-f73cd77cb562"
        )

        approval = await db.get(
            Approval,
            approval_id,
        )

        if approval is None:
            print("Approval not found.")
            return

        print("\nBefore Decision")
        print("Approval Status:", approval.status)
        print(
            "Workflow Execution:",
            approval.workflow_execution_id,
        )

        # APPROVE THE WORKFLOW
        result = await approve_approval(
            db=db,
            approval_id=approval.id,
            reviewer_comment="Approved after review.",
        )

        print("\nAfter Decision")
        print("Approval Status:", result.status)

        execution = await db.get(
            WorkflowExecution,
            result.workflow_execution_id,
        )

        print("Workflow Status:", execution.status)
        print("Workflow State:", execution.state)

        print("\nSUCCESS: Approval decision flow completed.")


if __name__ == "__main__":
    asyncio.run(main())