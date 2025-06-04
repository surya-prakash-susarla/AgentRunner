from fastmcp import FastMCP

echo_mcp_server: FastMCP = FastMCP("Echo")


@echo_mcp_server.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message back as a resource response.

    Args:
        message: The message to echo back.

    Returns:

        The echoed message with a resource prefix.
    """
    return f"Resource echo: {message}"


@echo_mcp_server.tool()
def echo_tool(message: str) -> str:
    """Echo a message back as a tool response.

    Args:
        message: The message to echo back.

    Returns:

        The echoed message with a tool prefix.
    """
    return f"Tool echo: {message}"


@echo_mcp_server.prompt()
def echo_prompt(message: str) -> str:
    """Create a formatted echo prompt message.

    Args:
        message: The message to include in the prompt.

    Returns:

        A formatted prompt message.
    """
    return f"Please process this message: {message}"
