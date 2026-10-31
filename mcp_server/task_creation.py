"""AI-assisted task creation with explicit user confirmation."""

import json
import re
from datetime import date, timedelta

from mcp import ClientSession
from openai import OpenAI


def get_tool_text(result):
    """Extract readable text from an MCP result."""
    return "\n".join(
        item.text
        for item in (result.content or [])
        if hasattr(item, "text")
    ) or "The task tool returned no message."



def extract_relative_due_date(user_message):
    """Convert clear relative due dates into YYYY-MM-DD."""
    message = user_message.casefold()
    today = date.today()

    if re.search(r"\btomorrow\b", message):
        return (today + timedelta(days=1)).isoformat()

    if re.search(r"\btoday\b", message):
        return today.isoformat()

    return None


def extract_task_details(client, model, user_message, tool_schema):
    """Ask Qwen to extract task details without creating anything."""
    today = date.today().isoformat()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract task details from the user's request. "
                    "Do not create, update, or complete tasks. "
                    f"Today's date is {today}. "
                    "Convert clear relative dates into YYYY-MM-DD. "
                    "If a date is not supplied, use null. "
                    "If priority is not supplied, use MEDIUM. "
                    "Use PENDING for status and NONE for recurrence "
                    "unless the user clearly requests recurrence. "
                    "Never invent a category ID. "
                    "Return only the create_task function arguments."
                ),
            },
            {"role": "user", "content": user_message},
        ],
        tools=[tool_schema],
        tool_choice={
            "type": "function",
            "function": {"name": "create_task"},
        },
    )

    message = response.choices[0].message

    if not message.tool_calls:
        raise ValueError("The AI could not extract the task details.")

    call = message.tool_calls[0]

    if call.function.name != "create_task":
        raise ValueError("The AI returned an unexpected function.")

    return json.loads(call.function.arguments)


def validate_task_details(details, schema):
    """Validate and normalize task details before showing a preview."""
    properties = schema.get("properties", {})
    allowed_fields = set(properties)

    # Ignore any fields not accepted by the actual MCP tool.
    details = {
        key: value
        for key, value in details.items()
        if key in allowed_fields
    }

    title = details.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("A valid task title is required.")

    details["title"] = title.strip()

    description = details.get("description")
    details["description"] = (
        description.strip()
        if isinstance(description, str)
        else ""
    )

    priority = str(details.get("priority") or "MEDIUM").upper()
    if priority not in {"HIGH", "MEDIUM", "LOW"}:
        raise ValueError("Invalid priority returned by the AI.")

    details["priority"] = priority

    # New tasks always start as pending.
    details["status"] = "PENDING"

    # Validate recurrence against Django model choices.
    recurrence = str(details.get("recurrence") or "NONE").upper()

    if recurrence not in {"NONE", "DAILY", "WEEKLY", "MONTHLY"}:
        raise ValueError("Invalid recurrence returned by the AI.")

    details["recurrence"] = recurrence

    due_date = details.get("due_date")
    if due_date in ("", None):
        details["due_date"] = None
    else:
        if not isinstance(due_date, str):
            raise ValueError("The due date must be a valid date string.")

        try:
            parsed_date = date.fromisoformat(due_date)
            details["due_date"] = parsed_date.isoformat()
        except ValueError as exc:
            raise ValueError(
                "The AI returned an invalid due date. Use YYYY-MM-DD."
            ) from exc

    category_id = details.get("category_id")
    if category_id is not None:
        if isinstance(category_id, bool) or not isinstance(category_id, int):
            raise ValueError("The category ID must be an integer or empty.")

    return details


async def create_task_flow(session, client, model, user_message):
    """Extract, preview, confirm, and then create a task."""
    tools_result = await session.list_tools()

    create_tool = next(
        (tool for tool in tools_result.tools if tool.name == "create_task"),
        None,
    )

    if create_tool is None:
        print("The create_task tool is not available.")
        return

    tool_schema = {
        "type": "function",
        "function": {
            "name": create_tool.name,
            "description": create_tool.description or create_tool.name,
            "parameters": create_tool.input_schema,
        },
    }

    try:
        extracted = extract_task_details(
            client,
            model,
            user_message,
            tool_schema,
        )

        task = validate_task_details(
            extracted,
            create_tool.input_schema,
        )

        relative_due_date = extract_relative_due_date(user_message)

        if relative_due_date:
            task["due_date"] = relative_due_date
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"\nCould not prepare the task: {exc}")
        return

    print("\nTASK PREVIEW")
    print("------------")
    print("Title:", task["title"])
    print("Description:", task["description"] or "None")
    print("Priority:", task["priority"])
    print("Due date:", task["due_date"] or "No due date")
    print("Status:", task["status"])
    category_id = task.get("category_id")
    print("Category ID:", category_id if category_id is not None else "None")
    print("Recurrence:", task["recurrence"])

    confirmation = input(
        "\nType YES to create this task, or NO to cancel: "
    ).strip().casefold()

    if confirmation != "yes":
        print("Task creation cancelled. Nothing was sent to the API.")
        return

    result = await session.call_tool("create_task", task)
    result_text = get_tool_text(result)

    print("\nTASK CREATION RESULT")
    print("--------------------")

    if result.is_error or result_text.lstrip().startswith("Error:"):
        print("Task creation failed:")
        print(result_text)
    else:
        print("Task creation completed:")
        print(result_text)
