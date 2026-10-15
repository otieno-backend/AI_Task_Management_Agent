"""Anna Executa plugin for the Task Management API."""

import json
import os
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = os.getenv(
    "DJANGO_API_URL",
    "https://ai-task-management-agent.onrender.com/api",
).rstrip("/")

MANIFEST = {'display_name': 'Task Manager',
 'version': '0.1.1',
 'description': 'Create tasks, list tasks, summarize progress, and generate '
                'daily plans through an authenticated Django REST API.',
 'tools': [{'name': 'ping',
            'description': 'Check whether the task manager plugin is running.',
            'parameters': []},
           {'name': 'list_tasks',
            'description': 'List tasks belonging to the authenticated user.',
            'parameters': []},
           {'name': 'create_task',
            'description': 'Create a task for the authenticated user.',
            'parameters': [{'name': 'title',
                            'type': 'string',
                            'description': 'The task title.',
                            'required': True},
                           {'name': 'description',
                            'type': 'string',
                            'description': 'Optional details about the task.',
                            'required': False},
                           {'name': 'priority',
                            'type': 'string',
                            'description': 'LOW, MEDIUM, or HIGH. Defaults to '
                                           'MEDIUM.',
                            'required': False}]},
           {'name': 'get_task_summary',
            'description': 'Summarize task statuses and overdue tasks.',
            'parameters': []},
           {'name': 'get_daily_plan',
            'description': 'Prioritize unfinished tasks for a daily plan.',
            'parameters': []}],
 'name': 'task-manager',
 'credentials': [{'name': 'DJANGO_API_TOKEN',
                  'description': 'Authentication token for the connected '
                                 'Django Task Management API.',
                  'required': True,
                  'sensitive': True}],
 'host_capabilities': [],
 'runtime': {'type': 'binary'}}


def api_request(path, method="GET", data=None, token=None):
    token = token or os.getenv("DJANGO_API_TOKEN")
    if not token:
        return {
            "success": False,
            "error": "DJANGO_API_TOKEN is not configured.",
        }

    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/json",
    }
    body = None

    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")

    request = Request(
        f"{API_URL}/{path.lstrip('/')}",
        headers=headers,
        data=body,
        method=method,
    )

    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
            payload = json.loads(raw) if raw else {}
            return {"success": True, "data": payload}
    except HTTPError as exc:
        if exc.code in (401, 403):
            message = "The API rejected the credentials or denied access."
        elif exc.code == 404:
            message = "The requested task or endpoint was not found."
        elif exc.code == 400:
            message = "The API rejected the task data. Check the supplied fields."
        else:
            message = f"The task API returned HTTP {exc.code}."
        return {"success": False, "error": message}
    except URLError as exc:
        reason = getattr(exc, "reason", None)
        detail = type(reason).__name__ if reason is not None else type(exc).__name__
        return {
            "success": False,
            "error": f"Could not reach the Django API ({detail}). Check DJANGO_API_URL and network access.",
        }
    except TimeoutError:
        return {
            "success": False,
            "error": "The Django API request timed out.",
        }
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {
            "success": False,
            "error": "The API did not return valid JSON.",
        }


def extract_tasks(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list):
            return results
    return []


def list_tasks(token=None):
    result = api_request("tasks/", token=token)
    if not result["success"]:
        return result

    payload = result["data"]
    tasks = extract_tasks(payload)
    count = (
        payload.get("count", len(tasks))
        if isinstance(payload, dict)
        else len(tasks)
    )

    return {
        "success": True,
        "data": {"count": count, "results": tasks},
    }


def create_task(arguments, token=None):
    title = arguments.get("title", "")
    if not isinstance(title, str) or not title.strip():
        return {"success": False, "error": "Task title is required."}

    description = arguments.get("description", "")
    if not isinstance(description, str):
        return {
            "success": False,
            "error": "Task description must be text.",
        }

    priority = arguments.get("priority", "MEDIUM")
    if priority not in ("LOW", "MEDIUM", "HIGH"):
        return {
            "success": False,
            "error": "Priority must be LOW, MEDIUM, or HIGH.",
        }

    data = {
        "title": title.strip(),
        "description": description,
        "priority": priority,
        "status": "PENDING",
        "recurrence": "NONE",
    }

    result = api_request("tasks/", method="POST", data=data, token=token)
    if not result["success"]:
        return result
    return {"success": True, "data": result["data"]}


