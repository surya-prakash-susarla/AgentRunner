import logging
from typing import List, Optional

from fastmcp import FastMCP

from src.config.config_manager import RunnerType, get_config_manager
from src.process.agent_process_input import AgentProcessInput
from src.process.exceptions import ChildAgentNotFoundError
from src.process.replica_manager import get_replica_manager
from src.utils.logging_config import setup_logger

# Set up logging
logger = setup_logger(__name__, logging.INFO)

# Create FastMCP app
replicator_tools_server: FastMCP = FastMCP("ReplicatorToolsServer")


@replicator_tools_server.tool()
async def create_child_agent(
    child_type: str,
    child_name: str,
    instruction: str,
    tool_names: Optional[List[str]] = None,
) -> str:
    """Create a new child agent process.

    Args:
        child_type: Type of agent to create ('gemini', etc.)
        child_name: Name for the new child agent
        instruction: Base instruction for the agent
        tool_names: Optional list of tool names to give the agent access to

    Returns:
        Success or error message string

    Raises:
        ValueError: If the agent type or configuration is invalid
        Exception: For other creation failures
    """
    logger.info(
        "Received create_child_agent request for %s with instruction: %s",
        child_type,
        instruction,
    )

    try:
        # Get the global replica manager
        replica_manager = get_replica_manager()

        # Validate that the agent name exists in the config
        config_manager = get_config_manager()
        try:
            # Convert string to RunnerType enum directly
            runner_type = RunnerType(child_type.lower())
        except ValueError:
            available_types = [t.value for t in RunnerType]
            raise ValueError(
                f"Invalid runner type: {child_type}. Must be one of {available_types}"
            )

        input_config = AgentProcessInput(
            name=child_name,
            child_type=runner_type,
            instruction=instruction,
            tool_names=tool_names if tool_names else [],
        )
        replica_manager.create_child(input_config)

        success_msg = (
            f"Successfully created child agent '{child_type}' "
            f"with instruction: {instruction}"
        )
        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to create child agent: {str(e)}"
        logger.error(error_msg)
        # Re-raise the exception to be handled by the MCP framework
        raise


@replicator_tools_server.tool()
async def ask_child_agent(child_name: str, question: str) -> str:
    """Send a question to a specific child agent and wait for response.

    Args:
        child_name: The name of the child agent to ask (e.g. 'agent_1')
        question: The question to ask the child agent

    Returns:
        str: The child agent's response

    Raises:
        ChildAgentNotFoundError: If the specified child agent doesn't exist
        ChildAgentNotRunningError: If the child agent process is not running
        ChildAgentTimeoutError: If the request times out
        ChildAgentOperationError: If there's an error getting the response

    """
    logger.info("Received request to ask child agent '%s': %s", child_name, question)

    try:
        # Get the global replica manager
        replica_manager = get_replica_manager()

        # Check if the specified child exists
        if child_name not in replica_manager.children:
            raise ChildAgentNotFoundError(child_name)

        # Ask the question and return the response
        logger.info("Forwarding question to child agent '%s'", child_name)
        response = replica_manager.ask_child(child_name, question)
        logger.info("Received response from child agent '%s'", child_name)
        return response

    except Exception as e:
        error_msg = f"Failed to get response from child agent: {str(e)}"
        logger.error(error_msg)
        # Re-raise the exception to be handled by the MCP framework
        raise


@replicator_tools_server.tool()
async def get_current_children() -> str:
    """List all currently running child agents.

    Returns:
        A message listing active child agents, or indicating none exist.

    Raises:
        ChildAgentOperationError: If there's an error accessing children.

    """
    logger.info("Received request to list current child agents")

    try:
        # Get the global replica manager
        replica_manager = get_replica_manager()

        if not replica_manager.children:
            return "No child agents currently exist"

        # Get all child names and create readable list
        child_names = list(replica_manager.children.keys())
        child_list = ", ".join(child_names)
        msg = (
            f"Current child agents: {child_list}. "
            "Use these exact names when working with these agents."
        )
        logger.info(msg)
        return msg

    except Exception as e:
        error_msg = f"Failed to list child agents: {str(e)}"
        logger.error(error_msg)
        # Re-raise the exception to be handled by the MCP framework
        raise


@replicator_tools_server.tool()
async def kill_child_agent(child_name: str) -> str:
    """Terminate a specific child agent process.

    Cleanly shuts down the specified child agent and removes it from the system.

    Args:
        child_name: Name of the child agent to terminate (e.g. 'agent_1').

    Returns:
        A message confirming the child agent was terminated.

    Raises:
        ChildAgentNotFoundError: If the specified child agent doesn't exist.
        ChildAgentOperationError: If there's an error during termination.

    """
    logger.info("Received request to terminate child agent '%s'", child_name)

    try:
        # Get the global replica manager
        replica_manager = get_replica_manager()

        # Check if the specified child exists
        if child_name not in replica_manager.children:
            raise ChildAgentNotFoundError(child_name)

        # Kill the child process
        replica_manager.kill_child(child_name)

        success_msg = f"Successfully terminated child agent '{child_name}'"
        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to terminate child agent: {str(e)}"
        logger.error(error_msg)
        # Re-raise the exception to be handled by the MCP framework
        raise


@replicator_tools_server.tool()
async def get_available_child_types() -> List[str]:
    """Return a list of available child agent types from the config.

    Returns:
        List[str]: The available child agent types, use values exactly as returned.

    """
    logger.info("Received request to list available child agent types")
    from src.config.config_manager import get_config_manager

    try:
        config_manager = get_config_manager()
        available_runners = [
            agent.runner.value for agent in config_manager.agents.values()
        ]
        return available_runners
    except Exception as e:
        error_msg = f"Failed to list available child agent types: {str(e)}"
        logger.error(error_msg)
        raise
