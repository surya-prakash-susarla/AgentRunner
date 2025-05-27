from google.genai import types


async def generateToolsConfig(mcp_client):
    async with mcp_client:
        list_tools_result = await mcp_client.list_tools()
        tools = [
            types.Tool(
                function_declarations=[
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            k: v
                            for k, v in tool.inputSchema.items()
                            if k not in ["additionalProperties", "$schema"]
                        },
                    }
                ]
            )
            for tool in list_tools_result
        ]
        return tools
