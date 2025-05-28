import logging

from fastmcp import FastMCP, Client

from process.exceptions import (
    ChildAgentNotFoundError,
    ChildAgentNotRunningError,
    ChildAgentTimeoutError,
    ChildAgentOperationError,
)
from process.replica_manager import get_replica_manager
from runner.gemini_runner import GeminiRunner
from utils.logging_config import setup_logger

# Set up logging
logger = setup_logger(__name__, logging.INFO)

# Create FastMCP app
replicator_tools_server = FastMCP("ReplicatorToolsServer")


@replicator_tools_server.tool()
async def create_child_agent(instruction: str) -> str:
    """Creates a child agent if one doesn't exist yet

    Args:
        instruction: The base instruction/system prompt for the child agent

    Returns:
        str: A message describing the result of the operation

    Raises:
        MaxChildrenExceededError: If maximum number of children has been reached
        ChildAgentExistsError: If a child with the given name already exists
        ChildAgentOperationError: If there's an error creating the child process
    """
    logger.info(
        "Received request to create child agent with instruction: %s", instruction
    )

    try:
        # Get the global replica manager
        replica_manager = get_replica_manager()

        # Generate a unique name for this agent
        agent_name = f"agent_{len(replica_manager.children) + 1}"

        # Create the child process through the replica manager
        logger.info("Creating child agent with name: %s", agent_name)
        replica_manager.create_child(agent_name, instruction)

        success_msg = f"Successfully created child agent '{agent_name}' with instruction: {instruction}"
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
