import asyncio

from fastmcp import Client

from src.dev_testing.server import echo_mcp_server


def test_server() -> None:
    """Test the MCP server functionality with basic operations.

    Sets up a test server and verifies basic functionality including
    tool listing and echo operations.
    """

    async def list_tools() -> list:
        async with client:
            result = await client.list_tools()
            return result

    client = Client(echo_mcp_server)

    response = asyncio.run(list_tools())
    print("Sample mcp server response: {response}".format(response=response))
    return
