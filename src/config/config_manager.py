import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from typing import Dict, List, Optional

from src.utils.logging_config import setup_logger

logger = setup_logger(__name__, logging.INFO)


@dataclass
class MCPServerConfig:
    command: str
    args: List[str]

    def to_dict(self) -> dict[str, str | list[str]]:
        return {"command": self.command, "args": self.args}


@dataclass
class MCPConfig:
    mcpServers: Dict[str, MCPServerConfig] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "MCPConfig":
        servers = {
            name: MCPServerConfig(**spec)
            for name, spec in data.get("mcpServers", {}).items()
        }
        return cls(mcpServers=servers)

    def get_server(self, name: str) -> MCPServerConfig:
        return self.mcpServers[name]

    def list_servers(self) -> List[str]:
        return list(self.mcpServers.keys())


class RunnerType(Enum):
    """Supported runner types"""

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
    max_global_children: int
    default_timeout_seconds: int


class ConfigManager:
    def __init__(self) -> None:
        """Initialize configuration manager and load config immediately"""
        self._agent_configs: Dict[str, AgentRuntime] = {}
        self._runtime: Optional[RuntimeConfig] = None
        self._mcp_config: Optional[MCPConfig] = None
        self._load_config()

    @property
    def agents(self) -> Dict[str, AgentRuntime]:
        """Get all agent configurations"""
        return self._agent_configs.copy()

    @property
    def runtime(self) -> Optional[RuntimeConfig]:
        """Get runtime configuration"""
        return self._runtime

    def get_main_agent(self) -> Optional[AgentRuntime]:
        """Get the main agent configuration"""
        for agent in self._agent_configs.values():
            if agent.is_main:
                return agent
        return None

    def get_agent(self, name: str) -> Optional[AgentRuntime]:
        """Get an agent's configuration"""
        return self._agent_configs.get(name)

    def get_mcp_config(self) -> Optional[MCPConfig]:
        """Get MCP configuration"""
        return self._mcp_config

    def _load_config(self) -> None:
        """Load configuration from the config file"""
        try:
            from src.config.config_handler import get_config

            config_data = get_config()

            if config_data["mcpServers"] != None:
                self._mcp_config = MCPConfig.from_dict(config_data)

            # Load agent configurations from runners array
            runners_raw = config_data.get("runners", [])
            if not isinstance(runners_raw, list):
                logger.error("'runners' configuration must be a list")
                return

            self._agent_configs = {}
            for i, runner_raw in enumerate(runners_raw):
                if not isinstance(runner_raw, dict):
                    logger.warning(f"Skipping runner {i}: not a dictionary")
                    continue

                if "type" not in runner_raw or "isMain" not in runner_raw:
                    logger.warning(f"Skipping runner {i}: missing required fields")
                    continue

                # Validate runner type
                runner_str = str(runner_raw["type"])
                try:
                    runner_type = RunnerType(runner_str)
                except ValueError:
                    logger.error(
                        f"Invalid runner type '{runner_str}' for runner {i}. Must be one of: {[r.value for r in RunnerType]}"
                    )
                    continue

                name = f"{runner_str}"  # Generate a unique name

                # Type-safe extraction of configuration values
                is_main = bool(runner_raw["isMain"])
                tools_raw = runner_raw.get("tools", [])
                tools = [str(t) for t in tools_raw] if isinstance(tools_raw, list) else []
                api_key = str(runner_raw.get("apiKey")) if runner_raw.get("apiKey") is not None else None
                model = str(runner_raw.get("model", "gemini-pro"))

                runtime = AgentRuntime(
                    runner=runner_type,
                    is_main=is_main,
                    tools=tools,
                    api_key=api_key,
                    model=model,
                )
                self._agent_configs[name] = runtime

            # Load runtime config if present
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

            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise  # Re-raise the exception as we don't want to silently use defaults


@lru_cache(maxsize=1)
def get_config_manager() -> ConfigManager:
    """Get the singleton instance of ConfigManager"""
    return ConfigManager()
