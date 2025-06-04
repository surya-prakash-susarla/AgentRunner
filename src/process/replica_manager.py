import logging
from functools import lru_cache
from typing import Dict, Optional

from src.config.config_manager import get_config_manager
from src.process.agent_process import AgentProcess
from src.process.agent_process_input import AgentProcessInput
from src.process.exceptions import (
    ChildAgentExistsError,
    ChildAgentNotFoundError,
    ChildAgentNotRunningError,
    ChildAgentOperationError,
    ChildAgentTimeoutError,
    MaxChildrenExceededError,
)
from src.utils.logging_config import setup_logger

logger = setup_logger(__name__, logging.INFO)


class ReplicaManager:
    """Manager for child agent processes and their lifecycle.

    Handles creation, communication, and cleanup of child agent processes. Maintains
    a registry of active child agents and enforces process limits.
    """

    def __init__(self, max_children: int = 1):
        """Initialize the replica manager.

        Args:
            max_children: Maximum number of child agents that can be spawned.

        """
        self.max_children = max_children
        self.children: Dict[str, AgentProcess] = {}
        logger.info("Initialized ReplicaManager with max_children=%d", max_children)

    def create_child(self, input_config: AgentProcessInput) -> None:
        """Create a new child agent process.

        Creates and initializes a new agent process with the provided configuration.
        The agent is registered and started upon successful creation.

        Args:
            input_config: Configuration for the new agent process with core settings.

        Raises:
            MaxChildrenExceededError: If maximum number of children has been reached.
            ChildAgentExistsError: If a child with the given name already exists.
            ChildAgentOperationError: If there's an error creating the child process.

        """
        logger.info("Attempting to create child agent '%s'", input_config.child_type)

        if len(self.children) >= self.max_children:
            logger.warning(
                "Cannot create child '%s': maximum children limit (%d) reached",
                input_config.name,
                self.max_children,
            )
            raise MaxChildrenExceededError(self.max_children)

        if input_config.name in self.children:
            logger.warning("Child with name '%s' already exists", input_config.name)
            raise ChildAgentExistsError(input_config.name)

        try:
            logger.info(
                "Creating new AgentProcess for child '%s'", input_config.child_type
            )
            process = AgentProcess(input_config=input_config)
            self.children[input_config.name] = process
            logger.info("Successfully created child agent '%s'", input_config.name)
        except Exception as e:
            logger.error(
                "Failed to create child agent '%s': %s", input_config.name, str(e)
            )
            raise ChildAgentOperationError(input_config.name, "creation", str(e)) from e

    def get_child(self, name: str) -> Optional[AgentProcess]:
        """Get a child agent by name.

        Retrieves a child agent process by its registered name.

        Args:
            name: The identifier of the child to retrieve.

        Returns:
            Optional[AgentProcess]: The child agent process if it exists.

        """
        logger.debug("Attempting to get child agent '%s'", name)
        process = self.children.get(name)
        if process:
            logger.debug("Found child agent '%s'", name)
        else:
            logger.debug("Child agent '%s' not found", name)
        return process

    def ask_child(
        self, name: str, question: str, timeout: Optional[float] = None
    ) -> str:
        """Send a question to a specific child agent.

        Sends a question to the specified child agent and waits for a response.

        Args:
            name: The identifier of the child to ask.
            question: The question to ask the child.
            timeout: Optional timeout for waiting for response.

        Returns:
            str: The child's response.

        Raises:
            ChildAgentNotFoundError: If the specified child does not exist.
            ChildAgentNotRunningError: If the child process is not running.
            ChildAgentTimeoutError: If the request times out.
            ChildAgentOperationError: If there's an error getting the response.

        """
        logger.info("Attempting to ask child '%s' question: %s", name, question)

        process = self.get_child(name)
        if not process:
            logger.warning("Child agent '%s' not found", name)
            raise ChildAgentNotFoundError(name)

        if not process.is_alive():
            logger.warning("Child agent '%s' is not running", name)
            raise ChildAgentNotRunningError(name)

        try:
            logger.debug("Sending question to child '%s'", name)
            response = process.ask(question, timeout=timeout)
            logger.info("Received response from child '%s'", name)
            return response
        except TimeoutError as e:
            logger.error("Timeout waiting for response from child agent '%s'", name)
            raise ChildAgentTimeoutError(name) from e
        except Exception as e:
            logger.error(
                "Error getting response from child agent '%s': %s", name, str(e)
            )
            raise ChildAgentOperationError(name, "question", str(e)) from e

    def kill_child(self, name: str) -> None:
        """Terminate a specific child agent process.

        Stops and cleans up a child agent process, removing it from the registry.

        Args:
            name: The identifier of the child to terminate.

        Raises:
            ChildAgentNotFoundError: If the specified child does not exist.
            ChildAgentOperationError: If there's an error terminating the process.

        """
        logger.info("Attempting to kill child agent '%s'", name)

        process = self.get_child(name)
        if not process:
            logger.warning("Child agent '%s' not found", name)
            raise ChildAgentNotFoundError(name)

        try:
            if process.is_alive():
                process.kill()
                logger.info("Successfully terminated child agent '%s'", name)
            else:
                logger.info("Child agent '%s' was already terminated", name)

            del self.children[name]
        except Exception as e:
            logger.error("Error terminating child agent '%s': %s", name, str(e))
            raise ChildAgentOperationError(name, "termination", str(e)) from e


@lru_cache(maxsize=1)
def get_replica_manager() -> ReplicaManager:
    """Get or create the global ReplicaManager instance.

    Returns:
        ReplicaManager: The global ReplicaManager instance.

    """
    runtime = get_config_manager().runtime
    if runtime is None:
        raise ValueError("Runtime configuration is not available")
    return ReplicaManager(max_children=runtime.max_global_children)
