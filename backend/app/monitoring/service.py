from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Approval,
    Request,
    WorkflowExecution,
)


async def get_monitoring_summary(
    db: AsyncSession,
) -> dict:
    total_requests = await db.scalar(
        select(func.count()).select_from(Request)
    )

    pending_requests = await db.scalar(
        select(func.count())
        .select_from(Request)
        .where(Request.status == "pending")
    )

    completed_requests = await db.scalar(
        select(func.count())
        .select_from(Request)
        .where(Request.status == "completed")
    )

    failed_requests = await db.scalar(
        select(func.count())
        .select_from(Request)
        .where(Request.status == "failed")
    )

    total_workflows = await db.scalar(
        select(func.count())
        .select_from(WorkflowExecution)
    )

    running_workflows = await db.scalar(
        select(func.count())
        .select_from(WorkflowExecution)
        .where(WorkflowExecution.status == "running")
    )

    waiting_approval = await db.scalar(
        select(func.count())
        .select_from(WorkflowExecution)
        .where(
            WorkflowExecution.status
            == "waiting_approval"
        )
    )

    completed_workflows = await db.scalar(
        select(func.count())
        .select_from(WorkflowExecution)
        .where(WorkflowExecution.status == "completed")
    )

    failed_workflows = await db.scalar(
        select(func.count())
        .select_from(WorkflowExecution)
        .where(WorkflowExecution.status == "failed")
    )

    total_approvals = await db.scalar(
        select(func.count())
        .select_from(Approval)
    )

    pending_approvals = await db.scalar(
        select(func.count())
        .select_from(Approval)
        .where(Approval.status == "pending")
    )

    approved_approvals = await db.scalar(
        select(func.count())
        .select_from(Approval)
        .where(Approval.status == "approved")
    )

    rejected_approvals = await db.scalar(
        select(func.count())
        .select_from(Approval)
        .where(Approval.status == "rejected")
    )

    return {
        "requests": {
            "total": total_requests or 0,
            "pending": pending_requests or 0,
            "completed": completed_requests or 0,
            "failed": failed_requests or 0,
        },
        "workflows": {
            "total": total_workflows or 0,
            "running": running_workflows or 0,
            "waiting_approval": waiting_approval or 0,
            "completed": completed_workflows or 0,
            "failed": failed_workflows or 0,
        },
        "approvals": {
            "total": total_approvals or 0,
            "pending": pending_approvals or 0,
            "approved": approved_approvals or 0,
            "rejected": rejected_approvals or 0,
        },
    }