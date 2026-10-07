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


async def main():
    print("AI Task Management Agent")
    print()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            all_tools = []
            cursor = None

            while True:
                if cursor:
                    result = await session.list_tools(
                        params={"cursor": cursor}
                    )
                else:
                    result = await session.list_tools()

                all_tools.extend(result.tools)

                cursor = result.next_cursor

                if not cursor:
                    break

            print("Tools available to the AI agent:")
            print()

            for tool in all_tools:
                print(f"Tool: {tool.name}")
                print(f"Description: {tool.description}")
                print()


if __name__ == "__main__":
    anyio.run(main)
