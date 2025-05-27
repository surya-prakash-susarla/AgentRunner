from runner.gemini_runner import GeminiRunner
from sessions.session_manager import SessionsManager
from dotenv import load_dotenv
from fastmcp import Client
from samples.server import echo_mcp_server
import asyncio

load_dotenv()

async def list_tools():
    async with client:
        result = await client.list_tools()
        return result

client = Client(echo_mcp_server)

response = asyncio.run(list_tools())
print("Sample mcp server response: {response}".format(response=response))

session_manager = SessionsManager()
instruction = "You are a general purpose agent to chat with the user"
runner = GeminiRunner(session_manager=session_manager, instruction=instruction)

while True:
    query = input("You: ")
    response = runner.getResponse(query)
    print("Agent: " + response)
