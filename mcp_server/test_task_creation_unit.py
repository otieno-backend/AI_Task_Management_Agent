import unittest
from datetime import date
from unittest.mock import patch

from task_creation import (
    extract_relative_due_date,
    validate_task_details,
)


TASK_SCHEMA = {
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "due_date": {"type": ["string", "null"]},
        "priority": {"type": "string"},
        "status": {"type": "string"},
        "category_id": {"type": ["integer", "null"]},
        "recurrence": {"type": "string"},
    }
}


class TestExtractRelativeDueDate(unittest.TestCase):

    @patch("task_creation.date")
    def test_extracts_tomorrow(self, mock_date):
        mock_date.today.return_value = date(2026, 10, 31)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = extract_relative_due_date("Create this task for tomorrow")

        self.assertEqual(result, "2026-11-01")

    @patch("task_creation.date")
    def test_extracts_today(self, mock_date):
        mock_date.today.return_value = date(2026, 10, 31)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = extract_relative_due_date("I need this task today")

        self.assertEqual(result, "2026-10-31")

    def test_returns_none_without_relative_date(self):
        result = extract_relative_due_date("Create a task to study Python")

        self.assertIsNone(result)


class TestValidateTaskDetails(unittest.TestCase):

    def test_valid_task_details(self):
        details = {
            "title": "  Learn Django  ",
            "description": "  Complete Django lessons  ",
            "priority": "high",
            "due_date": "2026-11-01",
            "status": "COMPLETED",
            "category_id": 2,
            "recurrence": "weekly",
        }

        result = validate_task_details(details, TASK_SCHEMA)

        self.assertEqual(result["title"], "Learn Django")
        self.assertEqual(result["description"], "Complete Django lessons")
        self.assertEqual(result["priority"], "HIGH")
        self.assertEqual(result["status"], "PENDING")
        self.assertEqual(result["recurrence"], "WEEKLY")
        self.assertEqual(result["due_date"], "2026-11-01")

    def test_rejects_empty_title(self):
        details = {"title": "   "}

        with self.assertRaises(ValueError):
            validate_task_details(details, TASK_SCHEMA)

    def test_rejects_invalid_priority(self):
        details = {"title": "Test task", "priority": "URGENT"}

        with self.assertRaises(ValueError):
            validate_task_details(details, TASK_SCHEMA)

    def test_rejects_invalid_recurrence(self):
        details = {"title": "Test task", "recurrence": "YEARLY"}

        with self.assertRaises(ValueError):
            validate_task_details(details, TASK_SCHEMA)

    def test_rejects_invalid_due_date(self):
        details = {"title": "Test task", "due_date": "tomorrow"}

        with self.assertRaises(ValueError):
            validate_task_details(details, TASK_SCHEMA)

    def test_rejects_invalid_category_id(self):
        details = {"title": "Test task", "category_id": "two"}

        with self.assertRaises(ValueError):
            validate_task_details(details, TASK_SCHEMA)

    def test_ignores_unsupported_fields(self):
        details = {
            "title": "Test task",
            "unknown_field": "This should be ignored",
        }

        result = validate_task_details(details, TASK_SCHEMA)

        self.assertNotIn("unknown_field", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)


from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from task_creation import create_task_flow


class TestCreateTaskFlow(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock()
        self.session.list_tools = AsyncMock()
        self.session.call_tool = AsyncMock()

        self.client = MagicMock()

        self.create_tool = SimpleNamespace(
            name="create_task",
            description="Create a task",
            input_schema=TASK_SCHEMA,
        )

        self.session.list_tools.return_value = SimpleNamespace(
            tools=[self.create_tool]
        )

        self.extracted_task = {
            "title": "Test confirmation",
            "description": "Testing confirmation",
            "priority": "HIGH",
            "due_date": None,
            "category_id": None,
            "recurrence": "NONE",
        }

    @patch("builtins.input", return_value="NO")
    @patch("task_creation.extract_task_details")
    async def test_no_confirmation_does_not_create_task(
        self, mock_extract, mock_input
    ):
        mock_extract.return_value = self.extracted_task

        await create_task_flow(
            self.session,
            self.client,
            "qwen2.5:3b",
            "Create a task called Test confirmation",
        )

        self.session.call_tool.assert_not_awaited()

    @patch("builtins.input", return_value="YES")
    @patch("task_creation.extract_task_details")
    async def test_yes_confirmation_creates_task_once(
        self, mock_extract, mock_input
    ):
        mock_extract.return_value = self.extracted_task

        self.session.call_tool.return_value = SimpleNamespace(
            is_error=False,
            content=[SimpleNamespace(text="Task created successfully.")],
        )

        await create_task_flow(
            self.session,
            self.client,
            "qwen2.5:3b",
            "Create a task called Test confirmation",
        )

        self.session.call_tool.assert_awaited_once()

        called_tool, called_task = self.session.call_tool.await_args.args

        self.assertEqual(called_tool, "create_task")
        self.assertEqual(called_task["title"], "Test confirmation")
        self.assertEqual(called_task["status"], "PENDING")

    @patch("builtins.input", return_value="YES")
    @patch("task_creation.extract_task_details")
    async def test_api_error_is_reported(
        self, mock_extract, mock_input
    ):
        mock_extract.return_value = self.extracted_task

        self.session.call_tool.return_value = SimpleNamespace(
            is_error=False,
            content=[SimpleNamespace(text="Error: Django API returned HTTP 500")],
        )

        with patch("builtins.print") as mock_print:
            await create_task_flow(
                self.session,
                self.client,
                "qwen2.5:3b",
                "Create a task called Test confirmation",
            )

        printed_text = " ".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertIn("Task creation failed:", printed_text)


    @patch("builtins.input", return_value="YES")
    @patch("task_creation.extract_task_details")
    async def test_mcp_error_flag_is_reported(
        self, mock_extract, mock_input
    ):
        mock_extract.return_value = self.extracted_task

        self.session.call_tool.return_value = SimpleNamespace(
            is_error=True,
            content=[SimpleNamespace(text="Internal MCP error")],
        )

        with patch("builtins.print") as mock_print:
            await create_task_flow(
                self.session,
                self.client,
                "qwen2.5:3b",
                "Create a task called Test confirmation",
            )

        printed_text = " ".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertIn("Task creation failed:", printed_text)

    async def test_missing_create_task_tool(self):
        self.session.list_tools.return_value = SimpleNamespace(tools=[])

        with patch("builtins.print") as mock_print:
            await create_task_flow(
                self.session,
                self.client,
                "qwen2.5:3b",
                "Create a task called Test confirmation",
            )

        self.session.call_tool.assert_not_awaited()
        mock_print.assert_called_with(
            "The create_task tool is not available."
        )
