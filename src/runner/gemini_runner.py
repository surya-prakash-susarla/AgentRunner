import asyncio
import logging
from typing import Any, List, Optional, cast

from fastmcp import Client, FastMCP
from fastmcp.mcp.types import ClientSession
from google import genai
from google.genai import types
from google.generativeai.types import Tool

from src.runner.agent_runner import AgentRunner
from src.sessions.session_manager import SessionsManager
from src.utils.logging_config import setup_logger


class GeminiRunner(AgentRunner):
    def __init__(
        self,
        instruction: str,
        model: str = "gemini-2.0-flash-001",
        log_level: int = logging.INFO,
    ) -> None:
        self.logger = setup_logger(__name__, log_level)
        self.logger.debug("Initializing GeminiRunner")

        self.client: genai.Client = genai.Client()
        self.model: str = model
        self.instruction: str = instruction
        self.log_level: int = log_level
        self._mcp_client: Client | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

        # Initialize session manager immediately
        self._session_manager: SessionsManager = SessionsManager()
        self._session_id: str = self._session_manager.createSession(instruction)

        # Initialize event loop
        self._event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()

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

    def getMcpClient(self) -> Optional[Client]:
        """Get the MCP client if one is configured for this agent.

        Returns:
            The configured MCP client if it exists, None otherwise
        """
        return self._mcp_client

    async def getResponseAsync(self, query_string: str) -> Optional[str]:
        self.logger.debug("Processing query: %s", query_string)
        session = self._session_manager.getSession(self._session_id)
        if session is None:
            self.logger.error("Session not found: %s", self._session_id)
            return None

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

        if self._mcp_client:
            async with self._mcp_client:
                tools: List[Tool] = [cast(Tool, self._mcp_client.session)]
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=session.base_instruction, tools=tools
                    ),
                )
        else:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=session.base_instruction
                ),
            )

        self.logger.debug("Raw response: %s", response)

        response_txt = response.text
        if response_txt is not None:
            self._session_manager.recordSystemInteractionInSession(
                self._session_id, response_txt
            )
        return response_txt

    def getResponse(self, query: str) -> str:
        result = self._event_loop.run_until_complete(self.getResponseAsync(query))
        if result is None:
            raise RuntimeError("Failed to get response from model")
        return result

    async def cleanup(self) -> None:
        """Cleanup event loop"""
        if self._event_loop and not self._event_loop.is_closed():
            self._event_loop.close()
            self._event_loop = None
