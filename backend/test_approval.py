import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.services.approval_service import create_approval


async def main():
    async with AsyncSessionLocal() as db:
        approval = await create_approval(
            db=db,
            workflow_execution_id=UUID(
                "df8a16d5-f641-42df-8d2e-04d9de792a23"
            ),
            reason="Invoice processing requires human verification.",
            recommendation={
                "action": "process_invoice",
                "tool": "invoice_validation",
            },
            requested_by=UUID(
                "1a9fcaec-9e9e-44fd-9885-acf790761557"
            ),
        )

        print({
            "approval_id": str(approval.id),
            "workflow_execution_id": str(
                approval.workflow_execution_id
            ),
            "status": approval.status,
            "reason": approval.reason,
            "recommendation": approval.recommendation,
        })


if __name__ == "__main__":
    asyncio.run(main())