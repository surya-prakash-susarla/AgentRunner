from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional
import json
import os

from src.utils.logging_config import setup_logger
import logging

logger = setup_logger(__name__, logging.INFO)

from enum import Enum

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

@dataclass
class RuntimeConfig:
    max_global_children: int
    default_timeout_seconds: int

@dataclass
class ToolServerConfig:
    pass  # Will be expanded based on needs

@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    runtime: AgentRuntime
    tools: List[str] = field(default_factory=list)

class ConfigManager:
    def __init__(self):
        """Initialize configuration manager and load config immediately"""
        self._agent_configs: Dict[str, AgentConfig] = {}
        self._runtime: Optional[RuntimeConfig] = None
        self._tool_servers: Dict[str, ToolServerConfig] = {}
        self._load_config()

    @property
    def agents(self) -> Dict[str, AgentConfig]:
        """Get all agent configurations"""
        return self._agent_configs.copy()

    @property
    def runtime(self) -> Optional[RuntimeConfig]:
        """Get runtime configuration"""
        return self._runtime

    @property
    def tool_servers(self) -> Dict[str, ToolServerConfig]:
        """Get tool server configurations"""
        return self._tool_servers

    def get_main_agent(self) -> Optional[AgentConfig]:
        """Get the main agent configuration"""
        for agent in self._agent_configs.values():
            if agent.runtime.is_main:
                return agent
        return None

    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """Get an agent's configuration"""
        return self._agent_configs.get(name)

    def _load_config(self):
        """Load configuration from the config file"""
        try:
            from src.config.config_handler import get_config
            config_data = get_config()

            # Load agent configurations
            agents_data = config_data.get("agents", {})
            self._agent_configs = {}
            for name, agent_data in agents_data.items():
                if "runtime" not in agent_data:
                    logger.warning(f"Skipping agent {name}: missing runtime configuration")
                    continue
                
                runtime_data = agent_data["runtime"]
                if "runner" not in runtime_data or "isMain" not in runtime_data:
                    logger.warning(f"Skipping agent {name}: missing required runtime fields")
                    continue

                # Validate runner type
                runner_str = runtime_data["runner"]
                try:
                    runner_type = RunnerType(runner_str)
                except ValueError:
                    logger.error(f"Invalid runner type '{runner_str}' for agent {name}. Must be one of: {[r.value for r in RunnerType]}")
                    continue

                runtime = AgentRuntime(
                    runner=runner_type,
                    is_main=runtime_data["isMain"],
                    api_key=runtime_data.get("api_key"),
                    model=runtime_data.get("model")
                )
                self._agent_configs[name] = AgentConfig(
                    name=name,
                    runtime=runtime,
                    tools=agent_data.get("tools", [])
                )

            # Load runtime config if present
            runtime_data = config_data.get("runtime")
            if runtime_data and "maxGlobalChildren" in runtime_data and "defaultTimeoutSeconds" in runtime_data:
                self._runtime = RuntimeConfig(
                    max_global_children=runtime_data["maxGlobalChildren"],
                    default_timeout_seconds=runtime_data["defaultTimeoutSeconds"]
                )

            # Load tool servers if present
            self._tool_servers = {}  # Will be expanded when tool server config is defined
            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise  # Re-raise the exception as we don't want to silently use defaults

@lru_cache(maxsize=1)
def get_config_manager() -> ConfigManager:
    """Get the singleton instance of ConfigManager"""
    return ConfigManager()
