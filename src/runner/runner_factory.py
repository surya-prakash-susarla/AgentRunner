import os
from typing import Optional

from src.config.config_manager import RunnerType, get_config_manager
from src.process.agent_process_input import AgentProcessInput
from src.runner.agent_runner import AgentRunner
from src.runner.gemini_runner import GeminiRunner
from src.tools.mcp_master import get_mcp_master


def create_runner(input_config: AgentProcessInput) -> Optional[AgentRunner]:
    """Create an agent runner based on configuration.

    Args:
        input_config: Configuration for the agent process containing:
            - type
            - instruction
            - tool names
            - other runner-specific settings

    Returns:
        A configured AgentRunner instance, or None if creation fails.

    """
    # Set up runtime environment first
    if not isinstance(input_config.child_type, str):
        runtime = get_config_manager().agents[input_config.child_type.value]
    else:
        runtime = get_config_manager().agents[input_config.child_type]
    runner = None

    if input_config.child_type == RunnerType.GEMINI.value:
        os.environ["GOOGLE_API_KEY"] = runtime.api_key
        runner = GeminiRunner(instruction=input_config.instruction)

        # Configure MCP tools if any are specified
        if input_config.tool_names:
            mcp_master = get_mcp_master()
            mcp_client = mcp_master.create_client_for_tools(input_config.tool_names)
            runner.configureMcp(mcp_client)

    return runner
