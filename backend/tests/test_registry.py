import pytest

from app.ai.tools.registry import ToolDefinition, ToolRegistry


def sample_handler(parameters):
    return {"status": "ok", "parameters": parameters}


def test_register_and_get_tool():
    registry = ToolRegistry()

    tool = ToolDefinition(
        name="test_tool",
        description="A test tool",
        handler=sample_handler,
    )

    registry.register(tool)

    result = registry.get("test_tool")

    assert result == tool
    assert result.name == "test_tool"
    assert result.description == "A test tool"
    assert result.requires_approval is False


def test_register_duplicate_tool():
    registry = ToolRegistry()

    tool = ToolDefinition(
        name="duplicate_tool",
        description="Test duplicate",
        handler=sample_handler,
    )

    registry.register(tool)

    with pytest.raises(
        ValueError,
        match="Tool already registered: duplicate_tool",
    ):
        registry.register(tool)


def test_get_unknown_tool():
    registry = ToolRegistry()

    with pytest.raises(
        KeyError,
        match="Unauthorized or unknown tool: unknown_tool",
    ):
        registry.get("unknown_tool")


def test_list_tools_empty_registry():
    registry = ToolRegistry()

    result = registry.list_tools()

    assert result == []


def test_list_registered_tools():
    registry = ToolRegistry()

    tool_one = ToolDefinition(
        name="tool_one",
        description="First tool",
        handler=sample_handler,
    )

    tool_two = ToolDefinition(
        name="tool_two",
        description="Second tool",
        handler=sample_handler,
        requires_approval=True,
    )

    registry.register(tool_one)
    registry.register(tool_two)

    tools = registry.list_tools()

    assert len(tools) == 2
    assert tool_one in tools
    assert tool_two in tools


def test_tool_definition_requires_approval_default():
    tool = ToolDefinition(
        name="default_tool",
        description="Default approval test",
        handler=sample_handler,
    )

    assert tool.requires_approval is False


def test_tool_definition_requires_approval_true():
    tool = ToolDefinition(
        name="approval_tool",
        description="Approval required",
        handler=sample_handler,
        requires_approval=True,
    )

    assert tool.requires_approval is True


def test_tool_definition_is_frozen():
    tool = ToolDefinition(
        name="frozen_tool",
        description="Frozen dataclass",
        handler=sample_handler,
    )

    with pytest.raises(Exception):
        tool.name = "changed_tool"  