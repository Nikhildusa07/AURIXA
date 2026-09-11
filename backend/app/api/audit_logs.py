from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import AuditLog, User


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("")
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
    )

    audit_logs = result.scalars().all()

    return [
        {
            "id": str(log.id),
            "trace_id": log.trace_id,
            "user_id": (
                str(log.user_id)
                if log.user_id is not None
                else None
            ),
            "event_type": log.event_type,
            "entity_type": log.entity_type,
            "entity_id": (
                str(log.entity_id)
                if log.entity_id is not None
                else None
            ),
            "action": log.action,
            "details": log.details or {},
            "created_at": (
                log.created_at.isoformat()
                if log.created_at is not None
                else None
            ),
        }
        for log in audit_logs
    ]