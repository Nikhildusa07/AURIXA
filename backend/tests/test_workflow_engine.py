from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.workflows.engine import (
    create_workflow_execution,
    start_workflow_execution,
    complete_workflow_execution,
    fail_workflow_execution,
    retry_workflow_execution,
    execute_workflow,
)


def make_db():
    db = Mock()
    db.scalar = AsyncMock()
    db.get = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = Mock()
    return db


def make_execution(
    status="pending",
    workflow_name="test_workflow",
    request_id="request-123",
):
    return SimpleNamespace(
        id="execution-123",
        workflow_id="workflow-123",
        request_id=request_id,
        status=status,
        current_step="pending",
        state={"workflow_name": workflow_name},
        error_message=None,
        started_at=None,
        completed_at=None,
    )


@pytest.mark.asyncio
async def test_create_workflow_execution_existing_workflow(monkeypatch):
    db = make_db()

    workflow_definition = SimpleNamespace(
        name="test_workflow",
        description="Test workflow",
    )

    workflow = SimpleNamespace(
        id="workflow-123",
        name="test_workflow",
        description="Test workflow",
    )

    monkeypatch.setattr(
        "app.workflows.engine.workflow_registry.get",
        Mock(return_value=workflow_definition),
    )

    db.scalar.return_value = workflow

    execution = await create_workflow_execution(
        db=db,
        workflow_name="test_workflow",
        request_id="request-123",
    )

    assert execution.status == "pending"
    assert execution.current_step == "pending"

    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_workflow_execution_new_workflow(monkeypatch):
    db = make_db()

    workflow_definition = SimpleNamespace(
        name="new_workflow",
        description="New workflow",
    )

    monkeypatch.setattr(
        "app.workflows.engine.workflow_registry.get",
        Mock(return_value=workflow_definition),
    )

    async def flush():
        added_workflow = db.add.call_args_list[0][0][0]
        added_workflow.id = "workflow-new"

    db.scalar.return_value = None
    db.flush.side_effect = flush

    execution = await create_workflow_execution(
        db=db,
        workflow_name="new_workflow",
        request_id="request-123",
    )

    assert execution.status == "pending"
    assert execution.state["workflow_name"] == "new_workflow"

    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_start_workflow_execution_success():
    db = make_db()

    execution = make_execution()
    request = SimpleNamespace(status="pending")

    db.get.side_effect = [
        execution,
        request,
    ]

    result = await start_workflow_execution(
        db=db,
        execution_id="execution-123",
    )

    assert result.status == "running"
    assert result.current_step == "processing"
    assert result.started_at is not None
    assert request.status == "processing"


@pytest.mark.asyncio
async def test_start_workflow_execution_not_found():
    db = make_db()
    db.get.return_value = None

    with pytest.raises(
        ValueError,
        match="Workflow execution not found",
    ):
        await start_workflow_execution(
            db=db,
            execution_id="missing",
        )


@pytest.mark.asyncio
async def test_start_workflow_execution_invalid_status():
    db = make_db()

    execution = make_execution(status="completed")
    db.get.return_value = execution

    with pytest.raises(
        ValueError,
        match="Cannot start execution",
    ):
        await start_workflow_execution(
            db=db,
            execution_id="execution-123",
        )


@pytest.mark.asyncio
async def test_complete_workflow_execution_with_state():
    db = make_db()

    execution = make_execution(status="running")
    request = SimpleNamespace(status="processing")

    db.get.side_effect = [
        execution,
        request,
    ]

    state = {"result": "success"}

    result = await complete_workflow_execution(
        db=db,
        execution_id="execution-123",
        state=state,
    )

    assert result.status == "completed"
    assert result.current_step == "completed"
    assert result.state == state
    assert result.completed_at is not None
    assert request.status == "completed"


@pytest.mark.asyncio
async def test_complete_workflow_execution_without_state():
    db = make_db()

    execution = make_execution(status="running")
    original_state = execution.state.copy()

    db.get.side_effect = [
        execution,
        None,
    ]

    result = await complete_workflow_execution(
        db=db,
        execution_id="execution-123",
    )

    assert result.status == "completed"
    assert result.state == original_state


@pytest.mark.asyncio
async def test_complete_workflow_execution_not_found():
    db = make_db()
    db.get.return_value = None

    with pytest.raises(
        ValueError,
        match="Workflow execution not found",
    ):
        await complete_workflow_execution(
            db=db,
            execution_id="missing",
        )


@pytest.mark.asyncio
async def test_fail_workflow_execution_success():
    db = make_db()

    execution = make_execution(status="running")
    request = SimpleNamespace(status="processing")

    db.get.side_effect = [
        execution,
        request,
    ]

    result = await fail_workflow_execution(
        db=db,
        execution_id="execution-123",
        error_message="Something failed",
    )

    assert result.status == "failed"
    assert result.current_step == "failed"
    assert result.error_message == "Something failed"
    assert result.completed_at is not None
    assert request.status == "failed"


@pytest.mark.asyncio
async def test_fail_workflow_execution_not_found():
    db = make_db()
    db.get.return_value = None

    with pytest.raises(
        ValueError,
        match="Workflow execution not found",
    ):
        await fail_workflow_execution(
            db=db,
            execution_id="missing",
            error_message="error",
        )


