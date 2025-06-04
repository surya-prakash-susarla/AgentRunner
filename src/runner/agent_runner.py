from abc import ABC, abstractmethod
from typing import Optional

from fastmcp import Client

"""Abstract agent runner class to be implemented for each LLM type"""


class AgentRunner(ABC):
    @abstractmethod
    def getResponseAsync(self, query_string: str) -> str:
        """Get a response from the agent asynchronously.

        Args:
            query_string: The query to send to the agent

        Returns:
            The agent's response
        """
        pass

    @abstractmethod
    def getResponse(self, query_string: str) -> str:
        """Get a response from the agent synchronously.

        Args:
            query_string: The query to send to the agent

        Returns:
            The agent's response
        """
        pass

    @abstractmethod
    def configureMcp(self, client: Client) -> None:
        """Configure the MCP client for this agent.

        Args:
            client: The configured MCP client to use
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup any resources used by the agent."""
        pass

    @abstractmethod
    def getMcpClient(self) -> Optional[Client]:
        """Get the MCP client if one is configured for this agent.

        Returns:
            The configured MCP client if it exists, None otherwise
        """
        pass
