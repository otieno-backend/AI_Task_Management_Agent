"""AI-assisted task updating with explicit user confirmation."""

import json
from datetime import date

from task_creation import get_tool_text


UPDATE_FIELDS = {
    "title",
    "description",
    "due_date",
    "priority",
    "status",
    "category_id",
    "recurrence",
}


def extract_update_details(client, model, user_message, tool_schema, tasks):
    """Ask Qwen to identify the target task and requested changes."""

    today = date.today().isoformat()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract task update details from the user's request. "
                    f"Today's date is {today}. "
                    "Identify the target using an existing task ID from "
                    "the supplied task list. Never invent a task ID. "
                    "Only include fields the user explicitly wants to change. "
                    "Do not invent values for unspecified fields. "
                    "Convert relative dates to YYYY-MM-DD. "
                    "Return only the update_task function arguments."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"User request: {user_message}\n\n"
                    f"Existing tasks: {json.dumps(tasks)}"
                ),
            },
        ],
        tools=[tool_schema],
        tool_choice={
            "type": "function",
            "function": {"name": "update_task"},
        },
    )

    message = response.choices[0].message

    if not message.tool_calls:
        raise ValueError("The AI could not identify the requested changes.")

    call = message.tool_calls[0]

    if call.function.name != "update_task":
        raise ValueError("The AI returned an unexpected function.")

    return json.loads(call.function.arguments)


def validate_update_details(details, tasks):
    """Validate the target task and requested field changes."""

    task_id = details.get("task_id")

    if isinstance(task_id, bool) or not isinstance(task_id, int):
        raise ValueError("A valid task ID is required.")

    matching_tasks = [
        task for task in tasks
        if task.get("id") == task_id
    ]

    if len(matching_tasks) != 1:
        raise ValueError(
            "The requested task could not be identified uniquely."
        )

    changes = {
        key: value
        for key, value in details.items()
        if key in UPDATE_FIELDS and value is not None
    }

    if not changes:
        raise ValueError("No task changes were provided.")

    if "title" in changes:
        if not isinstance(changes["title"], str) or not changes["title"].strip():
            raise ValueError("The task title cannot be empty.")
        changes["title"] = changes["title"].strip()

    if "description" in changes:
        if not isinstance(changes["description"], str):
            raise ValueError("The description must be text.")

    if "priority" in changes:
        changes["priority"] = str(changes["priority"]).upper()
        if changes["priority"] not in {"HIGH", "MEDIUM", "LOW"}:
            raise ValueError("Invalid task priority.")

    if "status" in changes:
        changes["status"] = str(changes["status"]).upper()
        if changes["status"] not in {
            "PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"
        }:
            raise ValueError("Invalid task status.")

    if "recurrence" in changes:
        changes["recurrence"] = str(changes["recurrence"]).upper()
        if changes["recurrence"] not in {
            "NONE", "DAILY", "WEEKLY", "MONTHLY"
        }:
            raise ValueError("Invalid recurrence.")

    if "due_date" in changes:
        due_date = changes["due_date"]

        if not isinstance(due_date, str):
            raise ValueError("The due date must be text.")

        if due_date:
            try:
                changes["due_date"] = date.fromisoformat(
                    due_date
                ).isoformat()
            except ValueError as exc:
                raise ValueError(
                    "Use a valid due date in YYYY-MM-DD format."
                ) from exc

    if "category_id" in changes:
        category_id = changes["category_id"]

        if (
            isinstance(category_id, bool)
            or not isinstance(category_id, int)
        ):
            raise ValueError("The category ID must be an integer.")

    return matching_tasks[0], changes


async def update_task_flow(session, client, model, user_message, tasks):
    """Preview and confirm an update before calling the API."""

    tools_result = await session.list_tools()

    update_tool = next(
        (tool for tool in tools_result.tools if tool.name == "update_task"),
        None,
    )

    if update_tool is None:
        print("The update_task tool is not available.")
        return

    tool_schema = {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": update_tool.description or "Update a task",
            "parameters": update_tool.input_schema,
        },
    }

    try:
        extracted = extract_update_details(
            client, model, user_message, tool_schema, tasks
        )
        task, changes = validate_update_details(extracted, tasks)

    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Could not prepare the update: {exc}")
        return

    print("\nTASK UPDATE PREVIEW")
    print("-------------------")
    print(f"Task ID: {task['id']}")
    print(f"Current title: {task.get('title', 'Unknown')}")

    for field, value in changes.items():
        print(f"{field}: {task.get(field)} -> {value}")

    confirmation = input(
        "\nType YES to update this task, or NO to cancel: "
    ).strip().casefold()

    if confirmation != "yes":
        print("Task update cancelled. Nothing was changed.")
        return

    result = await session.call_tool(
        "update_task",
        {"task_id": task["id"], **changes},
    )

    result_text = get_tool_text(result)

    print("\nTASK UPDATE RESULT")

    if result.is_error or result_text.lstrip().startswith("Error:"):
        print("Task update failed:")
    else:
        print("Task update completed:")

    print(result_text)
