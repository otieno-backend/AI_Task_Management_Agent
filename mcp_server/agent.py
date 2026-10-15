import ast
import anyio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


server_path = Path(__file__).with_name("server.py")

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(server_path)],
)


def choose_tool(user_message: str) -> str:
    """Choose an MCP tool using simple local rules."""
    message = user_message.lower()

    if "overdue" in message:
        return "find_overdue_tasks"
    if "today" in message:
        return "get_today_tasks"
    if "summary" in message:
        return "get_task_summary"
    if "next" in message:
        return "get_next_tasks"
    if "show me my tasks" in message or "list my tasks" in message:
        return "list_tasks"

    return "list_tasks"


def choose_tools(user_message: str) -> list[str]:
    """Choose one or more MCP tools using simple local rules."""
    message = user_message.lower()
    tools = []

    if "overdue" in message:
        tools.append("find_overdue_tasks")

    if "today" in message:
        tools.append("get_today_tasks")

    if not tools:
        tools.append(choose_tool(user_message))

    return tools


def format_task_list(raw_result: str) -> str:
    """Turn a list_tasks result into a readable response."""
    try:
        data = ast.literal_eval(raw_result)
    except (ValueError, SyntaxError):
        return f"I received a result, but couldn't format it:\n{raw_result}"

    tasks = data.get("results", [])

    if not tasks:
        return "You don't have any tasks."

    lines = [f"You have {data.get('count', len(tasks))} tasks:"]

    for task in tasks:
        title = task.get("title", "Untitled task")
        status = task.get("status", "UNKNOWN")
        priority = task.get("priority", "UNKNOWN")
        lines.append(f"- {title} | Status: {status} | Priority: {priority}")

    return "\n".join(lines)


async def run_agent(user_message: str):
    print(f"\nYou: {user_message}")

    selected_tool = choose_tool(user_message)
    print(f"Agent selected tool: {selected_tool}")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_tools()
            available_tools = [tool.name for tool in result.tools]

            if selected_tool not in available_tools:
                print("Agent: The requested tool is unavailable.")
                return

            response = await session.call_tool(selected_tool, {})

            if response.is_error:
                print("Agent: Sorry, the task request failed.")
                return

            if not response.content:
                print("Agent: The tool returned no information.")
                return

            raw_result = response.content[0].text

            if selected_tool == "list_tasks":
                answer = format_task_list(raw_result)
            else:
                answer = raw_result

            print(f"\nAgent:\n{answer}")


if __name__ == "__main__":
    message = input("What would you like to do? ")
    anyio.run(run_agent, message)
