from runner.gemini_runner import GeminiRunner
from dotenv import load_dotenv

load_dotenv()

runner = GeminiRunner()
query = "How are you?"
response = runner.getResponse(query)

print("Raw response from client: {response}".format(response=response))
print("*" * 10)
print("Text contents in response: {text}".format(text=response.text))
