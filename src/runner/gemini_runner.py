import asyncio
import logging

from fastmcp import Client, FastMCP
from google import genai
from google.genai import types

from runner.agent_runner import AgentRunner
from sessions.session_manager import SessionsManager
from utils.logging_config import setup_logger


class GeminiRunner(AgentRunner):
    def __init__(
        self,
        instruction: str,
        model: str = "gemini-2.0-flash-001",
        log_level: int = logging.INFO,
    ):
        self.logger = setup_logger(__name__, log_level)
        self.logger.debug("Initializing GeminiRunner")

        self.client = genai.Client()
        self.model = model
        self.instruction = instruction
        self.log_level = log_level

        # Initialize session manager immediately
        self._session_manager = SessionsManager()
        self._session_id = self._session_manager.createSession(instruction)

        # Initialize event loop
        self._event_loop = asyncio.new_event_loop()

        # MCP client will be configured later
        self._mcp_client = None

        self.logger.debug("GeminiRunner initialized with session %s", self._session_id)

    def configureMcp(self, client: Client) -> None:
        """Configure the MCP client for this runner.

        Args:
            client: The configured MCP client to use
        """
        self.logger.debug("Configuring MCP client")
        self._mcp_client = client

    async def getResponseAsync(self, query_string: str):
        self.logger.debug("Processing query: %s", query_string)
        session = self._session_manager.getSessionDetails(self._session_id)
        self._session_manager.recordUserInteractionInSession(
            self._session_id, query_string
        )

        prompt = ""
        for user_message, system_message in zip(
            session.user_messages, session.system_messages
        ):
            prompt += "User: " + user_message + "\n"
            prompt += "System: " + system_message + "\n"
        prompt += "User: " + query_string + "\n"

        tools = []
        if self._mcp_client:
            async with self._mcp_client:
                tools = [self._mcp_client.session]

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=session.base_instruction, tools=tools
            ),
        )

        self.logger.debug("Raw response: %s", response)

        response_txt = response.text
        if response_txt is not None:
            self._session_manager.recordSystemInteractionInSession(
                self._session_id, response_txt
            )
        return response_txt

    def getResponse(self, query: str):
        return self._event_loop.run_until_complete(self.getResponseAsync(query))

    async def cleanup(self):
        """Cleanup event loop"""
        if self._event_loop and not self._event_loop.is_closed():
            self._event_loop.close()
            self._event_loop = None
