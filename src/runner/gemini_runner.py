from .agent_runner import AgentRunner
from google import genai

class GeminiRunner(AgentRunner):
    def __init__(self, model: str = "gemini-2.0-flash-001", tools: list = None):
        self.client = genai.Client()
        self.model = model
        self.tools = tools if tools is not None else []

    def getResponse(self, query_string: str):
        return self.client.models.generate_content(
            model=self.model, contents=query_string
        )
