"""Ollama-powered AI task management agent."""

import json
import os
import re
import sys
from pathlib import Path

import anyio
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from openai import OpenAI
from task_creation import create_task_flow
from task_updating import update_task_flow

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434/v1",
)
SERVER_PATH = BASE_DIR / "server.py"

READ_ONLY_TOOLS = {
    "list_tasks",
    "get_task",
    "find_tasks",
    "find_overdue_tasks",
    "get_task_summary",
    "find_tasks_due_soon",
    "get_next_tasks",
    "get_today_tasks",
    "get_daily_plan",
}

SYSTEM_INSTRUCTIONS = """
You are an intelligent AI task management assistant.

Help the user understand their tasks and decide what to work on next
using only actual task data returned by the application's tools.

STRICT DATA RULES:
- Never invent task titles, IDs, priorities, statuses, dates, or statistics.
- A null or missing due_date means no due date is recorded.
- Never describe a task as overdue, due today, or due soon unless its
  actual due_date and the current date support that conclusion.
- Never treat a missing due date as today's date or a future date.
- Distinguish task priority from deadline urgency.
- HIGH priority does not prove that a task has an urgent deadline.
- A missing due date means deadline urgency is unknown, not that the
  task is urgent, overdue, or due earliest.
- If task data is unavailable or incomplete, explain the limitation.
- Never claim a task was created, updated, or completed unless an
  appropriate tool actually performed that action.

TASK ORDERING RULES:
- Python has already sorted the supplied unfinished tasks.
- Preserve the exact order supplied by Python.
- Do not independently reorder, remove, or add tasks.
- Known overdue tasks appear before tasks due today.
- Tasks due today appear before tasks with future deadlines.
- Tasks with missing or invalid due dates appear after tasks with
  known deadlines.
- Priority determines order within the same deadline category.
- Deadline urgency takes precedence over priority.
- A missing due date does not establish deadline urgency.

RECOMMENDATION RULES:
1. Recommend the first unfinished task in the supplied ordered list.
2. Explain why it appears first using its actual deadline category
   and priority.
3. Never claim that a task is urgent solely because its priority is HIGH.
4. Never describe a task with no due date as the earliest due task.
5. If all tasks have missing due dates, explicitly explain:
   "No tasks have recorded deadlines, so deadline urgency cannot
   be compared. This task appears first because it has the highest
   priority among the supplied tasks."
6. If tasks have known deadlines, explain the deadline ordering first
   and use priority to explain ties.
7. Recommend only tasks present in the supplied task data.
8. Suggest practical next actions only when supported by the task title
   or description.
9. Do not suggest changing a task's status unless the user has requested
   that action and the available information supports it.
10. If no unfinished tasks exist, say so clearly.

RESPONSE FORMAT:

1. TOP RECOMMENDATION
   - Task title
   - Actual priority and status
   - Recorded due date, or "No due date recorded"
   - Why this task appears first
   - One practical next action supported by its title or description

2. OTHER TASKS
   - List EVERY other unfinished task in the supplied task data.
   - Preserve the supplied task order.
   - Include each task's actual title, priority, status, and due date.
   - Write "No due date recorded" when due_date is null or missing.
   - Do not duplicate the top recommendation.
   - If there are no other unfinished tasks, say so clearly.

3. MISSING INFORMATION
   - Identify missing due dates or other information that prevents
     a reliable urgency assessment.
   - If all due dates are missing, explicitly state that deadline
     urgency cannot be compared.
   - Do not ask for information that is already available.

STYLE:
- Be concise, specific, and practical.
- Use simple language.
- Separate recorded facts from recommendations.
- Never invent deadlines, urgency, task details, or completed work.
"""


def build_openai_tools(mcp_tools):
    """Convert permitted MCP tools to OpenAI-compatible schemas."""
    tools = []

    for tool in mcp_tools:
        if tool.name not in READ_ONLY_TOOLS:
            continue

        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or tool.name,
                "parameters": tool.input_schema,
            },
        })

    return tools


def get_function_calls(response):
    """Extract tool calls from a chat completion."""
    message = response.choices[0].message
    return message.tool_calls or []


def get_text_result(result):
    """Convert MCP tool output to text."""
    if result.is_error:
        return "The task tool reported an error."

    parts = [
        item.text
        for item in (result.content or [])
        if hasattr(item, "text")
    ]
    return "\n".join(parts) if parts else "The tool returned no text."


from datetime import date
import json


def parse_tasks(task_data):
    """Parse task data and report API errors clearly."""
    import ast

    if not isinstance(task_data, str) or not task_data.strip():
        raise ValueError("The task API returned an empty response.")

    # MCP may return an API error as plain text.
    if task_data.lstrip().startswith("Error"):
        raise RuntimeError(task_data)

    try:
        data = json.loads(task_data)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(task_data)
        except (ValueError, SyntaxError) as exc:
            raise ValueError(
                "The task API returned data in an unexpected format."
            ) from exc

    if isinstance(data, dict):
        if "error" in data:
            raise RuntimeError(str(data["error"]))
        tasks = data.get("results", [])
    elif isinstance(data, list):
        tasks = data
    else:
        raise ValueError("Unexpected task-list response format.")

    if not isinstance(tasks, list):
        raise ValueError("The task list is not a valid list.")

    if not all(isinstance(task, dict) for task in tasks):
        raise ValueError("The task list contains an invalid entry.")

    return tasks


