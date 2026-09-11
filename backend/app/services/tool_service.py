from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Tool, ToolExecution


async def get_tool_by_name(
    db: AsyncSession,
    tool_name: str,
) -> Tool | None:
    return await db.scalar(
        select(Tool).where(
            Tool.name == tool_name
        )
    )


async def get_or_create_tool(
    db: AsyncSession,
    name: str,
    description: str,
    input_schema: dict[str, Any] | None = None,
    output_schema: dict[str, Any] | None = None,
) -> Tool:
    tool = await get_tool_by_name(
        db=db,
        tool_name=name,
    )

    if tool is not None:
        return tool

    tool = Tool(
        name=name,
        description=description,
        input_schema=input_schema or {},
        output_schema=output_schema or {},
        allowed_agents=[],
        configuration={},
        is_active=True,
    )

    db.add(tool)
    await db.commit()
    await db.refresh(tool)

    return tool


async def execute_tool(
    db: AsyncSession,
    tool_name: str,
    input_data: dict[str, Any],
    workflow_execution_id: UUID | None = None,
    agent_id: UUID | None = None,
) -> ToolExecution:
    tool = await get_tool_by_name(
        db=db,
        tool_name=tool_name,
    )

    if tool is None:
        tool = await get_or_create_tool(
            db=db,
            name=tool_name,
            description=f"AURIXA tool: {tool_name}",
        )

    if not tool.is_active:
        raise ValueError(
            f"Tool is inactive: {tool_name}"
        )

    execution = ToolExecution(
        tool_id=tool.id,
        workflow_execution_id=workflow_execution_id,
        agent_id=agent_id,
        status="running",
        input_data=input_data,
    )

    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    started = perf_counter()

    try:
        # Current simulated tool execution.
        # Real external tools can be connected here later.
        output_data = {
            "status": "success",
            "tool_name": tool_name,
            "result": input_data,
            "executed_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        duration_ms = int(
            (perf_counter() - started) * 1000
        )

        execution.status = "completed"
        execution.output_data = output_data
        execution.duration_ms = duration_ms

        await db.commit()
        await db.refresh(execution)

        return execution

    except Exception as exc:
        duration_ms = int(
            (perf_counter() - started) * 1000
        )

        execution.status = "failed"
        execution.error_message = str(exc)
        execution.duration_ms = duration_ms

        await db.commit()
        await db.refresh(execution)

        raise