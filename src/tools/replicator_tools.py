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
async def ask_child_agent(question: str) -> str:
    """Sends a question to the child agent and waits for response

    Args:
        question: The question to ask the child agent

    Returns:
        str: The child agent's response

    Raises:
        ChildAgentNotFoundError: If no child agent exists
        ChildAgentNotRunningError: If the child agent process is not running
        ChildAgentTimeoutError: If the request times out
        ChildAgentOperationError: If there's an error getting the response
    """
    logger.info("Received request to ask child agent: %s", question)

    try:
        # Get the global replica manager
        replica_manager = get_replica_manager()

        # Get the first child (since we only support one for now)
        if not replica_manager.children:
            raise ChildAgentNotFoundError(
                "any"
            )  # No specific name since we're getting first child

        # Get the first child's name
        child_name = next(iter(replica_manager.children.keys()))

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
