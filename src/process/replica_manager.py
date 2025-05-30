from typing import Optional, Dict
from functools import lru_cache
from src.process.process import AgentProcess
from src.runner.gemini_runner import GeminiRunner
from src.utils.logging_config import setup_logger
from src.process.exceptions import (
    MaxChildrenExceededError,
    ChildAgentNotFoundError,
    ChildAgentExistsError,
    ChildAgentNotRunningError,
    ChildAgentTimeoutError,
    ChildAgentOperationError,
)
import logging
from src.config.config_manager import RunnerType, get_config_manager

logger = setup_logger(__name__, logging.INFO)


class ReplicaManager:
    def __init__(self, max_children: int = 1):
        """Initialize the replica manager

        Args:
            max_children: Maximum number of child agents that can be spawned
        """
        self.max_children = max_children
        self.children: Dict[str, AgentProcess] = {}
        logger.info("Initialized ReplicaManager with max_children=%d", max_children)

    def create_child(self, name: str, child_type: RunnerType, instruction: str) -> None:
        """Create a new child agent process

        Args:
            name: The name of the child agent
            child_type: The type of the runner to use for the child agent
            instruction: The instruction/system prompt for the child agent

        Raises:
            MaxChildrenExceededError: If maximum number of children has been reached
            ChildAgentExistsError: If a child with the given name already exists
            ChildAgentOperationError: If there's an error creating the child process
        """
        logger.info("Attempting to create child agent '%s'", child_type)

        if len(self.children) >= self.max_children:
            logger.warning(
                "Cannot create child '%s': maximum children limit (%d) reached",
                name,
                self.max_children,
            )
            raise MaxChildrenExceededError(self.max_children)

        if name in self.children:
            logger.warning("Child with name '%s' already exists", name)
            raise ChildAgentExistsError(name)

        try:
            logger.info("Creating new AgentProcess for child '%s'", child_type)
            process = AgentProcess(
                name=name, instruction=instruction, child_type=child_type
            )
            self.children[name] = process
            logger.info("Successfully created child agent '%s'", name)
        except Exception as e:
            logger.error("Failed to create child agent '%s': %s", name, str(e))
            raise ChildAgentOperationError(name, "creation", str(e)) from e

    def get_child(self, name: str) -> Optional[AgentProcess]:
        """Get a child agent by name

        Args:
            name: The identifier of the child to retrieve

        Returns:
            Optional[AgentProcess]: The child agent process if it exists
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
        """Send a question to a specific child agent

        Args:
            name: The identifier of the child to ask
            question: The question to ask the child
            timeout: Optional timeout for waiting for response

        Returns:
            str: The child's response

        Raises:
            ChildAgentNotFoundError: If the specified child does not exist
            ChildAgentNotRunningError: If the child process is not running
            ChildAgentTimeoutError: If the request times out
            ChildAgentOperationError: If there's an error getting the response
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
        """Terminate a specific child agent process

        Args:
            name: The identifier of the child to terminate

        Raises:
            ChildAgentNotFoundError: If the specified child does not exist
            ChildAgentOperationError: If there's an error terminating the child process
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
    """Get or create the global ReplicaManager instance

    Returns:
        ReplicaManager: The global ReplicaManager instance
    """
    return ReplicaManager(max_children=get_config_manager().runtime.max_global_children)
