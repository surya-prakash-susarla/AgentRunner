from runner.agent_runner import AgentRunner
from google import genai
from google.genai import types
from sessions.session_manager import SessionsManager
from fastmcp import Client
import asyncio
from typing import List, Dict


class GeminiRunner(AgentRunner):
    def __init__(
        self,
        session_manager: SessionsManager,
        instruction: str,
        model: str = "gemini-2.0-flash-001",
        mcp_client: Client = None
    ):
        self.client = genai.Client()
        self.model = model
        self.mcp_client = mcp_client
        self.mcp_sessions: Dict = {}
        self.session_manager = session_manager
        self.session_id = self.session_manager.createSession(instruction)
        self.event_loop = asyncio.new_event_loop()

    async def getResponseAsync(self, query_string: str):
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

        async with self.mcp_client:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=session.base_instruction,
                    tools=[self.mcp_client.session]
                ),
            )

        print("Raw response: {response}".format(response=response))

        response_txt = response.text
        if response_txt is not None:
            self.session_manager.recordSystemInteractionInSession(self.session_id, response_txt)
        return response_txt
    
    def getResponse(self, query: str):
        return self.event_loop.run_until_complete(self.getResponseAsync(query))

    async def cleanup(self):
        """Cleanup all MCP sessions"""
        for session in self.mcp_sessions.values():
            await session.close()
