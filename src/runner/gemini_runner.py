from runner.agent_runner import AgentRunner
from google import genai
from google.genai import types
from sessions.session_manager import SessionsManager


class GeminiRunner(AgentRunner):
    def __init__(
        self,
        session_manager: SessionsManager,
        instruction: str,
        model: str = "gemini-2.0-flash-001",
        tools: list = None,
    ):
        self.client = genai.Client()
        self.model = model
        self.tools = tools if tools is not None else []
        self.session_manager = session_manager
        self.session_id = self.session_manager.createSession(instruction)

    def getResponse(self, query_string: str):
        session = self.session_manager.getSessionDetails(self.session_id)
        self.session_manager.recordUserInteractionInSession(
            self.session_id, query_string
        )

        prompt = ""
        for user_message, system_message in zip(
            session.user_messages, session.system_messages
        ):
            prompt += "User: " + user_message + "\n"
            prompt += "System: " + system_message + "\n"
        prompt += "User: " + query_string + "\n"

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=session.base_instruction
            ),
        ).text

        self.session_manager.recordSystemInteractionInSession(self.session_id, response)
        return response