def get_task_summary(token=None):
    result = list_tasks(token=token)
    if not result["success"]:
        return result

    tasks = result["data"]["results"]
    counts = {
        "total": result["data"]["count"],
        "completed": 0,
        "pending": 0,
        "in_progress": 0,
        "cancelled": 0,
        "overdue": 0,
    }
    now = datetime.now(timezone.utc)

    for task in tasks:
        status = task.get("status", "")
        if status == "COMPLETED":
            counts["completed"] += 1
        elif status == "PENDING":
            counts["pending"] += 1
        elif status == "IN_PROGRESS":
            counts["in_progress"] += 1
        elif status == "CANCELLED":
            counts["cancelled"] += 1

        due_date = task.get("due_date")
        if due_date and status not in ("COMPLETED", "CANCELLED"):
            try:
                due = datetime.fromisoformat(
                    due_date.replace("Z", "+00:00")
                )
                if due.tzinfo is None:
                    due = due.replace(tzinfo=timezone.utc)
                if due < now:
                    counts["overdue"] += 1
            except (ValueError, TypeError):
                pass

    return {"success": True, "data": counts}


def get_daily_plan(token=None):
    result = list_tasks(token=token)
    if not result["success"]:
        return result

    tasks = result["data"]["results"]
    now = datetime.now(timezone.utc)
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    planned = []

    for task in tasks:
        if task.get("status") in ("COMPLETED", "CANCELLED"):
            continue

        due_date = task.get("due_date")
        due = None

        if due_date:
            try:
                due = datetime.fromisoformat(
                    due_date.replace("Z", "+00:00")
                )
                if due.tzinfo is None:
                    due = due.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                due = None

        if due is not None and due < now:
            reason, urgency = "OVERDUE", 0
        elif due is not None and due.date() == now.date():
            reason, urgency = "DUE TODAY", 1
        elif task.get("priority") == "HIGH":
            reason, urgency = "HIGH PRIORITY", 2
        else:
            reason, urgency = "UPCOMING", 3

        planned.append((
            urgency,
            priority_order.get(task.get("priority"), 3),
            due.timestamp() if due else float("inf"),
            {
                "id": task.get("id"),
                "title": task.get("title"),
                "status": task.get("status"),
                "priority": task.get("priority"),
                "due_date": due_date,
                "reason": reason,
            },
        ))

    planned.sort(key=lambda item: (item[0], item[1], item[2]))
    return {
        "success": True,
        "data": {
            "count": len(planned),
            "tasks": [item[3] for item in planned],
        },
    }


def invoke(method, args, token=None):
    if method == "ping":
        return {"success": True, "data": {"pong": True}}
    if method == "list_tasks":
        return list_tasks(token=token)
    if method == "create_task":
        return create_task(args, token=token)
    if method == "get_task_summary":
        return get_task_summary(token=token)
    if method == "get_daily_plan":
        return get_daily_plan(token=token)
    return {"success": False, "error": f"Unknown tool: {method}"}


def dispatch(envelope):
    method = envelope.get("method")
    request_id = envelope.get("id")

    if method == "initialize":
        result = {
            "protocolVersion": "2.0",
            "server_info": {
                "name": MANIFEST["display_name"],
                "version": MANIFEST["version"],
            },
            "capabilities": {},
        }
    elif method == "describe":
        result = MANIFEST
    elif method == "health":
        result = {"status": "ready"}
    elif method == "invoke":
        params = envelope.get("params") or {}
        tool_name = params.get("tool", "")
        arguments = params.get("arguments") or {}
        context = params.get("context") or {}
        credentials = context.get("credentials") or {}
        token = credentials.get("DJANGO_API_TOKEN")

        if not isinstance(arguments, dict):
            result = {
                "success": False,
                "error": "Tool arguments must be an object.",
            }
        elif token is not None and not isinstance(token, str):
            result = {
                "success": False,
                "error": "The configured API credential has an invalid format.",
            }
        else:
            result = invoke(tool_name, arguments, token=token)
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": "Unknown RPC method.",
            },
        }

    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main():
    for line in sys.stdin:
        try:
            envelope = json.loads(line)
            if not isinstance(envelope, dict):
                raise ValueError("Request must be a JSON object.")
            response = dispatch(envelope)
        except (json.JSONDecodeError, ValueError):
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Invalid JSON-RPC request.",
                },
            }

        # stdout is reserved for JSON-RPC messages.
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
