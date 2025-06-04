import logging
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from typing import Dict, List, Optional

from src.utils.logging_config import setup_logger

logger = setup_logger(__name__, logging.INFO)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server with command and arguments."""

    command: str
    args: List[str]

    def to_dict(self) -> dict[str, str | list[str]]:
        """Convert the configuration to a dictionary.

        Returns:
            A dictionary with command and args keys.

        """
        return {"command": self.command, "args": self.args}


@dataclass
class MCPConfig:
    """Configuration for MCP (Model Context Protocol) servers.

    This class stores and manages the configuration for MCP servers, including
    their command-line arguments and other settings.

    Args:
        mcp_servers: Dictionary mapping server names to their configurations.

    """

    mcp_servers: Dict[str, MCPServerConfig] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "MCPConfig":
        """Create an MCPConfig instance from a dictionary.

        Args:
            data: Dictionary containing MCP server configurations.

        Returns:
            A new MCPConfig instance.

        """
        servers = {
            name: MCPServerConfig(**spec)
            for name, spec in data.get("mcpServers", {}).items()
        }
        return cls(mcp_servers=servers)

    def get_server(self, name: str) -> MCPServerConfig:
        """Get configuration for a specific server.

        Args:
            name: Name of the server to retrieve.

        Returns:
            Configuration for the specified server.

        """
        return self.mcp_servers[name]

    def list_servers(self) -> List[str]:
        """Get a list of all configured server names.

        Returns:
            List of server names in the configuration.

        """
        return list(self.mcp_servers.keys())


class RunnerType(Enum):
    """Supported runner types for agents.

    Defines the valid types of runners that can be used to execute agents.
    """

    GEMINI = "gemini"


@dataclass
class AgentRuntime:
    """Runtime configuration for an agent."""

    runner: RunnerType
    is_main: bool
    api_key: Optional[str] = None
    model: str = "gemini-pro"
    tools: List[str] = field(default_factory=list)


@dataclass
class RuntimeConfig:
    """Configuration for runtime behavior.

    Holds configuration values that control the runtime behavior of the system,
    such as process limits and timeouts.

    Args:
        max_global_children: Maximum number of child processes allowed.
        default_timeout_seconds: Default timeout for operations in seconds.

    """

    max_global_children: int
    default_timeout_seconds: int


class ConfigManager:
    """Manager for loading and accessing configuration for runners and MCP servers."""

    def __init__(self) -> None:
        """Initialize configuration manager and load config immediately."""
        self._agent_configs: Dict[str, AgentRuntime] = {}
        self._runtime: Optional[RuntimeConfig] = None
        self._mcp_config: Optional[MCPConfig] = None
        self._load_config()

    @property
    def agents(self) -> Dict[str, AgentRuntime]:
        """Get all agent configurations."""
        return self._agent_configs.copy()

    @property
    def runtime(self) -> Optional[RuntimeConfig]:
        """Get runtime configuration."""
        return self._runtime

    def get_main_agent(self) -> Optional[AgentRuntime]:
        """Get the main agent configuration."""
        for agent in self._agent_configs.values():
            if agent.is_main:
                return agent
        return None

    def get_agent(self, name: str) -> Optional[AgentRuntime]:
        """Get an agent's configuration."""
        return self._agent_configs.get(name)

    def get_mcp_config(self) -> Optional[MCPConfig]:
        """Get MCP configuration."""
        return self._mcp_config

    def _load_config(self) -> None:
        """Load configuration from the config file."""
        try:
            from src.config.config_handler import get_config

            config_data = get_config()

            # Load MCP configuration
            self._load_mcp_config(config_data)

            # Load agent configurations from runners array
            runners_raw = config_data.get("runners", [])
            if not isinstance(runners_raw, list):
                logger.error("'runners' configuration must be a list")
                return

            # Process each runner configuration
            self._agent_configs = {}
            for i, runner_raw in enumerate(runners_raw):
                result = self._process_runner_config(runner_raw, i)
                if result:
                    name, runtime = result
                    self._agent_configs[name] = runtime

            # Load runtime configuration
            self._load_runtime_config(config_data)

            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise  # Re-raise as we don't want to silently use defaults

    def _load_mcp_config(self, config_data: dict) -> None:
        """Load MCP server configuration from config data.

        Args:
            config_data: Raw configuration dictionary.

        """
        if config_data.get("mcpServers") is not None:
            self._mcp_config = MCPConfig.from_dict(config_data)

    def _load_runtime_config(self, config_data: dict) -> None:
        """Load runtime configuration from config data.

        Args:
            config_data: Raw configuration dictionary.

        """
        runtime_raw = config_data.get("runtime")
        if runtime_raw is not None and isinstance(runtime_raw, dict):
            max_children_raw = runtime_raw.get("maxGlobalChildren")
            timeout_raw = runtime_raw.get("defaultTimeoutSeconds")

            if max_children_raw is not None and timeout_raw is not None:
                try:
                    max_children = int(max_children_raw)
                    timeout = int(timeout_raw)
                    self._runtime = RuntimeConfig(
                        max_global_children=max_children,
                        default_timeout_seconds=timeout,
                    )
                except (ValueError, TypeError):
                    logger.error("Runtime configuration values must be integers")

    def _validate_runner_type(
        self, runner_str: str, index: int
    ) -> Optional[RunnerType]:
        """Validate and convert runner type string to enum.

        Args:
            runner_str: The runner type string from config.
            index: Index of the runner in config for error reporting.

        Returns:
            RunnerType if valid, None otherwise.

        """
        try:
            return RunnerType(runner_str)
        except ValueError:
            logger.error(
                f"Invalid runner type '{runner_str}' for runner {index}. "
                f"Must be one of: {[r.value for r in RunnerType]}"
            )
            return None

    def _process_runner_config(
        self, runner_raw: dict, index: int
    ) -> Optional[tuple[str, AgentRuntime]]:
        """Process a single runner configuration entry.

        Args:
            runner_raw: Raw runner configuration dictionary.
            index: Index of the runner in config for error reporting.

        Returns:
            Tuple of (name, AgentRuntime) if valid, None otherwise.

        """

        if not isinstance(runner_raw, dict):
            logger.warning(f"Skipping runner {index}: not a dictionary")
            return None

        if "type" not in runner_raw or "isMain" not in runner_raw:
            logger.warning(f"Skipping runner {index}: missing required fields")
            return None

        runner_str = str(runner_raw["type"])
        runner_type = self._validate_runner_type(runner_str, index)
        if runner_type is None:
            return None

        name = f"{runner_str}"
        is_main = bool(runner_raw["isMain"])
        tools_raw = runner_raw.get("tools", [])
        tools = [str(t) for t in tools_raw] if isinstance(tools_raw, list) else []

        return name, AgentRuntime(runner=runner_type, is_main=is_main, tools=tools, api_key=runner_raw["apiKey"], model=runner_raw["model"])


@lru_cache(maxsize=1)
def get_config_manager() -> ConfigManager:
    """Get the singleton instance of ConfigManager.

    Returns:
        The singleton ConfigManager instance.

    """
    return ConfigManager()
