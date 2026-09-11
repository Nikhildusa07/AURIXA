import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.models.models import Approval, WorkflowExecution
from app.services.approval_service import reject_approval


async def main():
    async with AsyncSessionLocal() as db:

        # Replace with a NEW pending approval ID
        approval_id = UUID("1e9dfbe5-0883-4497-8663-388bc829f99e")

        approval = await db.get(
            Approval,
            approval_id,
        )

        if approval is None:
            print("Approval not found.")
            return

        print("\nBefore Rejection")
        print("Approval Status:", approval.status)
        print("Workflow Execution:", approval.workflow_execution_id)

        result = await reject_approval(
            db=db,
            approval_id=approval.id,
            reviewer_comment="Rejected after human review.",
        )

        print("\nAfter Rejection")
        print("Approval Status:", result.status)

        execution = await db.get(
            WorkflowExecution,
            result.workflow_execution_id,
        )

        print("Workflow Status:", execution.status)
        print("Workflow State:", execution.state)

        print("\nSUCCESS: Rejection flow completed.")


if __name__ == "__main__":
    asyncio.run(main())