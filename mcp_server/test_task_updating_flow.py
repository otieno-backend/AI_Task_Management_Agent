import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from task_updating import update_task_flow


class UpdateTaskFlowTests(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.tasks = [
            {
                "id": 1,
                "title": "Complete API project",
                "priority": "LOW",
                "status": "PENDING",
            }
        ]

        self.update_tool = SimpleNamespace(
            name="update_task",
            description="Update an existing task",
            input_schema={"type": "object", "properties": {}},
        )

        self.session = SimpleNamespace(
            list_tools=AsyncMock(
                return_value=SimpleNamespace(
                    tools=[self.update_tool]
                )
            ),
            call_tool=AsyncMock(),
        )

        self.client = SimpleNamespace()

        self.extracted_details = {
            "task_id": 1,
            "priority": "HIGH",
        }

        self.success_result = SimpleNamespace(is_error=False)

    @patch("task_updating.extract_update_details")
    @patch("builtins.input", return_value="NO")
    async def test_no_cancels_update(self, mock_input, mock_extract):
        mock_extract.return_value = self.extracted_details

        await update_task_flow(
            self.session,
            self.client,
            "qwen2.5:3b",
            "Update my task priority",
            self.tasks,
        )

        self.session.call_tool.assert_not_awaited()

    @patch("task_updating.get_tool_text")
    @patch("task_updating.extract_update_details")
    @patch("builtins.input", return_value="YES")
    async def test_yes_calls_update_tool(
        self, mock_input, mock_extract, mock_get_text
    ):
        mock_extract.return_value = self.extracted_details
        mock_get_text.return_value = "Task updated successfully."
        self.session.call_tool.return_value = self.success_result

        await update_task_flow(
            self.session,
            self.client,
            "qwen2.5:3b",
            "Update my task priority",
            self.tasks,
        )

        self.session.call_tool.assert_awaited_once_with(
            "update_task",
            {"task_id": 1, "priority": "HIGH"},
        )

    async def test_missing_update_tool_does_not_call_api(self):
        self.session.list_tools.return_value = SimpleNamespace(tools=[])

        await update_task_flow(
            self.session,
            self.client,
            "qwen2.5:3b",
            "Update my task priority",
            self.tasks,
        )

        self.session.call_tool.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
