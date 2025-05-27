from runner.gemini_runner import GeminiRunner
from sessions.session_manager import SessionsManager
from dotenv import load_dotenv
from tools.samples.server import echo_mcp_server
from tools.replicator_tools import replicator_tools_server
from fastmcp import Client, FastMCP
from utils.logging_config import setup_logger
import asyncio
import logging

# Set up logging for the main module
logger = setup_logger(__name__, logging.INFO)

load_dotenv()


def getSampleClient():
    # NOTE: A single client can contain multiple servers.
    tool_server = FastMCP("main_server")
    asyncio.run(tool_server.import_server("echo_tools", echo_mcp_server))
    asyncio.run(tool_server.import_server("replicator_tools", replicator_tools_server))
    return Client(tool_server)


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
    model="gemini-2.0-flash-001",
)

# Main chat loop
try:
    logger.info("Starting chat session. Type 'exit' or 'quit' to end.")
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            logger.info("Chat session ended by user")
            break
        response = runner.getResponse(query)
        logger.info("Response from agent: %s", response)
finally:
    # Cleanup when done
    asyncio.run(runner.cleanup())
