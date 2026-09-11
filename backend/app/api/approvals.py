from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.models.models import Approval, User
from app.services.approval_service import (
    approve_approval,
    reject_approval,
)


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


class ApprovalDecision(BaseModel):
    decision: str = Field(
        pattern="^(approved|rejected)$"
    )

    reviewer_comment: str | None = Field(
        default=None,
        max_length=2000,
    )


@router.get("")
async def list_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:

    result = await db.execute(
        select(Approval)
        .order_by(Approval.created_at.desc())
    )

    approvals = result.scalars().all()

    return [
        {
            "id": str(approval.id),
            "workflow_execution_id": str(
                approval.workflow_execution_id
            ),
            "requested_by": (
                str(approval.requested_by)
                if approval.requested_by
                else None
            ),
            "reviewed_by": (
                str(approval.reviewed_by)
                if approval.reviewed_by
                else None
            ),
            "status": approval.status,
            "reason": approval.reason,
            "recommendation": approval.recommendation,
            "reviewer_comment": approval.reviewer_comment,
            "created_at": approval.created_at,
            "reviewed_at": approval.reviewed_at,
        }
        for approval in approvals
    ]


@router.patch("/{approval_id}")
async def decide_approval(
    approval_id: UUID,
    decision_data: ApprovalDecision,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> dict:

    approval = await db.scalar(
        select(Approval).where(
            Approval.id == approval_id
        )
    )

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found.",
        )

    if approval.status.lower() != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approval has already been decided.",
        )

    try:
        if decision_data.decision == "approved":

            approval = await approve_approval(
                db=db,
                approval_id=approval_id,
                reviewed_by=current_user.id,
                reviewer_comment=decision_data.reviewer_comment,
            )

        else:

            approval = await reject_approval(
                db=db,
                approval_id=approval_id,
                reviewed_by=current_user.id,
                reviewer_comment=decision_data.reviewer_comment,
            )

        return {
            "id": str(approval.id),
            "workflow_execution_id": str(
                approval.workflow_execution_id
            ),
            "status": approval.status,
            "reviewed_by": (
                str(approval.reviewed_by)
                if approval.reviewed_by
                else None
            ),
            "reviewer_comment": approval.reviewer_comment,
            "reviewed_at": approval.reviewed_at,
            "message": (
                "Workflow approved and completed."
                if approval.status.lower() == "approved"
                else "Workflow rejected and cancelled."
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )