from runner.gemini_runner import GeminiRunner
from sessions.session_manager import SessionsManager
from dotenv import load_dotenv
from tools.description_generator import generateToolsConfig
from tools.samples.server import echo_mcp_server
from tools.replicator_tools import agent_mcp_server
from tools.samples.test_server import test_server
from fastmcp import Client
from utils.logging_config import setup_logger
import asyncio
import logging

# Set up logging for the main module
logger = setup_logger(__name__, logging.INFO)

load_dotenv()


def getSampleClient():
    # NOTE: A single client can contain multiple servers.
    # Combine both echo and replicator tools in one client
    return Client([echo_mcp_server, agent_mcp_server])

logger.info("Initializing MCP servers for testing")
# To send a quick message for testing the echo MCP server.
# test_server()

# Initialize clients and session manager
session_manager = SessionsManager()
instruction = "You are a general purpose agent to chat with the user. You can use tools when needed."

# Create runner with MCP clients
runner = GeminiRunner(
    session_manager=session_manager,
    instruction=instruction,
    mcp_client=getSampleClient(),
    model="gemini-2.0-flash-001"
)

# Main chat loop
try:
    logger.info("Starting chat session. Type 'exit' or 'quit' to end.")
    while True:
        query = input("You: ")
        if query.lower() in ['exit', 'quit']:
            logger.info("Chat session ended by user")
            break
        response = runner.getResponse(query)
        logger.info("Response from agent: %s", response)
finally:
    # Cleanup when done
    asyncio.run(runner.cleanup())
