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
    tools: List[str] = field(default_factory=list)


@dataclass
class RuntimeConfig:
    max_global_children: int
    default_timeout_seconds: int


class ConfigManager:
    def __init__(self):
        """Initialize configuration manager and load config immediately"""
        self._agent_configs: Dict[str, AgentRuntime] = {}
        self._runtime: Optional[RuntimeConfig] = None
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

    def _load_config(self):
        """Load configuration from the config file"""
        try:
            from src.config.config_handler import get_config

            config_data = get_config()

            # Load agent configurations from runners array
            runners_data = config_data.get("runners", [])
            self._agent_configs = {}
            for i, runner_data in enumerate(runners_data):
                if "type" not in runner_data or "isMain" not in runner_data:
                    logger.warning(f"Skipping runner {i}: missing required fields")
                    continue

                # Validate runner type
                runner_str = runner_data["type"]
                try:
                    runner_type = RunnerType(runner_str)
                except ValueError:
                    logger.error(
                        f"Invalid runner type '{runner_str}' for runner {i}. Must be one of: {[r.value for r in RunnerType]}"
                    )
                    continue

                name = f"{runner_str}"  # Generate a unique name
                runtime = AgentRuntime(
                    runner=runner_type,
                    is_main=runner_data["isMain"],
                    tools=runner_data.get("tools", []),
                    api_key=runner_data.get("apiKey"),
                    model=runner_data.get("model"),
                )
                self._agent_configs[name] = runtime

            # Load runtime config if present
            runtime_data = config_data.get("runtime")
            if (
                runtime_data
                and "maxGlobalChildren" in runtime_data
                and "defaultTimeoutSeconds" in runtime_data
            ):
                self._runtime = RuntimeConfig(
                    max_global_children=runtime_data["maxGlobalChildren"],
                    default_timeout_seconds=runtime_data["defaultTimeoutSeconds"],
                )

            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise  # Re-raise the exception as we don't want to silently use defaults


@lru_cache(maxsize=1)
def get_config_manager() -> ConfigManager:
    """Get the singleton instance of ConfigManager"""
    return ConfigManager()
