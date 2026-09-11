import pytest
from unittest.mock import patch

from app.ai.tools.runtime import execute_with_retry


def test_success_on_first_attempt():
    with patch(
        "app.ai.tools.runtime.execute_tool",
        return_value={"status": "success", "result": "done"},
    ) as mock_execute:

        result = execute_with_retry(
            tool_name="invoice",
            parameters={"id": 1},
        )

    assert result["status"] == "success"
    assert result["result"] == "done"
    assert result["attempts"] == 1
    assert mock_execute.call_count == 1


def test_success_after_retry():
    with patch(
        "app.ai.tools.runtime.execute_tool",
        side_effect=[
            {"status": "failed", "error": "temporary error"},
            {"status": "success", "result": "done"},
        ],
    ) as mock_execute:

        result = execute_with_retry(
            tool_name="invoice",
            parameters={"id": 1},
            max_attempts=3,
        )

    assert result["status"] == "success"
    assert result["result"] == "done"
    assert result["attempts"] == 2
    assert mock_execute.call_count == 2


def test_all_attempts_fail():
    with patch(
        "app.ai.tools.runtime.execute_tool",
        return_value={"status": "failed", "error": "error"},
    ) as mock_execute:

        result = execute_with_retry(
            tool_name="invoice",
            parameters={"id": 1},
            max_attempts=3,
        )

    assert result["status"] == "failed"
    assert result["attempts"] == 3
    assert mock_execute.call_count == 3


def test_single_attempt_failure():
    with patch(
        "app.ai.tools.runtime.execute_tool",
        return_value={"status": "failed", "error": "failed"},
    ) as mock_execute:

        result = execute_with_retry(
            tool_name="invoice",
            parameters={},
            max_attempts=1,
        )

    assert result["status"] == "failed"
    assert result["attempts"] == 1
    assert mock_execute.call_count == 1


@pytest.mark.parametrize("max_attempts", [0, -1, -5])
def test_invalid_max_attempts(max_attempts):
    with pytest.raises(
        ValueError,
        match="max_attempts must be at least 1",
    ):
        execute_with_retry(
            tool_name="invoice",
            parameters={},
            max_attempts=max_attempts,
        )