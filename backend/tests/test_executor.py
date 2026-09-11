import pytest
from unittest.mock import Mock, patch

from app.ai.tools.executor import execute_tool


def test_execute_tool_success():
    mock_tool = Mock()
    mock_tool.handler.return_value = {
        "message": "Tool executed successfully"
    }

    with patch(
        "app.ai.tools.executor.tool_registry.get",
        return_value=mock_tool,
    ) as mock_get:

        result = execute_tool(
            tool_name="test_tool",
            parameters={"value": 123},
        )

    assert result["status"] == "success"
    assert result["tool_name"] == "test_tool"
    assert result["result"] == {
        "message": "Tool executed successfully"
    }

    mock_get.assert_called_once_with("test_tool")
    mock_tool.handler.assert_called_once_with({"value": 123})


def test_execute_tool_handler_exception():
    mock_tool = Mock()
    mock_tool.handler.side_effect = Exception("Something went wrong")

    with patch(
        "app.ai.tools.executor.tool_registry.get",
        return_value=mock_tool,
    ):

        result = execute_tool(
            tool_name="failing_tool",
            parameters={"id": 1},
        )

    assert result["status"] == "failed"
    assert result["tool_name"] == "failing_tool"
    assert result["error"] == "Something went wrong"


@pytest.mark.parametrize(
    "invalid_result",
    [
        None,
        "invalid response",
        123,
        ["invalid"],
    ],
)
def test_execute_tool_invalid_response(invalid_result):
    mock_tool = Mock()
    mock_tool.handler.return_value = invalid_result

    with patch(
        "app.ai.tools.executor.tool_registry.get",
        return_value=mock_tool,
    ):

        result = execute_tool(
            tool_name="test_tool",
            parameters={},
        )

    assert result["status"] == "failed"
    assert result["tool_name"] == "test_tool"
    assert result["error"] == "Tool returned an invalid response."


@pytest.mark.parametrize(
    "invalid_parameters",
    [
        None,
        "parameters",
        [],
        123,
    ],
)
def test_execute_tool_invalid_parameters(invalid_parameters):
    mock_tool = Mock()

    with patch(
        "app.ai.tools.executor.tool_registry.get",
        return_value=mock_tool,
    ):

        with pytest.raises(
            ValueError,
            match="Tool parameters must be a dictionary",
        ):
            execute_tool(
                tool_name="test_tool",
                parameters=invalid_parameters,
            )