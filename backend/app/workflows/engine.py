from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Request,
    Workflow,
    WorkflowExecution,
)
from app.services.approval_service import create_approval
from app.services.audit_service import create_audit_log
from app.workflows.registry import workflow_registry
from app.workflows.tasks import (
    create_workflow_task,
    start_workflow_task,
    complete_workflow_task,
    fail_workflow_task,
)


async def create_workflow_execution(
    db: AsyncSession,
    workflow_name: str,
    request_id: UUID,
) -> WorkflowExecution:
    workflow_definition = workflow_registry.get(workflow_name)

    workflow = await db.scalar(
        select(Workflow).where(
            Workflow.name == workflow_definition.name
        )
    )

    if workflow is None:
        workflow = Workflow(
            name=workflow_definition.name,
            description=workflow_definition.description,
            status="active",
            configuration={},
        )

        db.add(workflow)
        await db.flush()

    execution = WorkflowExecution(
        workflow_id=workflow.id,
        request_id=request_id,
        status="pending",
        current_step="pending",
        state={
            "workflow_name": workflow.name,
            "description": workflow.description,
            "request_id": str(request_id),
        },
        error_message=None,
        started_at=None,
        completed_at=None,
    )

    db.add(execution)

    await db.commit()
    await db.refresh(execution)

    return execution


async def start_workflow_execution(
    db: AsyncSession,
    execution_id: UUID,
) -> WorkflowExecution:
    execution = await db.get(
        WorkflowExecution,
        execution_id,
    )

    if execution is None:
        raise ValueError("Workflow execution not found.")

    if execution.status != "pending":
        raise ValueError(
            f"Cannot start execution with status: {execution.status}"
        )

    execution.status = "running"
    execution.current_step = "processing"
    execution.started_at = datetime.now(timezone.utc)

    request = await db.get(
        Request,
        execution.request_id,
    )

    if request is not None:
        request.status = "processing"

    await db.commit()
    await db.refresh(execution)

    return execution


async def complete_workflow_execution(
    db: AsyncSession,
    execution_id: UUID,
    state: dict | None = None,
) -> WorkflowExecution:
    execution = await db.get(
        WorkflowExecution,
        execution_id,
    )

    if execution is None:
        raise ValueError("Workflow execution not found.")

    execution.status = "completed"
    execution.current_step = "completed"
    execution.completed_at = datetime.now(timezone.utc)

    if state is not None:
        execution.state = state

    request = await db.get(
        Request,
        execution.request_id,
    )

    if request is not None:
        request.status = "completed"

    await db.commit()
    await db.refresh(execution)

    return execution


async def fail_workflow_execution(
    db: AsyncSession,
    execution_id: UUID,
    error_message: str,
) -> WorkflowExecution:
    execution = await db.get(
        WorkflowExecution,
        execution_id,
    )

    if execution is None:
        raise ValueError("Workflow execution not found.")

    execution.status = "failed"
    execution.current_step = "failed"
    execution.error_message = error_message
    execution.completed_at = datetime.now(timezone.utc)

    request = await db.get(
        Request,
        execution.request_id,
    )

    if request is not None:
        request.status = "failed"

    await db.commit()
    await db.refresh(execution)

    return execution


async def retry_workflow_execution(
    db: AsyncSession,
    execution_id: UUID,
) -> WorkflowExecution:
    execution = await db.get(
        WorkflowExecution,
        execution_id,
    )

    if execution is None:
        raise ValueError("Workflow execution not found.")

    if execution.status != "failed":
        raise ValueError(
            f"Only failed executions can be retried. "
            f"Current status: {execution.status}"
        )

    execution.status = "pending"
    execution.current_step = "pending"
    execution.error_message = None
    execution.completed_at = None

    request = await db.get(
        Request,
        execution.request_id,
    )

    if request is not None:
        request.status = "pending"

    await db.commit()
    await db.refresh(execution)

    return execution


