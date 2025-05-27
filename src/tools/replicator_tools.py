from fastmcp import FastMCP, Client
from runner.gemini_runner import GeminiRunner
from sessions.session_manager import SessionsManager
from utils.logging_config import setup_logger
from tools.samples.server import echo_mcp_server
import logging

# Set up logging
logger = setup_logger(__name__, logging.INFO)

# Global state for child agent management
child_agent: GeminiRunner | None = None
has_child = False

# Create FastMCP app
agent_mcp_server = FastMCP()

@agent_mcp_server.tool()
async def create_child_agent(instruction: str) -> str:
    """Creates a child agent if one doesn't exist yet
    
    Args:
        instruction: The base instruction/system prompt for the child agent
        
    Returns:
        str: A message describing the result of the operation - either success message
            with the instruction given to the new agent, or a message indicating an
            agent already exists
    """
    global child_agent, has_child
    
    if has_child:
        logger.info("Child agent already exists")
        return "A child agent already exists. You must use ask_child_agent to interact with it."
        
    logger.info("Creating new child agent with instruction: %s", instruction)
    session_manager = SessionsManager()
    
    # Create child agent with the same echo tool access
    child_agent = GeminiRunner(
        session_manager=session_manager,
        instruction=instruction,
        mcp_client=Client(echo_mcp_server)  # Give child the same echo tool
    )
    has_child = True
    return f"Successfully created a new child agent with the following instruction: {instruction}"

@agent_mcp_server.tool()
async def ask_child_agent(question: str) -> str:
    """Sends a question to the child agent and waits for response
    
    Args:
        question: The question to ask the child agent
        
    Returns:
        str: The child agent's response, or error message if no child exists
    """
    global child_agent
    
    if not has_child or child_agent is None:
        return "Error: No child agent exists. Create one first using create_child_agent."
        
    logger.info("Asking child agent: %s", question)
    response = child_agent.getResponse(question)
    logger.info("Child agent responded: %s", response)
    return response
