from multiprocessing import Process, Queue, current_process
from runner.agent_runner import AgentRunner
from typing import Optional
from utils.logging_config import setup_logger
import asyncio
import logging
import os


class AgentProcess:
    def __init__(self, name: str, runner: AgentRunner):
        self.name = name
        self.input_q = Queue()
        self.output_q = Queue()
        self.runner = runner
        self.logger = setup_logger(__name__, logging.INFO)
        self.logger.info("Initializing agent process %s", name)

        # Launch the process
        self.proc = Process(
            target=self._run_agent,
            args=(self.input_q, self.output_q, self.runner),
            daemon=True,
        )
        self.proc.start()

    @staticmethod
    def _run_agent(input_q: Queue, output_q: Queue, runner: AgentRunner):
        """Run loop for the child agent."""

        proc = current_process()
        logger = setup_logger(f"{__name__}.{proc.name}", logging.INFO)
        logger.info("Starting agent process. PID: %d, Name: %s", os.getpid(), proc.name)

        try:
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
                    response = f"[Agent Error]: {str(e)}"
                output_q.put(response)
        finally:
            # Ensure cleanup runs when the process exits
            logger.info("Running cleanup for process %d", os.getpid())
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(runner.cleanup())
            except Exception as e:
                logger.error("Error during cleanup: %s", str(e))
            finally:
                loop.close()

    def ask(self, message: str, timeout: Optional[float] = None) -> str:
        """Send message to the agent and get the response."""
        self.logger.debug(
            "Sending message to process %s (PID: %d): %s",
            self.name,
            self.proc.pid,
            message,
        )
        self.input_q.put(message)
        response = self.output_q.get(timeout=timeout)
        self.logger.debug(
            "Received response from process %s (PID: %d)", self.name, self.proc.pid
        )
        return response

    def kill(self):
        """Stop the agent process."""
        self.logger.info("Killing agent process %s (PID: %d)", self.name, self.proc.pid)
        self.input_q.put("__EXIT__")
        self.proc.join()
        self.logger.info("Agent process %s terminated", self.name)

    def is_alive(self) -> bool:
        is_alive = self.proc.is_alive()
        self.logger.debug(
            "Process %s (PID: %d) alive status: %s", self.name, self.proc.pid, is_alive
        )
        return is_alive
