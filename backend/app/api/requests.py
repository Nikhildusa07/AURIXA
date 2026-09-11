import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import Request, User
from app.schemas.requests import RequestCreate, RequestResponse
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/requests",
    tags=["Requests"],
)


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

    request = Request(
        user_id=current_user.id,
        title=request_data.title,
        content=request_data.content,
        request_type=request_data.request_type,
        status="pending",
        priority=request_data.priority,
        confidence_score=None,
        result=None,
        trace_id=str(uuid.uuid4()),
    )

    try:
        db.add(request)

        # Generate request ID before audit log creation
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