import anyio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main():
    server_path = Path(__file__).with_name("server.py")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-u", str(server_path)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_tools()

            print("NUMBER OF TOOLS:", len(result.tools))
            print()

            print("Calling get_task_summary...")
            response = await session.call_tool("get_task_summary", {})

            print()
            print("RESULT:")
            print(response)


if __name__ == "__main__":
    anyio.run(main)
