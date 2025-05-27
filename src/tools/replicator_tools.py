from fastmcp import FastMCP, Client
from runner.gemini_runner import GeminiRunner
from sessions.session_manager import SessionsManager
from utils.logging_config import setup_logger
from tools.samples.server import echo_mcp_server
import logging

# Set up logging
logger = setup_logger(__name__, logging.INFO)

# We'll use the replica manager instead of global state
from process.replica_manager import get_replica_manager

# Create FastMCP app
replicator_tools_server = FastMCP("ReplicatorToolsServer")

@replicator_tools_server.tool()
async def create_child_agent(instruction: str) -> str:
    """Creates a child agent if one doesn't exist yet
    
    Args:
        instruction: The base instruction/system prompt for the child agent
        
    Returns:
        str: A message describing the result of the operation
    """
    pass

@replicator_tools_server.tool()
async def ask_child_agent(question: str) -> str:
    """Sends a question to the child agent and waits for response
    
    Args:
        question: The question to ask the child agent
        
    Returns:
        str: The child agent's response
    """
    pass
