import asyncio
import logging

from dotenv import load_dotenv
from fastmcp import Client, FastMCP

from runner.gemini_runner import GeminiRunner
from tools.samples.server import echo_mcp_server
from tools.replicator_tools import replicator_tools_server
from utils.cleanup import cleanup_manager
from utils.logging_config import setup_logger

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

# Create the instruction for our agent
instruction = "You are a general purpose agent to chat with the user. You can use tools when needed."

# Create runner and configure it with tools
runner = GeminiRunner(instruction=instruction, model="gemini-2.0-flash-001")
runner.configureMcp(getSampleClient())

# Register the runner with the cleanup manager
cleanup_manager.register_runner(runner)

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
except KeyboardInterrupt:
    logger.info("\nReceived keyboard interrupt, shutting down...")
except Exception as e:
    logger.error("Unexpected error: %s", str(e))
finally:
    # Run cleanup directly here as well, in case the signal handlers don't trigger
    cleanup_manager.cleanup_all_processes()
