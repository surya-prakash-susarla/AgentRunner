from src.config.config_manager import get_config_manager
import functools
import logging
from src.utils.logging_config import setup_logger
from src.config.config_manager import MCPConfig
from fastmcp import Client
import asyncio

logger = setup_logger(__name__, logging.INFO)


class McpMaster:
    def __init__(self, mcp_config: MCPConfig):
        self._mcp_config = mcp_config
        self._tool_mapping = dict()
        self._create_tool_mapping()

    def _create_tool_mapping(self):
        logger.info("Creating tool mapping")

        for server_name in self._mcp_config.list_servers():
            logger.info(
                "Creating tool mapping for server: {server}".format(server=server_name)
            )
            server_config = self._generate_mcp_config_from_subconfig(server_name)
            logger.info(
                "Generated server config: {config}".format(config=server_config)
            )
            temporary_event_loop = asyncio.new_event_loop()
            temporary_event_loop.run_until_complete
            tools = asyncio.run(self._get_tool_names(server_config))
            for tool in tools:
                self._tool_mapping[tool] = server_name

        logger.info(
            "All tools mapped, final mapping: {tool_mapping}".format(
                tool_mapping=self._tool_mapping
            )
        )

    async def _get_tool_names(self, server_config) -> list[str]:
        async with Client(server_config) as client:
            tools = await client.list_tools()
            return [x.name for x in tools]

    def _generate_mcp_config_from_subconfig(self, server_name: str):
        return {
            "mcpServers": {
                server_name: get_config_manager()
                .get_mcp_config()
                .get_server(server_name)
                .to_dict()
            }
        }

    def get_server_for_tool(self, tool_name: str) -> str | None:
        pass

    def create_client_for_server(self, server_name: str):
        pass


@functools.lru_cache(maxsize=1)
def get_mcp_master() -> McpMaster:
    mcp_master = McpMaster(get_config_manager().get_mcp_config())
    logger.info(
        "MCP config loaded: {config}".format(
            config=get_config_manager().get_mcp_config()
        )
    )
    return mcp_master
