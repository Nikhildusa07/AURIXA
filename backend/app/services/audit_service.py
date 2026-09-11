from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuditLog


async def create_audit_log(
    db: AsyncSession,
    trace_id: str,
    event_type: str,
    action: str,
    user_id: UUID | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    details: dict[str, Any] | None = None,
    commit: bool = False,
) -> AuditLog:
    audit_log = AuditLog(
        trace_id=trace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        details=details or {},
    )

    db.add(audit_log)

    # Make the audit log available in the current transaction
    await db.flush()

    # Commit only when explicitly requested.
    # This allows Request + AuditLog to be saved together safely.
    if commit:
        await db.commit()
        await db.refresh(audit_log)

    return audit_log