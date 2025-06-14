import asyncio
import functools
import logging
from typing import Dict, List

from fastmcp import Client

from src.config.config_manager import MCPConfig, get_config_manager
from src.process.exceptions import UnknownToolError
from src.utils.logging_config import setup_logger

logger = setup_logger(__name__, logging.INFO)


class McpMaster:
    """Master controller for MCP tool servers and tool mapping.

    Manages the mapping between tools and their MCP servers, enabling dynamic tool
    discovery and server configuration.
    """

    def __init__(self, mcp_config: MCPConfig | None):
        """Initialize the MCP master controller.

        Args:
            mcp_config: Configuration object containing MCP server specs.

        Raises:
            ValueError: If mcp_config is None.

        """
        if mcp_config is None:
            raise ValueError("MCP configuration cannot be None")
        self._mcp_config = mcp_config
        self._tool_mapping: Dict[str, str] = {}  # Maps tool names to server names
        self._create_tool_mapping()

    def _create_tool_mapping(self) -> None:
        """Create the internal mapping of tools to their respective servers.

        Queries each configured MCP server to discover its available tools
        and builds a mapping for future lookups.
        """
        logger.info("Creating tool mapping")

        for server_name in self._mcp_config.list_servers():
            logger.info(f"Creating tool mapping for server: {server_name}")
            server_config = self._generate_mcp_config_from_subconfig(server_name)
            logger.info(f"Generated server config: {server_config}")
            tools = asyncio.run(self._get_tool_names(server_config))
            for tool in tools:
                self._tool_mapping[tool] = server_name

        logger.info(f"All tools mapped, final mapping: {self._tool_mapping}")

    async def _get_tool_names(self, server_config: Dict) -> list[str]:
        """Get list of tool names available from an MCP server.

        Args:
            server_config: MCP server configuration dictionary.

        Returns:
            List of tool names available on the server.

        """
        async with Client(server_config) as client:
            tools = await client.list_tools()
            return [x.name for x in tools]

    def _generate_mcp_config_from_subconfig(self, server_name: str) -> Dict:
        """Generate an MCP configuration for a specific server.

        Args:
            server_name: Name of the server to generate config for.

        Returns:
            Dictionary containing the MCP server configuration.

        Raises:
            ValueError: If MCP config not found for the server.

        """
        mcp_config = get_config_manager().get_mcp_config()
        if mcp_config is None:
            raise ValueError(f"MCP config not found for server {server_name}")

        return {
            "mcpServers": {server_name: mcp_config.get_server(server_name).to_dict()}
        }

    def get_available_tools(self) -> List[str]:
        """Get all available tool names across MCP servers.

        Returns:
            List of all known tool names that can be used with MCP clients.

        """
        return list(self._tool_mapping.keys())

    def _get_server_for_tool(self, tool_name: str) -> str | None:
        """Get the server name that provides the specified tool.

        Args:
            tool_name: Name of the tool to look up

        Returns:
            Server name if the tool exists, None otherwise

        """
        return (
            self._tool_mapping[tool_name] if tool_name in self._tool_mapping else None
        )

    def _get_server_collection_for_tools(self, tools: list[str]) -> set[str]:
        """Get the set of server names required for the given tools.

        Args:
            tools: List of tool names to find servers for

        Returns:
            Set of server names that collectively provide all the requested tools

        Raises:
            UnknownToolError: If any tool name is not found in the tool mapping

        """
        required_servers = set()
        for tool in tools:
            server = self._get_server_for_tool(tool)
            if server is None:
                raise UnknownToolError(tool)
            required_servers.add(server)

        logger.info(f"Required servers for tools {tools}: {required_servers}")
        return required_servers

    def create_client_for_tools(self, tools: list[str]) -> Client:
        """Create an MCP client that has access to all the requested tools.

        This method will:
        1. Find all servers needed for the requested tools
        2. Generate a combined MCP configuration including all required servers
        3. Create and return a client with access to all tools

        Args:
            tools: List of tool names that the client needs access to

        Returns:
            MCP Client configured with all required servers

        Raises:
            UnknownToolError: If any requested tool is not available

        """
        # Get all required servers for these tools
        servers = self._get_server_collection_for_tools(tools)

        logger.info("Creating client for tools: {tools}".format(tools=tools))
        logger.info("Required servers: {servers}".format(servers=servers))

        # Create a combined configuration with all required servers
        combined_config: dict[str, dict] = {"mcpServers": {}}
        for server_name in servers:
            server_config = self._mcp_config.get_server(server_name).to_dict()
            combined_config["mcpServers"][server_name] = server_config

        logger.info("Created combined config: {config}".format(config=combined_config))

        # Create and return a client with the combined configuration
        return Client(combined_config)


@functools.lru_cache(maxsize=1)
def get_mcp_master() -> McpMaster:
    """Get or create the singleton instance of McpMaster.

    Returns:
        Singleton instance of McpMaster with loaded configuration

    Note:
        This function is cached, so subsequent calls will return the same instance

    """
    mcp_master = McpMaster(get_config_manager().get_mcp_config())
    logger.info(
        "MCP config loaded: {config}".format(
            config=get_config_manager().get_mcp_config()
        )
    )
    return mcp_master
