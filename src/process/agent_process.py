import asyncio
import logging
import os
import queue
from multiprocessing import Process, Queue, current_process
from typing import Optional, cast

from src.runner.runner_factory import create_runner
from src.utils.logging_config import setup_logger

from .agent_process_input import AgentProcessInput


class AgentProcess:
    def __init__(self, input_config: AgentProcessInput) -> None:
        self.input_q: Queue = Queue()
        self.output_q: Queue = Queue()
        self._input_config: AgentProcessInput = input_config
        self.logger = setup_logger(__name__, logging.INFO)
        self.logger.info("Initializing agent process %s", input_config.name)

        # Launch the process
        self.proc = Process(
            target=self._run_agent,
            args=(self.input_q, self.output_q, input_config),
            daemon=True,
        )
        self.proc.start()

    @staticmethod
    def _run_agent(
        input_q: Queue, output_q: Queue, input_config: AgentProcessInput
    ) -> None:
        """Run loop for the child agent."""

        proc = current_process()
        logger = setup_logger(f"{__name__}.{proc.name}", logging.INFO)
        logger.info("Starting agent process. PID: %d, Name: %s", os.getpid(), proc.name)

        runner = None
        try:
            # Create runner inside the child process
            runner = create_runner(input_config)
            if runner == None:
                raise Exception(
                    "No runner could be created, the given child type was: {child_type}".format(
                        child_type=input_config.child_type
                    )
                )

            while True:
                query = input_q.get()
                if query == "__EXIT__":
                    logger.info(
                        "Received exit signal. Shutting down process %d", os.getpid()
                    )
                    break

                try:
                    response = runner.getResponse(query)
                except Exception as e:
                    logger.error("Error processing query: %s", str(e))
                    response = f"[Agent Error]: {str(e)}"

                try:
                    output_q.put(response)
                except Exception as e:
                    logger.error("Error sending response: %s", str(e))

        except Exception as e:
            logger.error("Fatal error in agent process: %s", str(e))
            try:
                output_q.put(f"[Fatal Agent Error]: {str(e)}")
            except:
                pass
        finally:
            if runner:
                try:
                    asyncio.run(runner.cleanup())
                    logger.info("Runner cleanup completed")
                except Exception as e:
                    logger.error("Error during runner cleanup: %s", str(e))

    def ask(self, message: str, timeout: Optional[float] = None) -> str:
        """Send message to the agent and get the response.

        Args:
            message: The message to send to the agent
            timeout: Optional timeout in seconds

        Returns:
            str: The response from the agent

        Raises:
            queue.Empty: If no response is received within timeout
            RuntimeError: If the process is not alive
        """
        if not self.is_alive():
            raise RuntimeError(f"Process {self._input_config.name} is not alive")

        self.logger.debug(
            "Sending message to process %s (PID: %d): %s",
            self._input_config.name,
            self.proc.pid,
            message,
        )
        self.input_q.put(message)

        try:
            response = cast(str, self.output_q.get(timeout=timeout))
            self.logger.debug(
                "Received response from process %s (PID: %d)",
                self._input_config.name,
                self.proc.pid,
            )
            return response
        except queue.Empty:
            raise queue.Empty(
                f"No response received from process {self._input_config.name} within {timeout} seconds"
            )

    def kill(self) -> None:
        """Stop the agent process."""
        self.logger.info(
            "Killing agent process %s (PID: %d)", self._input_config.name, self.proc.pid
        )
        self.input_q.put("__EXIT__")
        self.proc.join()
        self.logger.info("Agent process %s terminated", self._input_config.name)

    def is_alive(self) -> bool:
        is_alive = self.proc.is_alive()
        self.logger.debug(
            "Process %s (PID: %d) alive status: %s",
            self._input_config.name,
            self.proc.pid,
            is_alive,
        )
        return is_alive
