from dev_testing.server import echo_mcp_server
from fastmcp import Client
import asyncio


def test_server() -> None:
    async def list_tools():
        async with client:
            result = await client.list_tools()
            return result

    client = Client(echo_mcp_server)

    response = asyncio.run(list_tools())
    print("Sample mcp server response: {response}".format(response=response))
    return
