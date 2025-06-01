from multiprocessing import Process, Queue, current_process
from typing import Optional
from src.utils.logging_config import setup_logger
import asyncio
import logging
import os


from src.runner.runner_generator import create_runner
from .agent_process_input import AgentProcessInput


class AgentProcess:
    def __init__(self, input_config: AgentProcessInput):
        self.input_q = Queue()
        self.output_q = Queue()
        self._input_config = input_config
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
    def _run_agent(input_q: Queue, output_q: Queue, input_config: AgentProcessInput):
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
            "Received response from process %s (PID: %d)",
            self._input_config.name,
            self.proc.pid,
        )
        return response

    def kill(self):
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
