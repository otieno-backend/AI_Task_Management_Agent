import sys
import os
import requests
from typing import Optional
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

load_dotenv()

mcp = MCPServer("Task Management Server")

DJANGO_API_URL = os.getenv(
    "DJANGO_API_URL",
    "http://127.0.0.1:8000/api"
)

DJANGO_API_TOKEN = os.getenv("DJANGO_API_TOKEN")


def get_headers():
    return {
        "Authorization": f"Token {DJANGO_API_TOKEN}",
        "Content-Type": "application/json",
    }


@mcp.tool()
def hello_task_manager() -> str:
    """A simple test tool for the Task Management MCP server."""
    return "Hello! The Task Management MCP server is working."


@mcp.tool()
def list_tasks() -> str:
    """List tasks from the Django Task Management API."""

    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code == 200:
            return str(response.json())

        return (
            f"Error: Django API returned HTTP "
            f"{response.status_code}: {response.text}"
        )

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"


@mcp.tool()
def create_task(
    title: str,
    description: str = "",
    due_date: Optional[str] = None,
    priority: str = "MEDIUM",
    status: str = "PENDING",
    category_id: Optional[int] = None,
    recurrence: str = "NONE",
) -> str:
    """Create a new task in the Django Task Management API."""

    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    data = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "recurrence": recurrence,
    }

    if due_date is not None:
        data["due_date"] = due_date

    if category_id is not None:
        data["category_id"] = category_id

    try:
        response = requests.post(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            json=data,
            timeout=10,
        )

        if response.status_code in (200, 201):
            return str(response.json())

        return (
            f"Error: Django API returned HTTP "
            f"{response.status_code}: {response.text}"
        )

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"


@mcp.tool()
def get_task(task_id: int) -> str:
    """Get a specific task from the Django Task Management API."""

    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/{task_id}/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code == 200:
            return str(response.json())

        if response.status_code == 404:
            return f"Error: Task {task_id} was not found."

        return (
            f"Error: Django API returned HTTP "
            f"{response.status_code}: {response.text}"
        )

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"


