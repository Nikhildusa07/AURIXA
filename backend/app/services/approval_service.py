from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Approval, Request, WorkflowExecution
from app.services.audit_service import create_audit_log


async def create_approval(
    db: AsyncSession,
    workflow_execution_id: UUID,
    reason: str,
    recommendation: dict[str, Any],
    requested_by: UUID | None = None,
) -> Approval:
    approval = Approval(
        workflow_execution_id=workflow_execution_id,
        requested_by=requested_by,
        status="pending",
        reason=reason,
        recommendation=recommendation,
    )

    db.add(approval)
    await db.commit()
    await db.refresh(approval)

    return approval


async def approve_approval(
    db: AsyncSession,
    approval_id: UUID,
    reviewed_by: UUID | None = None,
    reviewer_comment: str | None = None,
) -> Approval:
    approval = await db.get(
        Approval,
        approval_id,
    )

    if approval is None:
        raise ValueError("Approval not found.")

    if approval.status != "pending":
        raise ValueError(
            f"Approval cannot be approved. "
            f"Current status: {approval.status}"
        )

    execution = await db.get(
        WorkflowExecution,
        approval.workflow_execution_id,
    )

    if execution is None:
        raise ValueError("Workflow execution not found.")

    request = await db.get(
        Request,
        execution.request_id,
    )

    approval.status = "approved"
    approval.reviewed_by = reviewed_by
    approval.reviewer_comment = reviewer_comment
    approval.reviewed_at = datetime.now(timezone.utc)

    execution.status = "completed"
    execution.current_step = "completed"
    execution.completed_at = datetime.now(timezone.utc)

    execution.state = {
        **execution.state,
        "approval_status": "approved",
        "reviewer_comment": reviewer_comment,
    }

    if request is not None:
        request.status = "completed"

        await create_audit_log(
            db=db,
            trace_id=request.trace_id,
            user_id=reviewed_by,
            event_type="approval",
            entity_type="approval",
            entity_id=str(approval.id),
            action="approved",
            details={
                "workflow_execution_id": str(execution.id),
                "reviewer_comment": reviewer_comment,
                "workflow_status": "completed",
            },
        )

    await db.commit()
    await db.refresh(approval)

    return approval


async def reject_approval(
    db: AsyncSession,
    approval_id: UUID,
    reviewed_by: UUID | None = None,
    reviewer_comment: str | None = None,
) -> Approval:
    approval = await db.get(
        Approval,
        approval_id,
    )

    if approval is None:
        raise ValueError("Approval not found.")

    if approval.status != "pending":
        raise ValueError(
            f"Approval cannot be rejected. "
            f"Current status: {approval.status}"
        )

    execution = await db.get(
        WorkflowExecution,
        approval.workflow_execution_id,
    )

    if execution is None:
        raise ValueError("Workflow execution not found.")

    request = await db.get(
        Request,
        execution.request_id,
    )

    approval.status = "rejected"
    approval.reviewed_by = reviewed_by
    approval.reviewer_comment = reviewer_comment
    approval.reviewed_at = datetime.now(timezone.utc)

    execution.status = "cancelled"
    execution.current_step = "cancelled"
    execution.completed_at = datetime.now(timezone.utc)

    execution.state = {
        **execution.state,
        "approval_status": "rejected",
        "reviewer_comment": reviewer_comment,
    }

    if request is not None:
        request.status = "cancelled"

        await create_audit_log(
            db=db,
            trace_id=request.trace_id,
            user_id=reviewed_by,
            event_type="approval",
            entity_type="approval",
            entity_id=str(approval.id),
            action="rejected",
            details={
                "workflow_execution_id": str(execution.id),
                "reviewer_comment": reviewer_comment,
                "workflow_status": "cancelled",
            },
        )

    await db.commit()
    await db.refresh(approval)

    return approval