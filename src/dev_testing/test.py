import asyncio

from fastmcp import Client


async def test() -> None:
    """Run a test configuration of the MCP server setup.

    Creates a basic MCP server configuration and tests the connection
    by calling an echo tool.
    """
    config = {
        "mcpServers": {
            "everything": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-everything"],
            }
        }
    }

    async with Client(config) as client:
        tools = await client.list_tools()
        print("TOOlS: {tools}".format(tools=tools))


asyncio.run(test())
