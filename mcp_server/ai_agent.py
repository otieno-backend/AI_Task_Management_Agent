"""OpenAI-powered, read-only task management agent."""

import json
import os
import sys
from pathlib import Path

import anyio
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
SERVER_PATH = BASE_DIR / "server.py"

# Only allow tools that read task information.
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
You are an AI task management assistant.

Help the user understand and plan their actual tasks.
Use the available read-only tools when current task data is needed.
Base recommendations on the returned data. Never invent tasks,
due dates, priorities, or task statistics.

Explain why you recommend a task, especially when it is overdue,
due soon, or high priority. If information is missing, say so.

You must not claim to have created, updated, or completed a task.
You have read-only access and cannot make changes.
Keep your response practical, clear, and organized.
"""


def build_openai_tools(mcp_tools):
    """Convert permitted MCP tool definitions to OpenAI tool schemas."""
    tools = []

    for tool in mcp_tools:
        if tool.name not in READ_ONLY_TOOLS:
            continue

        tools.append(
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description or tool.name,
                "parameters": tool.inputSchema,
                "strict": False,
            }
        )

    return tools


def get_function_calls(response):
    """Extract function calls from an OpenAI Responses API result."""
    return [
        item
        for item in response.output
        if item.type == "function_call"
    ]


def get_text_result(result):
    """Combine text returned by an MCP tool."""
    if result.isError:
        return "The task tool reported an error."

    parts = [
        item.text
        for item in (result.content or [])
        if hasattr(item, "text")
    ]

    return "\n".join(parts) if parts else "The tool returned no text."


async def run_agent(user_message: str):
    """Ask OpenAI to reason over data obtained through read-only MCP tools."""
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is missing from mcp_server/.env.")
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )

    try:
        client = OpenAI()

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tool_result = await session.list_tools()
                openai_tools = build_openai_tools(tool_result.tools)

                if not openai_tools:
                    print("No permitted read-only MCP tools are available.")
                    return

                conversation = [
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ]

                for _ in range(6):
                    response = client.responses.create(
                        model=MODEL,
                        instructions=SYSTEM_INSTRUCTIONS,
                        input=conversation,
                        tools=openai_tools,
                        tool_choice="auto",
                    )

                    calls = get_function_calls(response)

                    if not calls:
                        print("\nAI Task Manager:\n")
                        print(
                            response.output_text
                            or "The AI did not return a text response."
                        )
                        return

                    # Preserve the model's response before adding tool results.
                    conversation.extend(response.output)

                    for call in calls:
                        if call.name not in READ_ONLY_TOOLS:
                            output = "This tool is not permitted."
                        else:
                            try:
                                arguments = json.loads(call.arguments or "{}")
                                result = await session.call_tool(
                                    call.name,
                                    arguments,
                                )
                                output = get_text_result(result)
                            except (ValueError, TypeError) as exc:
                                output = f"Invalid tool arguments: {exc}"
                            except Exception:
                                output = (
                                    "The task tool failed. "
                                    "Please check the MCP server and API."
                                )

                        conversation.append(
                            {
                                "type": "function_call_output",
                                "call_id": call.call_id,
                                "output": output,
                            }
                        )

                print(
                    "The agent reached its tool-call limit. "
                    "Please try a more specific request."
                )

    except Exception as exc:
        # Avoid printing request details or credentials.
        print(
            f"Agent error ({type(exc).__name__}). "
            "Check API access, configuration, and server logs."
        )


if __name__ == "__main__":
    message = input(
        "What would you like help with? "
    ).strip()

    if message:
        anyio.run(run_agent, message)
    else:
        print("Please enter a question about your tasks.")
