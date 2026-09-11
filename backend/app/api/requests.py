import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import (
    Approval,
    ApprovalStatus,
    ExecutionStatus,
    Request,
    RequestStatus,
    User,
    Workflow,
    WorkflowExecution,
    WorkflowStatus,
)
from app.schemas.requests import RequestCreate, RequestResponse
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/requests",
    tags=["Requests"],
)


HIGH_PRIORITY_WORKFLOW_NAME = "High Priority Request Approval"


async def get_or_create_high_priority_workflow(
    db: AsyncSession,
) -> Workflow:
    result = await db.execute(
        select(Workflow).where(
            Workflow.name == HIGH_PRIORITY_WORKFLOW_NAME
        )
    )

    workflow = result.scalar_one_or_none()

    if workflow is not None:
        return workflow

    workflow = Workflow(
        name=HIGH_PRIORITY_WORKFLOW_NAME,
        description=(
            "System workflow for high-priority enterprise requests "
            "requiring administrator approval."
        ),
        status=WorkflowStatus.ACTIVE.value,
        configuration={
            "trigger": "high_priority_request",
            "requires_approval": True,
        },
    )

    db.add(workflow)
    await db.flush()

    return workflow


@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_request(
    request_data: RequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Request:

    priority = (
        request_data.priority.lower()
        if request_data.priority
        else "normal"
    )

    requires_approval = priority == "high"

    request_status = (
        RequestStatus.WAITING_APPROVAL.value
        if requires_approval
        else RequestStatus.PENDING.value
    )

    request = Request(
        user_id=current_user.id,
        title=request_data.title,
        content=request_data.content,
        request_type=request_data.request_type,
        status=request_status,
        priority=priority,
        confidence_score=None,
        result=None,
        trace_id=str(uuid.uuid4()),
    )

    try:
        db.add(request)
        await db.flush()

        approval = None
        execution = None

        if requires_approval:
            workflow = await get_or_create_high_priority_workflow(db)

            execution = WorkflowExecution(
                workflow_id=workflow.id,
                request_id=request.id,
                status=ExecutionStatus.WAITING_APPROVAL.value,
                current_step="waiting_for_admin_approval",
                state={
                    "request_title": request.title,
                    "priority": priority,
                    "approval_required": True,
                },
            )

            db.add(execution)
            await db.flush()

            approval = Approval(
                workflow_execution_id=execution.id,
                requested_by=current_user.id,
                status=ApprovalStatus.PENDING.value,
                reason=(
                    f"High-priority request requires administrator approval: "
                    f"{request.title}"
                ),
                recommendation={
                    "action": "review_and_decide",
                    "request_id": str(request.id),
                    "title": request.title,
                    "content": request.content,
                    "request_type": request.request_type,
                    "priority": request.priority,
                },
            )

            db.add(approval)
            await db.flush()

        await create_audit_log(
            db=db,
            trace_id=request.trace_id,
            user_id=current_user.id,
            event_type="request",
            entity_type="request",
            entity_id=str(request.id),
            action="created",
            details={
                "title": request.title,
                "content": request.content,
                "request_type": request.request_type,
                "priority": request.priority,
                "status": request.status,
                "requires_approval": requires_approval,
                "workflow_execution_id": (
                    str(execution.id)
                    if execution is not None
                    else None
                ),
                "approval_id": (
                    str(approval.id)
                    if approval is not None
                    else None
                ),
            },
        )

        if approval is not None:
            await create_audit_log(
                db=db,
                trace_id=request.trace_id,
                user_id=current_user.id,
                event_type="approval",
                entity_type="approval",
                entity_id=str(approval.id),
                action="created",
                details={
                    "request_id": str(request.id),
                    "workflow_execution_id": str(execution.id),
                    "status": approval.status,
                    "reason": approval.reason,
                },
            )

        await db.commit()
        await db.refresh(request)

        return request

    except Exception:
        await db.rollback()
        raise


@router.get(
    "",
    response_model=list[RequestResponse],
)
async def list_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Request]:

    result = await db.execute(
        select(Request)
        .where(Request.user_id == current_user.id)
        .order_by(Request.created_at.desc())
    )

    return list(result.scalars().all())