from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import WorkflowTask


async def create_workflow_task(
    db: AsyncSession,
    execution_id: UUID,
    task_name: str,
    task_type: str,
) -> WorkflowTask:
    task = WorkflowTask(
        execution_id=execution_id,
        task_name=task_name,
        task_type=task_type,
        status="pending",
        input_data={},
        output_data=None,
        error_message=None,
        retry_count=0,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


async def start_workflow_task(
    db: AsyncSession,
    task_id: UUID,
) -> WorkflowTask:
    task = await db.get(WorkflowTask, task_id)

    if task is None:
        raise ValueError("Workflow task not found.")

    if task.status != "pending":
        raise ValueError(
            f"Cannot start task with status: {task.status}"
        )

    task.status = "running"

    await db.commit()
    await db.refresh(task)

    return task


async def complete_workflow_task(
    db: AsyncSession,
    task_id: UUID,
    output_data: dict | None = None,
) -> WorkflowTask:
    task = await db.get(WorkflowTask, task_id)

    if task is None:
        raise ValueError("Workflow task not found.")

    if task.status != "running":
        raise ValueError(
            f"Cannot complete task with status: {task.status}"
        )

    task.status = "completed"
    task.output_data = output_data or {}

    await db.commit()
    await db.refresh(task)

    return task


async def fail_workflow_task(
    db: AsyncSession,
    task_id: UUID,
    error_message: str,
) -> WorkflowTask:
    task = await db.get(WorkflowTask, task_id)

    if task is None:
        raise ValueError("Workflow task not found.")

    task.status = "failed"
    task.error_message = error_message

    await db.commit()
    await db.refresh(task)

    return task


async def retry_workflow_task(
    db: AsyncSession,
    task_id: UUID,
) -> WorkflowTask:
    task = await db.get(WorkflowTask, task_id)

    if task is None:
        raise ValueError("Workflow task not found.")

    if task.status != "failed":
        raise ValueError(
            f"Only failed tasks can be retried. Current status: {task.status}"
        )

    task.status = "pending"
    task.error_message = None
    task.retry_count += 1

    await db.commit()
    await db.refresh(task)

    return task