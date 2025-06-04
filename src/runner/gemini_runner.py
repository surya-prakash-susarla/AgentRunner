import asyncio
import logging
from typing import Any, List, Optional, Sequence, cast

from fastmcp import Client, FastMCP
from google import genai
from google.genai import types

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
        self._event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()

        # Initialize session manager immediately
        self._session_manager: SessionsManager = SessionsManager()
        self._session_id: str = self._session_manager.createSession(instruction)

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

    def getResponseAsync(self, query_string: str) -> str:
        """Get a response from the agent asynchronously.

        Note: This method is not supported in the base class, use getResponse instead.
        """
        raise NotImplementedError("Use getResponse instead - async methods not supported in base class")

    def getResponse(self, query_string: str) -> str:
        """Get a response from the agent synchronously.

        Args:
            query_string: The query to send to the agent

        Returns:
            The agent's response
        
        Raises:
            RuntimeError: If there's an error getting the response or if response is empty
        """
        async def _get_response() -> str:
            self.logger.debug("Processing query: %s", query_string)
            session = self._session_manager.getSessionDetails(self._session_id)
            if session is None:
                error_msg = f"Session not found: {self._session_id}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

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
                    # Using list instead of Sequence for tool type compatibility
                    tools = [cast(types.Tool, self._mcp_client.session)]
                    response = await self.client.aio.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=session.base_instruction, 
                            tools=tools
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
            if response_txt is None:
                raise RuntimeError("Received empty response from model")
                
            self._session_manager.recordSystemInteractionInSession(
                self._session_id, response_txt
            )
            return response_txt

        # Run the async function in the event loop
        response = self._event_loop.run_until_complete(_get_response())
        return response

    async def cleanup(self) -> None:
        """Cleanup event loop"""
        if self._event_loop and not self._event_loop.is_closed():
            self._event_loop.close()
            self._event_loop = cast(asyncio.AbstractEventLoop, None)
