from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import Tool, ToolExecution, User
from app.services.tool_service import (
    execute_tool,
    get_or_create_tool,
)


router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
)


class ToolCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str = Field(
        min_length=1,
    )


class ToolExecuteRequest(BaseModel):
    input_data: dict = Field(
        default_factory=dict,
    )
    workflow_execution_id: UUID | None = None


@router.get("")
async def list_tools(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    result = await db.execute(
        select(Tool).order_by(
            Tool.created_at.desc()
        )
    )

    tools = result.scalars().all()

    return [
        {
            "id": str(tool.id),
            "name": tool.name,
            "description": tool.description,
            "is_active": tool.is_active,
            "created_at": tool.created_at,
        }
        for tool in tools
    ]


@router.post("")
async def create_tool(
    tool_data: ToolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    existing_tool = await db.scalar(
        select(Tool).where(
            Tool.name == tool_data.name
        )
    )

    if existing_tool is not None:
        raise HTTPException(
            status_code=409,
            detail="Tool already exists.",
        )

    tool = await get_or_create_tool(
        db=db,
        name=tool_data.name,
        description=tool_data.description,
    )

    return {
        "id": str(tool.id),
        "name": tool.name,
        "description": tool.description,
        "is_active": tool.is_active,
        "message": "Tool created successfully.",
    }


@router.post("/{tool_name}/execute")
async def execute_tool_api(
    tool_name: str,
    request_data: ToolExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        execution = await execute_tool(
            db=db,
            tool_name=tool_name,
            input_data=request_data.input_data,
            workflow_execution_id=(
                request_data.workflow_execution_id
            ),
        )

        return {
            "execution_id": str(execution.id),
            "tool_id": str(execution.tool_id),
            "workflow_execution_id": (
                str(execution.workflow_execution_id)
                if execution.workflow_execution_id
                else None
            ),
            "status": execution.status,
            "input_data": execution.input_data,
            "output_data": execution.output_data,
            "duration_ms": execution.duration_ms,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )