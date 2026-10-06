from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Task Management Server")


@mcp.tool()
def hello_task_manager() -> str:
    """A simple test tool for the Task Management MCP server."""
    return "Hello! The Task Management MCP server is working."


if __name__ == "__main__":
    mcp.run()