def summarize_missing_information(tasks):
    """Report missing due dates based on actual task data."""
    missing_due_dates = [
        task.get("title", "Untitled task")
        for task in tasks
        if not task.get("due_date")
    ]

    if not missing_due_dates:
        return "All tasks have a recorded due date."

    titles = ", ".join(missing_due_dates)
    return (
        f"No due date is recorded for: {titles}. "
        "Deadline urgency cannot be determined for these tasks."
    )


def rank_tasks(tasks):
    """Sort unfinished tasks by known deadline, then priority."""
    today = date.today()

    priority_order = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2,
    }

    finished_statuses = {
        "COMPLETED",
        "CANCELLED",
        "CANCELED",
    }

    def sort_key(task):
        status = str(task.get("status") or "").upper()
        priority = str(task.get("priority") or "").upper()
        due_value = task.get("due_date")

        due_date = None
        if due_value:
            try:
                due_date = date.fromisoformat(str(due_value)[:10])
            except ValueError:
                pass

        if due_date and due_date < today:
            deadline_rank = 0  # Overdue
        elif due_date == today:
            deadline_rank = 1  # Due today
        elif due_date:
            deadline_rank = 2  # Future deadline
        else:
            deadline_rank = 3  # Missing or invalid deadline

        return (
            deadline_rank,
            priority_order.get(priority, 3),
            str(task.get("title") or "").casefold(),
        )

    unfinished = [
        task for task in tasks
        if str(task.get("status") or "").upper()
        not in finished_statuses
    ]

    return sorted(unfinished, key=sort_key)

def is_task_creation_request(user_message):
    """Recognize explicit requests to create or add a task."""
    pattern = (
        r"^(?:(?:please|can you|could you|would you|"
        r"i want you to|i need you to)\s+)*"
        r"(?:create|add|make)\b.*\b(?:task|todo)\b"
    )
    return bool(re.search(pattern, user_message.strip(), re.IGNORECASE))


async def run_agent(user_message: str):
    """Fetch real tasks first, then ask Ollama to reason over them."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )

    try:
        client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Handle explicit task-creation requests separately.
                if is_task_creation_request(user_message):
                    await create_task_flow(
                        session,
                        client,
                        MODEL,
                        user_message,
                    )
                    return

                # Always retrieve the real task list before planning.
                result = await session.call_tool("list_tasks", {})
                task_data = get_text_result(result)

                if result.is_error:
                    print("Could not retrieve your real tasks:")
                    print(task_data)
                    return

                try:
                    tasks = parse_tasks(task_data)
                except RuntimeError as exc:
                    print("Task API error:", exc)
                    return
                except ValueError as exc:
                    print("Could not read the API task list:", exc)
                    return

                # Handle explicit task-update requests.
                if is_task_update_request(user_message):
                    await update_task_flow(
                        session,
                        client,
                        MODEL,
                        user_message,
                        tasks,
                    )
                    return

                ranked_tasks = rank_tasks(tasks)
                ranked_task_data = json.dumps(ranked_tasks, indent=2)
                missing_information = summarize_missing_information(tasks)

                messages = [
                    {
                        "role": "system",
                        "content": SYSTEM_INSTRUCTIONS
                        + "\\n\\nPython has already sorted the unfinished tasks. "
                          "Preserve the exact task order supplied below. "
                          "Do not invent reasons based on update history, "
                          "deadlines, or facts absent from the data. "
                          "Explain recommendations using only recorded fields.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"User request:\\n{user_message}\\n\\n"
                            "Actual unfinished tasks, sorted by Python "
                            "(highest recommendation first):\\n"
                            f"{ranked_task_data}\\n\\n"
                            "Recommend the first task, explain why using its "
                            "actual priority and recorded due date, and list "
                            "every remaining task in the supplied order. "
                            "For each task include its title, priority, status, "
                            "and due date. If due_date is null, say "
                            "'No due date recorded'. Do not change the order.\\n\\n"
                            f"Verified missing-information summary: "
                            f"{missing_information}\\n"
                            "Use this exact factual summary in the MISSING "
                            "INFORMATION section. Do not contradict it."
                        ),
                    },
                ]

                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                )

                print("\nAI Task Manager:\n")
                print(
                    response.choices[0].message.content
                    or "The AI did not return a text response."
                )

    except Exception as exc:
        print(
            f"Agent error ({type(exc).__name__}). "
            "Check API access, configuration, and server logs."
        )


def is_task_update_request(user_message):
    """Recognize explicit requests to update an existing task."""
    pattern = (
        r"^(?:(?:please|can you|could you|would you|"
        r"i want you to|i need you to)\s+)*"
        r"(?:update|edit|change|modify)\b.*\b(?:task|todo)\b"
    )
    return bool(re.search(pattern, user_message.strip(), re.IGNORECASE))


if __name__ == "__main__":
    message = input("What would you like help with? ").strip()
    if message:
        anyio.run(run_agent, message)
    else:
        print("Please enter a question about your tasks.")
