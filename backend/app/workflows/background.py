from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.documents.ingestion import ingest_document
from app.services.notification_service import (
    send_email_notification,
)
from app.workflows.engine import execute_workflow


async def run_workflow_job(
    execution_id: UUID,
) -> None:
    """Execute a workflow in the background."""

    async with AsyncSessionLocal() as db:
        await execute_workflow(
            db=db,
            execution_id=execution_id,
        )


async def run_document_ingestion_job(
    file_path: str,
    document_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Process and index a document in the background."""

    return await asyncio.to_thread(
        ingest_document,
        file_path=file_path,
        document_id=document_id,
        metadata=metadata,
    )


async def run_notification_job(
    recipient_email: str,
    subject: str,
    message: str,
) -> dict[str, Any]:
    """Send an email notification in the background."""

    return await asyncio.to_thread(
        send_email_notification,
        recipient_email=recipient_email,
        subject=subject,
        message=message,
    )