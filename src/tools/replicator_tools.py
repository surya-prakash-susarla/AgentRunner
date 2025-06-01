import logging
from typing import List

from fastmcp import FastMCP, Client

from src.process.exceptions import (
    ChildAgentNotFoundError,
    ChildAgentNotRunningError,
    ChildAgentTimeoutError,
    ChildAgentOperationError,
)
from src.process.replica_manager import get_replica_manager
from src.process.agent_process_input import AgentProcessInput
from src.utils.logging_config import setup_logger

# Set up logging
logger = setup_logger(__name__, logging.INFO)

# Create FastMCP app
replicator_tools_server = FastMCP("ReplicatorToolsServer")


@replicator_tools_server.tool()
async def create_child_agent(child_type: str, child_name: str, instruction: str, tool_names: List[str] = None) -> str:
    """Creates a specialized child agent of a given type with specific tools and instruction.

    This tool creates a child agent that is specialized for a particular task through its instruction
    and has access to a specific set of tools that are relevant to its purpose. The tool names provided
    must exactly match the names of tools available to the caller, and should be scoped appropriately
    to match the instruction being given to the agent.

    Args:
        child_type: The type of the child agent to create (must match a name in the config)
        child_name: The name of the child agent (must be referenced verbatim in further calls to converse with the child)
        instruction: The base instruction/system prompt for the child agent
        tool_names: List of tool names the child agent should have access to. Tools should be relevant to the instruction. Tool names should match verbatim to the list provided to the caller.

    Returns:
        str: A message describing the result of the operation

    Raises:
        MaxChildrenExceededError: If maximum number of children has been reached
        ChildAgentExistsError: If a child with the given name already exists
        ChildAgentOperationError: If there's an error creating the child process
    """
    logger.info(
        "Received request to create child agent with name: %s and instruction: %s",
        child_type,
        instruction,
    )

    try:
        # Get the global replica manager
        replica_manager = get_replica_manager()

        # Validate that the agent name exists in the config
        from src.config.config_manager import get_config_manager

        config_manager = get_config_manager()
        if child_type not in config_manager.agents:
            raise ValueError(f"Agent name '{child_type}' not found in config")

        # Create the child process through the replica manager
        logger.info("Creating child agent of type: %s", child_type)
        # Convert None to empty list for tool_names
        tools_list = tool_names if tool_names else []
        
        input_config = AgentProcessInput(
            name=child_name,
            child_type=child_type,
            instruction=instruction,
            tool_names=tools_list
        )
        replica_manager.create_child(input_config)

        success_msg = f"Successfully created child agent '{child_type}' with instruction: {instruction}"
        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to create child agent: {str(e)}"
        logger.error(error_msg)
        # Re-raise the exception to be handled by the MCP framework
        raise


@replicator_tools_server.tool()
async def ask_child_agent(child_name: str, question: str) -> str:
    """Sends a question to a specific child agent and waits for response

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
    """Gets the names of all currently running child agents

    Returns:
        str: A message listing all current child agent names, or indicating no children exist

    Raises:
        ChildAgentOperationError: If there's an error accessing the children
    """
    logger.info("Received request to list current child agents")

    try:
        # Get the global replica manager
        replica_manager = get_replica_manager()

        if not replica_manager.children:
            return "No child agents currently exist"

        # Get all child names and their states
        child_names = list(replica_manager.children.keys())
        child_list = ", ".join(child_names)

        success_msg = f"Current child agents: {child_list}. Use the exact names when referencing children in future queries."
        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to list child agents: {str(e)}"
        logger.error(error_msg)
        # Re-raise the exception to be handled by the MCP framework
        raise


@replicator_tools_server.tool()
async def kill_child_agent(child_name: str) -> str:
    """Terminates a specific child agent process

    Args:
        child_name: The name of the child agent to terminate (e.g. 'agent_1')

    Returns:
        str: A message confirming the child agent was terminated

    Raises:
        ChildAgentNotFoundError: If the specified child agent doesn't exist
        ChildAgentOperationError: If there's an error terminating the process
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
    """Gets the available child agent types from the config.

    Returns:
        List[str]: A list of the available child agent types. These types should be used exactly as returned.
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
