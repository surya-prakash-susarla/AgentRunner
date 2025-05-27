from runner.gemini_runner import GeminiRunner
from sessions.session_manager import SessionsManager
from dotenv import load_dotenv
from tools.description_generator import generateToolsConfig
from tools.samples.server import echo_mcp_server
from tools.samples.test_server import test_server
from fastmcp import Client
import asyncio

load_dotenv()


def getSampleClient():
    # NOTE: A single client can contain multiple servers.
    return Client(echo_mcp_server)

print("Testing the echo server")
test_server()

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
    while True:
        query = input("You: ")
        if query.lower() in ['exit', 'quit']:
            break
        response = runner.getResponse(query)
        print("Response from agent: {response}".format(response=str(response)))
finally:
    # Cleanup when done
    asyncio.run(runner.cleanup())
