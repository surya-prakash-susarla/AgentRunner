import re
from dataclasses import dataclass
from typing import List

from src.config.config_manager import RunnerType, get_config_manager
from src.process.exceptions import ChildAgentOperationError


@dataclass
class AgentProcessInput:
    name: str
    instruction: str
    child_type: RunnerType
    tool_names: List[str]

    def __post_init__(self) -> None:
        """Validate all input parameters during initialization."""
        errors = []

        # Validate name
        if not self.name:
            errors.append("Agent name cannot be empty")
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.name):
            errors.append(
                "Agent name can only contain letters, numbers, underscores, and hyphens"
            )

        # Validate instruction
        if not self.instruction or not self.instruction.strip():
            errors.append("Instruction cannot be empty")

        # Validate child_type against config
        config_manager = get_config_manager()
        if self.child_type not in config_manager.agents:
            errors.append(
                f"Invalid runner type '{self.child_type}'. Must be one of: {list(config_manager.agents.keys())}"
            )

        # Validate tool_names against MCP master's available tools
        if self.tool_names:
            from src.tools.mcp_master import get_mcp_master

            mcp_master = get_mcp_master()
            available_tools = mcp_master.get_available_tools()

            # Collect all missing tools
            missing_tools = [
                tool for tool in self.tool_names if tool not in available_tools
            ]
            if missing_tools:
                errors.append(
                    f"The following tools are not available in any MCP server: {missing_tools}\n"
                    f"Available tools: {available_tools}"
                )

        if errors:
            raise ChildAgentOperationError(
                name=self.name,
                operation="initialization",
                error="Invalid agent configuration:\n- " + "\n- ".join(errors),
            )