async def execute_workflow(
    db: AsyncSession,
    execution_id: UUID,
) -> WorkflowExecution:
    execution = await db.get(
        WorkflowExecution,
        execution_id,
    )

    if execution is None:
        raise ValueError("Workflow execution not found.")

    if execution.status != "pending":
        raise ValueError(
            f"Workflow must be pending before execution. "
            f"Current status: {execution.status}"
        )

    workflow_name = execution.state.get("workflow_name")

    if not workflow_name:
        raise ValueError(
            "Workflow name is missing from execution state."
        )

    workflow = workflow_registry.get(workflow_name)

    request = await db.get(
        Request,
        execution.request_id,
    )

    trace_id = (
        request.trace_id
        if request is not None
        else str(execution.id)
    )

    user_id = (
        request.user_id
        if request is not None
        else None
    )

    task = await create_workflow_task(
        db=db,
        execution_id=execution.id,
        task_name=f"Execute {workflow_name}",
        task_type="workflow_execution",
    )

    try:
        execution.status = "running"
        execution.current_step = "processing"
        execution.started_at = datetime.now(timezone.utc)

        if request is not None:
            request.status = "processing"

        await db.commit()
        await db.refresh(execution)

        await create_audit_log(
            db=db,
            trace_id=trace_id,
            user_id=user_id,
            event_type="workflow",
            entity_type="workflow_execution",
            entity_id=str(execution.id),
            action="started",
            details={
                "workflow_name": workflow_name,
                "status": "running",
            },
        )

        task = await start_workflow_task(
            db=db,
            task_id=task.id,
        )

        result = workflow.handler()

        output_data = (
            result
            if isinstance(result, dict)
            else {"result": result}
        )

        task = await complete_workflow_task(
            db=db,
            task_id=task.id,
            output_data=output_data,
        )

        if request is not None and isinstance(result, dict):
            request.request_type = result.get(
                "request_type"
            )

            request.confidence_score = result.get(
                "classification_confidence"
            )

            request.result = result

        execution.state = {
            **execution.state,
            "result": result,
            "task_id": str(task.id),
            "task_status": task.status,
        }

        requires_approval = (
            isinstance(result, dict)
            and result.get(
                "requires_approval",
                False,
            )
        )

        if requires_approval:
            approval = await create_approval(
                db=db,
                workflow_execution_id=execution.id,
                reason="AI workflow requires human approval.",
                recommendation=result,
                requested_by=user_id,
            )

            execution.status = "waiting_approval"
            execution.current_step = "human_approval"

            execution.state = {
                **execution.state,
                "approval_id": str(approval.id),
                "approval_status": approval.status,
            }

            if request is not None:
                request.status = "waiting_approval"

            await db.commit()
            await db.refresh(execution)

            await create_audit_log(
                db=db,
                trace_id=trace_id,
                user_id=user_id,
                event_type="workflow",
                entity_type="workflow_execution",
                entity_id=str(execution.id),
                action="waiting_approval",
                details={
                    "workflow_name": workflow_name,
                    "approval_id": str(approval.id),
                    "status": "waiting_approval",
                },
            )

            return execution

        execution.status = "completed"
        execution.current_step = "completed"
        execution.completed_at = datetime.now(timezone.utc)

        if request is not None:
            request.status = "completed"

        await db.commit()
        await db.refresh(execution)

        await create_audit_log(
            db=db,
            trace_id=trace_id,
            user_id=user_id,
            event_type="workflow",
            entity_type="workflow_execution",
            entity_id=str(execution.id),
            action="completed",
            details={
                "workflow_name": workflow_name,
                "status": "completed",
            },
        )

        return execution

    except Exception as exc:
        try:
            await fail_workflow_task(
                db=db,
                task_id=task.id,
                error_message=str(exc),
            )
        except Exception:
            pass

        execution.status = "failed"
        execution.current_step = "failed"
        execution.error_message = str(exc)
        execution.completed_at = datetime.now(timezone.utc)

        if request is not None:
            request.status = "failed"

        await db.commit()
        await db.refresh(execution)

        await create_audit_log(
            db=db,
            trace_id=trace_id,
            user_id=user_id,
            event_type="workflow",
            entity_type="workflow_execution",
            entity_id=str(execution.id),
            action="failed",
            details={
                "workflow_name": workflow_name,
                "status": "failed",
                "error": str(exc),
            },
        )

        return execution