import anyio
import sys

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "list_tasks",
                {},
            )

            print("Task result:")
            print(result)


if __name__ == "__main__":
    anyio.run(main)
