import anyio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from task_creation import create_task_flow

load_dotenv(Path(__file__).resolve().parent / ".env")


async def main():
    client = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key="ollama",
    )

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path("mcp_server/server.py").resolve())],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            await create_task_flow(
                session,
                client,
                os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
                "Create a HIGH priority task called "
                "'Test AI task creation' with a due date of tomorrow."
            )


if __name__ == "__main__":
    anyio.run(main)
