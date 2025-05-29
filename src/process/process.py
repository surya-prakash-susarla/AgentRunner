from multiprocessing import Process, Queue, current_process
from src.runner.agent_runner import AgentRunner
from src.runner.gemini_runner import GeminiRunner
from typing import Optional
from src.utils.logging_config import setup_logger
import asyncio
import logging
import os


from src.config.config_manager import RunnerType
from src.runner.runner_generator import generate_runner


class AgentProcess:
    def __init__(self, name: str, instruction: str, child_type: RunnerType):
        self.name = name
        self.input_q = Queue()
        self.output_q = Queue()
        self.instruction = instruction
        self.child_type = child_type
        self.logger = setup_logger(__name__, logging.INFO)
        self.logger.info("Initializing agent process %s", name)

        # Launch the process
        self.proc = Process(
            target=self._run_agent,
            args=(self.input_q, self.output_q, self.child_type, self.instruction),
            daemon=True,
        )
        self.proc.start()

    @staticmethod
    def _run_agent(
        input_q: Queue, output_q: Queue, child_type: RunnerType, instruction: str
    ):
        """Run loop for the child agent."""

        proc = current_process()
        logger = setup_logger(f"{__name__}.{proc.name}", logging.INFO)
        logger.info("Starting agent process. PID: %d, Name: %s", os.getpid(), proc.name)

        runner = None
        try:
            # TODO: Replace by creating an actual runner here.
            # Create runner inside the child process
            runner = generate_runner(type=child_type, instruction=instruction)

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