@pytest.mark.asyncio
async def test_retry_workflow_execution_success():
    db = make_db()

    execution = make_execution(status="failed")
    execution.error_message = "Old error"
    execution.completed_at = "old-time"

    request = SimpleNamespace(status="failed")

    db.get.side_effect = [
        execution,
        request,
    ]

    result = await retry_workflow_execution(
        db=db,
        execution_id="execution-123",
    )

    assert result.status == "pending"
    assert result.current_step == "pending"
    assert result.error_message is None
    assert result.completed_at is None
    assert request.status == "pending"


@pytest.mark.asyncio
async def test_retry_workflow_execution_not_found():
    db = make_db()
    db.get.return_value = None

    with pytest.raises(
        ValueError,
        match="Workflow execution not found",
    ):
        await retry_workflow_execution(
            db=db,
            execution_id="missing",
        )


@pytest.mark.asyncio
async def test_retry_workflow_execution_invalid_status():
    db = make_db()

    execution = make_execution(status="running")
    db.get.return_value = execution

    with pytest.raises(
        ValueError,
        match="Only failed executions can be retried",
    ):
        await retry_workflow_execution(
            db=db,
            execution_id="execution-123",
        )


@pytest.mark.asyncio
async def test_execute_workflow_not_found():
    db = make_db()
    db.get.return_value = None

    with pytest.raises(
        ValueError,
        match="Workflow execution not found",
    ):
        await execute_workflow(
            db=db,
            execution_id="missing",
        )


@pytest.mark.asyncio
async def test_execute_workflow_invalid_status():
    db = make_db()

    execution = make_execution(status="running")
    db.get.return_value = execution

    with pytest.raises(
        ValueError,
        match="Workflow must be pending",
    ):
        await execute_workflow(
            db=db,
            execution_id="execution-123",
        )


@pytest.mark.asyncio
async def test_execute_workflow_missing_workflow_name():
    db = make_db()

    execution = make_execution()
    execution.state = {}

    db.get.return_value = execution

    with pytest.raises(
        ValueError,
        match="Workflow name is missing",
    ):
        await execute_workflow(
            db=db,
            execution_id="execution-123",
        )


@pytest.mark.asyncio
async def test_execute_workflow_success(monkeypatch):
    db = make_db()

    execution = make_execution()

    request = SimpleNamespace(
        status="pending",
        trace_id="trace-123",
        user_id="user-123",
        request_type=None,
        confidence_score=None,
        result=None,
    )

    workflow = SimpleNamespace(
        handler=Mock(
            return_value={
                "request_type": "invoice",
                "classification_confidence": 0.95,
            }
        )
    )

    task = SimpleNamespace(
        id="task-123",
        status="completed",
    )

    db.get.side_effect = [
        execution,
        request,
    ]

    monkeypatch.setattr(
        "app.workflows.engine.workflow_registry.get",
        Mock(return_value=workflow),
    )

    monkeypatch.setattr(
        "app.workflows.engine.create_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.start_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.complete_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.create_audit_log",
        AsyncMock(),
    )

    result = await execute_workflow(
        db=db,
        execution_id="execution-123",
    )

    assert result.status == "completed"
    assert result.current_step == "completed"
    assert request.status == "completed"
    assert request.request_type == "invoice"
    assert request.confidence_score == 0.95


@pytest.mark.asyncio
async def test_execute_workflow_requires_approval(monkeypatch):
    db = make_db()

    execution = make_execution()

    request = SimpleNamespace(
        status="pending",
        trace_id="trace-123",
        user_id="user-123",
        request_type=None,
        confidence_score=None,
        result=None,
    )

    workflow = SimpleNamespace(
        handler=Mock(
            return_value={
                "requires_approval": True,
                "action": "important_action",
            }
        )
    )

    task = SimpleNamespace(
        id="task-123",
        status="completed",
    )

    approval = SimpleNamespace(
        id="approval-123",
        status="pending",
    )

    db.get.side_effect = [
        execution,
        request,
    ]

    monkeypatch.setattr(
        "app.workflows.engine.workflow_registry.get",
        Mock(return_value=workflow),
    )

    monkeypatch.setattr(
        "app.workflows.engine.create_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.start_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.complete_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.create_approval",
        AsyncMock(return_value=approval),
    )

    monkeypatch.setattr(
        "app.workflows.engine.create_audit_log",
        AsyncMock(),
    )

    result = await execute_workflow(
        db=db,
        execution_id="execution-123",
    )

    assert result.status == "waiting_approval"
    assert result.current_step == "human_approval"
    assert request.status == "waiting_approval"
    assert result.state["approval_id"] == "approval-123"


@pytest.mark.asyncio
async def test_execute_workflow_handler_failure(monkeypatch):
    db = make_db()

    execution = make_execution()

    request = SimpleNamespace(
        status="pending",
        trace_id="trace-123",
        user_id="user-123",
    )

    workflow = SimpleNamespace(
        handler=Mock(
            side_effect=RuntimeError("Workflow crashed")
        )
    )

    task = SimpleNamespace(
        id="task-123",
        status="running",
    )

    db.get.side_effect = [
        execution,
        request,
    ]

    monkeypatch.setattr(
        "app.workflows.engine.workflow_registry.get",
        Mock(return_value=workflow),
    )

    monkeypatch.setattr(
        "app.workflows.engine.create_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.start_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.fail_workflow_task",
        AsyncMock(return_value=task),
    )

    monkeypatch.setattr(
        "app.workflows.engine.create_audit_log",
        AsyncMock(),
    )

    result = await execute_workflow(
        db=db,
        execution_id="execution-123",
    )

    assert result.status == "failed"
    assert result.current_step == "failed"
    assert "Workflow crashed" in result.error_message
    assert request.status == "failed"