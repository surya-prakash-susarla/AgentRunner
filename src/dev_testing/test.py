import asyncio

from fastmcp import Client


async def test():
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
