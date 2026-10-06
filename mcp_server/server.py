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


if __name__ == "__main__":
    mcp.run()
