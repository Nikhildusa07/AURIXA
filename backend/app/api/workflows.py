from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User, WorkflowExecution
from app.workflows.background import run_workflow_job
from app.workflows.engine import (
    create_workflow_execution,
    retry_workflow_execution,
)


router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
)


# ==========================================
# EXECUTE WORKFLOW IN BACKGROUND
# ==========================================

@router.post("/{workflow_name}/execute")
async def execute_workflow_api(
    workflow_name: str,
    request_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        execution = await create_workflow_execution(
            db=db,
            workflow_name=workflow_name,
            request_id=request_id,
        )

        background_tasks.add_task(
            run_workflow_job,
            execution.id,
        )

        return {
            "execution_id": str(execution.id),
            "workflow": workflow_name,
            "workflow_name": workflow_name,
            "workflow_id": str(execution.workflow_id),
            "request_id": str(execution.request_id),
            "status": execution.status,
            "current_step": execution.current_step,
            "message": (
                "Workflow execution started in the background."
            ),
        }

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Workflow execution failed: {str(exc)}"
            ),
        )


# ==========================================
# LIST WORKFLOW EXECUTIONS
# ==========================================

@router.get("/executions")
async def list_workflow_executions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkflowExecution)
        .order_by(WorkflowExecution.created_at.desc())
    )

    executions = result.scalars().all()

    return [
        {
            "execution_id": str(execution.id),
            "workflow_id": str(execution.workflow_id),
            "workflow": (
                execution.state.get("workflow_name")
                if isinstance(execution.state, dict)
                else None
            ) or "Unknown Workflow",
            "workflow_name": (
                execution.state.get("workflow_name")
                if isinstance(execution.state, dict)
                else None
            ) or "Unknown Workflow",
            "request_id": (
                str(execution.request_id)
                if execution.request_id
                else None
            ),
            "status": execution.status,
            "current_step": execution.current_step,
            "state": execution.state,
            "error_message": execution.error_message,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "created_at": execution.created_at,
        }
        for execution in executions
    ]


# ==========================================
# GET SINGLE WORKFLOW EXECUTION
# ==========================================

@router.get("/executions/{execution_id}")
async def get_workflow_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    execution = await db.get(
        WorkflowExecution,
        execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow execution not found.",
        )

    workflow_name = (
        execution.state.get("workflow_name")
        if isinstance(execution.state, dict)
        else None
    ) or "Unknown Workflow"

    return {
        "execution_id": str(execution.id),
        "workflow_id": str(execution.workflow_id),
        "workflow": workflow_name,
        "workflow_name": workflow_name,
        "request_id": (
            str(execution.request_id)
            if execution.request_id
            else None
        ),
        "status": execution.status,
        "current_step": execution.current_step,
        "state": execution.state,
        "error_message": execution.error_message,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
        "created_at": execution.created_at,
    }


# ==========================================
# RETRY WORKFLOW IN BACKGROUND
# ==========================================

@router.post("/executions/{execution_id}/retry")
async def retry_workflow_execution_api(
    execution_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        execution = await retry_workflow_execution(
            db=db,
            execution_id=execution_id,
        )

        background_tasks.add_task(
            run_workflow_job,
            execution.id,
        )

        return {
            "execution_id": str(execution.id),
            "workflow_id": str(execution.workflow_id),
            "request_id": (
                str(execution.request_id)
                if execution.request_id
                else None
            ),
            "status": execution.status,
            "current_step": execution.current_step,
            "message": (
                "Workflow retry started in the background."
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow retry failed: {str(exc)}",
        )