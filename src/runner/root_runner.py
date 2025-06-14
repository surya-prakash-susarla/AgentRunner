import asyncio
from typing import Optional

from fastmcp import Client, FastMCP

from src.config.config_manager import RunnerType, get_config_manager
from src.dev_testing.server import echo_mcp_server
from src.process.agent_process_input import AgentProcessInput
from src.runner.agent_runner import AgentRunner
from src.runner.runner_factory import create_runner
from src.tools.mcp_master import get_mcp_master
from src.tools.replicator_tools import replicator_tools_server


def create_root_runner() -> Optional[AgentRunner]:
    """Create the root/main agent runner based on configuration.

    This method:
    1. Finds the agent marked as main in the config
    2. Creates and configures a runner for that agent type
    3. Sets up its MCP tools and runtime environment

    Returns:
        An AgentRunner instance configured as the main agent, or None if creation fails

    Raises:
        Exception: If no main agent is configured or if config is invalid

    """
    config_manager = get_config_manager()
    main_agent = None
    main_type: RunnerType | None = None

    # Find the agent marked as main in config
    for agent_type, runtime in config_manager.agents.items():
        if runtime.is_main:
            main_agent = runtime
            if isinstance(agent_type, str):
                main_type = RunnerType(agent_type)
            else:
                main_type = agent_type
            break

    if not main_agent or not main_type:
        msg = "No main agent configured. Please mark one agent as 'isMain: true'"
        raise Exception(msg)

    # Create input config for the main agent
    meta_instruction = """
        You are the orchestrator agent in charge of managing specialized child agents.
        Your role is to chat naturally with the user, delegate tasks to child agents
        using available tools when appropriate, and manage their lifecycle if needed.

        Tool Management and Distribution:
        - You have access to ALL available tools in the system
        - When creating child agents, analyze which tools they need for their purpose
        - Distribute tools thoughtfully - give agents only what they need
        - Consider these tool distribution principles:
            * Task-specific tools: Give agents only tools for their domain
            * Security: Avoid giving sensitive system tools to task-specific agents
            * Efficiency: Don't overload agents with unnecessary tools
        - Track which tools you've given to which agents for coordination

        Agent Management:
        - Create child agents dynamically as needed
        - When creating an agent, specify instruction and required tool_names
        - Route follow-up questions to relevant child agents
        - Summarize child agent responses before replying
        - Proactively call tools and relay responses when appropriate

        Tools and Capabilities:
        - Review available tools to understand what capabilities you can grant
        - Consider tool dependencies for complex tasks
        - You can adjust tool access for agents as needs change

        Always behave as an intelligent, proactive assistant. Only pause for
        confirmation when ambiguity exists or user intent is unclear.
    """

    # For root agent, always give access to all available tools
    mcp_master = get_mcp_master()
    all_tools = mcp_master.get_available_tools()

    input_config = AgentProcessInput(
        name="main",
        instruction=meta_instruction,
        child_type=main_type,
        tool_names=all_tools,
    )

    root_runner = create_runner(input_config)
    if root_runner is None:
        raise Exception("Failed to create root runner")

    mcp_client = root_runner.get_mcp_client()
    if mcp_client is None:
        raise Exception("Root runner MCP client not configured")

    replicator_enabled_client = _get_client_with_replicator_tools(mcp_client)
    root_runner.configure_mcp(replicator_enabled_client)

    return root_runner


def _get_client_with_replicator_tools(client: Client) -> Client:
    """Add replicator tools to an existing MCP client.

    This ensures the client has access to tools needed for agent replication and
    management.

    Args:
        client: The existing MCP client to enhance

    Returns:
        A new client that has both the original tools and replicator tools

    """
    # Create a new server instance for the enhanced client
    tool_server: FastMCP = FastMCP("enhanced_server")

    all_tool_proxy = FastMCP.as_proxy(client)

    # Add the replicator and echo tools
    asyncio.run(tool_server.import_server("all_tools", all_tool_proxy))
    asyncio.run(tool_server.import_server("replicator_tools", replicator_tools_server))
    asyncio.run(tool_server.import_server("echo_tools", echo_mcp_server))

    return Client(tool_server)
