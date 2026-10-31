import unittest

from task_updating import validate_update_details


class ValidateUpdateDetailsTests(unittest.TestCase):

    def setUp(self):
        self.tasks = [
            {
                "id": 1,
                "title": "Complete API project",
                "description": "Finish the backend API",
                "priority": "LOW",
                "status": "PENDING",
                "due_date": "2026-11-01",
                "recurrence": "NONE",
            }
        ]

    def test_valid_priority_update(self):
        task, changes = validate_update_details(
            {"task_id": 1, "priority": "HIGH"},
            self.tasks,
        )

        self.assertEqual(task["id"], 1)
        self.assertEqual(changes, {"priority": "HIGH"})

    def test_valid_status_update(self):
        task, changes = validate_update_details(
            {"task_id": 1, "status": "IN_PROGRESS"},
            self.tasks,
        )

        self.assertEqual(changes, {"status": "IN_PROGRESS"})

    def test_unknown_task_id_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_update_details(
                {"task_id": 999, "priority": "HIGH"},
                self.tasks,
            )

    def test_boolean_task_id_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_update_details(
                {"task_id": True, "priority": "HIGH"},
                self.tasks,
            )

    def test_empty_update_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_update_details(
                {"task_id": 1},
                self.tasks,
            )

    def test_invalid_priority_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_update_details(
                {"task_id": 1, "priority": "URGENT"},
                self.tasks,
            )

    def test_invalid_status_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_update_details(
                {"task_id": 1, "status": "WAITING"},
                self.tasks,
            )

    def test_empty_title_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_update_details(
                {"task_id": 1, "title": "   "},
                self.tasks,
            )

    def test_invalid_due_date_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_update_details(
                {"task_id": 1, "due_date": "next Friday"},
                self.tasks,
            )


if __name__ == "__main__":
    unittest.main()