@mcp.tool()
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    recurrence: Optional[str] = None,
) -> str:
    """Update one or more fields of an existing task."""

    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    data = {}

    if title is not None:
        data["title"] = title

    if description is not None:
        data["description"] = description

    if due_date is not None:
        data["due_date"] = due_date

    if priority is not None:
        data["priority"] = priority

    if status is not None:
        data["status"] = status

    if category_id is not None:
        data["category_id"] = category_id

    if recurrence is not None:
        data["recurrence"] = recurrence

    if not data:
        return "Error: At least one field must be provided for update."

    try:
        response = requests.patch(
            f"{DJANGO_API_URL}/tasks/{task_id}/",
            headers=get_headers(),
            json=data,
            timeout=10,
        )

        if response.status_code == 200:
            return str(response.json())

        if response.status_code == 404:
            return f"Error: Task {task_id} was not found."

        return (
            f"Error: Django API returned HTTP "
            f"{response.status_code}: {response.text}"
        )

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task as completed using the Django Task Management API."""

    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    try:
        response = requests.patch(
            f"{DJANGO_API_URL}/tasks/{task_id}/complete/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code in (200, 201):
            return str(response.json())

        if response.status_code == 404:
            return f"Error: Task {task_id} was not found."

        return (
            f"Error: Django API returned HTTP "
            f"{response.status_code}: {response.text}"
        )

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"


@mcp.tool()
def find_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[int] = None,
    due_date: Optional[str] = None,
) -> str:
    """Find tasks using optional status, priority, category, or due date filters."""
    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    params = {}

    if status is not None:
        params["status"] = status

    if priority is not None:
        params["priority"] = priority

    if category is not None:
        params["category"] = category

    if due_date is not None:
        params["due_date"] = due_date

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            params=params,
            timeout=10,
        )

        if response.status_code == 200:
            return str(response.json())

        return (
            f"Error: Django API returned HTTP "
            f"{response.status_code}: {response.text}"
        )

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"


@mcp.tool()
def find_overdue_tasks() -> str:
    """Find unfinished tasks whose due date has passed."""
    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code != 200:
            return (
                f"Error: Django API returned HTTP "
                f"{response.status_code}: {response.text}"
            )

        tasks = response.json().get("results", [])

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        overdue_tasks = []

        for task in tasks:
            due_date = task.get("due_date")
            status = task.get("status")

            if not due_date:
                continue

            if status == "COMPLETED":
                continue

            due = datetime.fromisoformat(
                due_date.replace("Z", "+00:00")
            )

            if due < now:
                overdue_tasks.append(task)

        return str(overdue_tasks)

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"
    except (ValueError, TypeError) as exc:
        return f"Error processing task dates: {exc}"


@mcp.tool()
def get_task_summary() -> str:
    """Return a simple summary of the user's tasks."""
    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code != 200:
            return (
                f"Error: Django API returned HTTP "
                f"{response.status_code}: {response.text}"
            )

        tasks = response.json().get("results", [])

        from datetime import datetime, timezone

        total = len(tasks)
        completed = 0
        pending = 0
        in_progress = 0
        cancelled = 0
        overdue = 0

        now = datetime.now(timezone.utc)

        for task in tasks:
            task_status = task.get("status")
            due_date = task.get("due_date")

            if task_status == "COMPLETED":
                completed += 1
            elif task_status == "PENDING":
                pending += 1
            elif task_status == "IN_PROGRESS":
                in_progress += 1
            elif task_status == "CANCELLED":
                cancelled += 1

            if (
                due_date
                and task_status != "COMPLETED"
            ):
                due = datetime.fromisoformat(
                    due_date.replace("Z", "+00:00")
                )

                if due < now:
                    overdue += 1

        summary = (
            f"Task Summary:\n"
            f"Total tasks: {total}\n"
            f"Completed: {completed}\n"
            f"Pending: {pending}\n"
            f"In progress: {in_progress}\n"
            f"Cancelled: {cancelled}\n"
            f"Overdue: {overdue}"
        )

        return summary

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"
    except (ValueError, TypeError) as exc:
        return f"Error processing task data: {exc}"


@mcp.tool()
def find_tasks_due_soon(days: int = 3) -> str:
    """Find unfinished tasks due within the next number of days."""
    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    if days < 1:
        return "Error: days must be at least 1."

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code != 200:
            return (
                f"Error: Django API returned HTTP "
                f"{response.status_code}: {response.text}"
            )

        tasks = response.json().get("results", [])

        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        deadline = now + timedelta(days=days)

        due_soon = []

        for task in tasks:
            task_status = task.get("status")
            due_date = task.get("due_date")

            if not due_date:
                continue

            if task_status == "COMPLETED":
                continue

            due = datetime.fromisoformat(
                due_date.replace("Z", "+00:00")
            )

            if now <= due <= deadline:
                due_soon.append(task)

        return str(due_soon)

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"
    except (ValueError, TypeError) as exc:
        return f"Error processing task dates: {exc}"


@mcp.tool()
def get_next_tasks(limit: int = 5) -> str:
    """Return the most urgent unfinished tasks based on status, priority, and due date."""
    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    if limit < 1:
        return "Error: limit must be at least 1."

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code != 200:
            return (
                f"Error: Django API returned HTTP "
                f"{response.status_code}: {response.text}"
            )

        tasks = response.json().get("results", [])

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        priority_order = {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }

        unfinished_tasks = []

        for task in tasks:
            status = task.get("status")

            if status in ("COMPLETED", "CANCELLED"):
                continue

            due_date = task.get("due_date")

            if due_date:
                due = datetime.fromisoformat(
                    due_date.replace("Z", "+00:00")
                )
            else:
                due = None

            if due is not None and due < now:
                urgency = 0
            else:
                urgency = 1

            priority = priority_order.get(
                task.get("priority"),
                3,
            )

            due_timestamp = (
                due.timestamp()
                if due is not None
                else float("inf")
            )

            unfinished_tasks.append(
                (
                    urgency,
                    priority,
                    due_timestamp,
                    task,
                )
            )

        unfinished_tasks.sort(
            key=lambda item: (
                item[0],
                item[1],
                item[2],
            )
        )

        next_tasks = [
            item[3]
            for item in unfinished_tasks[:limit]
        ]

        return str(next_tasks)

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"
    except (ValueError, TypeError) as exc:
        return f"Error processing task data: {exc}"

