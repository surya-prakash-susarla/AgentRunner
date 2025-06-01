import os
import asyncio
from typing import Optional
from src.runner.gemini_runner import GeminiRunner
from src.runner.agent_runner import AgentRunner
from src.config.config_manager import RunnerType, get_config_manager
from src.process.agent_process_input import AgentProcessInput
from src.tools.mcp_master import get_mcp_master
from src.tools.replicator_tools import replicator_tools_server
from src.dev_testing.server import echo_mcp_server
from fastmcp import Client, FastMCP


def create_root_runner() -> Optional[AgentRunner]:
    """Create the root/main agent runner based on configuration.

    This method:
    1. Finds the agent marked as main in the config
    2. Creates and configures a runner for that agent type
    3. Sets up its MCP tools and runtime environment

    Returns:
        An instance of AgentRunner configured as the main agent, or None if creation fails

    Raises:
        Exception: If no main agent is configured or if the main agent's configuration is invalid
    """
    config_manager = get_config_manager()
    main_agent = None

    # Find the agent marked as main in config
    for agent_type, runtime in config_manager.agents.items():
        if runtime.is_main:
            main_agent = runtime
            main_type = agent_type
            break

    if not main_agent:
        raise Exception(
            "No main agent configured. Please mark one agent as 'isMain: true' in config"
        )

    # Create input config for the main agent
    meta_instruction = """
        You are the orchestrator agent in charge of managing specialized child agents. Your role is to chat naturally with the user, delegate tasks to child agents using available tools when appropriate, and manage their lifecycle if needed.

        You may:
        - Create child agents dynamically, choosing their names, types, and instructions if the user does not specify.
        - Route follow-up questions to relevant child agents based on their assigned roles.
        - Summarize or rephrase responses from child agents before replying to the user.
        - Proactively call tools and relay agent responses without waiting for user input when appropriate.

        Always behave as an intelligent, proactive assistant. Only pause for confirmation when ambiguity exists or user intent is unclear.
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
    replicator_enabled_client = _get_client_with_replicator_tools(
        root_runner.getMcpClient()
    )
    root_runner.configureMcp(replicator_enabled_client)

    return root_runner


def _get_client_with_replicator_tools(client: Client) -> Client:
    """Add replicator tools to an existing MCP client.
    
    This ensures the client has access to tools needed for agent replication and management.
    
    Args:
        client: The existing MCP client to enhance
        
    Returns:
        A new client that has both the original tools and replicator tools
    """
    # Create a new server instance for the enhanced client
    tool_server = FastMCP("enhanced_server")
    
    # Get tools from the original session and register them directly
    for tool in client.session.tools:
        asyncio.run(tool_server.register_tool(tool))
    
    # Add the replicator and echo tools
    asyncio.run(tool_server.import_server("replicator_tools", replicator_tools_server))
    asyncio.run(tool_server.import_server("echo_tools", echo_mcp_server))
    
    return Client(tool_server)


def create_runner(input_config: AgentProcessInput) -> Optional[AgentRunner]:
    """Create an appropriate runner instance and set up its runtime environment.

    Args:
        input_config: Configuration for the agent process containing type, instruction,
                     tool names, and other settings needed to create and configure the runner

    Returns:
        An instance of AgentRunner or None if creation fails
    """
    # Set up runtime environment first
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
