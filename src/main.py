from runner.gemini_runner import GeminiRunner
from sessions.session_manager import SessionsManager
from dotenv import load_dotenv
from tools.description_generator import generateToolsConfig
from tools.samples.server import echo_mcp_server
from tools.samples.test_server import test_server
from fastmcp import Client
import asyncio

load_dotenv()


def getSampleToolList():
    echo_client = Client(echo_mcp_server)
    tools = asyncio.run(generateToolsConfig(echo_client))
    print("Formatted tool output: {output}".format(output=tools))
    return tools

print("Testing the echo server")
test_server()

sample_tools = getSampleToolList()
session_manager = SessionsManager()
instruction = "You are a general purpose agent to chat with the user"
runner = GeminiRunner(
    session_manager=session_manager, instruction=instruction, tools=sample_tools
)

while True:
    query = input("You: ")
    response = runner.getResponse(query)
    print("Response from agent: {response}".format(response=str(response)))
