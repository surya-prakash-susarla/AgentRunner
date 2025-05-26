from runner.gemini_runner import GeminiRunner
from sessions.session_manager import SessionsManager
from dotenv import load_dotenv

load_dotenv()

session_manager = SessionsManager()
instruction = "You are a general purpose agent to chat with the user"
runner = GeminiRunner(session_manager=session_manager, instruction=instruction)

while True:
    query = input("You: ")
    response = runner.getResponse(query)
    print("Agent: " + response)