@mcp.tool()
def get_today_tasks() -> str:
    """Return unfinished tasks that are overdue or due today."""
    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code != 200:
            return (
                f"Error: Django API returned HTTP "
                f"{response.status_code}: {response.text}"
            )

        tasks = response.json().get("results", [])

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        today = now.date()

        today_tasks = []

        for task in tasks:
            status = task.get("status")
            due_date = task.get("due_date")

            if status in ("COMPLETED", "CANCELLED"):
                continue

            if not due_date:
                continue

            due = datetime.fromisoformat(
                due_date.replace("Z", "+00:00")
            )

            if due.date() <= today:
                today_tasks.append(task)

        return str(today_tasks)

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"
    except (ValueError, TypeError) as exc:
        return f"Error processing task dates: {exc}"

@mcp.tool()
def get_daily_plan() -> str:
    """Create a simple daily plan from unfinished tasks."""
    if not DJANGO_API_TOKEN:
        return "Error: DJANGO_API_TOKEN is not configured."

    try:
        response = requests.get(
            f"{DJANGO_API_URL}/tasks/",
            headers=get_headers(),
            timeout=10,
        )

        if response.status_code != 200:
            return (
                f"Error: Django API returned HTTP "
                f"{response.status_code}: {response.text}"
            )

        tasks = response.json().get("results", [])

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        today = now.date()

        priority_order = {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }

        planned_tasks = []

        for task in tasks:
            status = task.get("status")

            if status in ("COMPLETED", "CANCELLED"):
                continue

            due_date = task.get("due_date")

            if due_date:
                due = datetime.fromisoformat(
                    due_date.replace("Z", "+00:00")
                )
            else:
                due = None

            if due is not None and due < now:
                urgency = 0
                reason = "OVERDUE"
            elif due is not None and due.date() == today:
                urgency = 1
                reason = "DUE TODAY"
            elif task.get("priority") == "HIGH":
                urgency = 2
                reason = "HIGH PRIORITY"
            else:
                urgency = 3
                reason = "UPCOMING"

            priority = priority_order.get(
                task.get("priority"),
                3,
            )

            due_timestamp = (
                due.timestamp()
                if due is not None
                else float("inf")
            )

            planned_tasks.append(
                (
                    urgency,
                    priority,
                    due_timestamp,
                    task,
                    reason,
                )
            )

        planned_tasks.sort(
            key=lambda item: (
                item[0],
                item[1],
                item[2],
            )
        )

        if not planned_tasks:
            return "Daily Plan:\nNo unfinished tasks. Great job!"

        lines = ["Daily Plan:"]

        for number, item in enumerate(planned_tasks, start=1):
            task = item[3]
            reason = item[4]

            lines.append(
                f"{number}. {task.get('title')} "
                f"[{reason}] - "
                f"Priority: {task.get('priority')}"
            )

        return "\n".join(lines)

    except requests.RequestException as exc:
        return f"Error connecting to Django API: {exc}"
    except (ValueError, TypeError) as exc:
        return f"Error processing task data: {exc}"

print(
    "REGISTERED TOOLS:",
    len(mcp._tool_manager._tools),
    file=sys.stderr
)

print(
    "REGISTERED TOOL NAMES:",
    list(mcp._tool_manager._tools.keys()),
    file=sys.stderr
)

if __name__ == "__main__":
    mcp.run()
