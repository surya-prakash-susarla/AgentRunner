import asyncio
import atexit
import logging
import signal
from typing import Optional

from src.utils.logging_config import setup_logger

logger = setup_logger(__name__, logging.INFO)


class ProcessCleanup:
    def __init__(self):
        self._runner = None
        self._registered = False

    def register_runner(self, runner) -> None:
        """Register the main runner instance for cleanup.

        Args:
            runner: The main GeminiRunner instance
        """
        self._runner = runner
        if not self._registered:
            self._setup_cleanup_handlers()
            self._registered = True

    def cleanup_all_processes(self) -> None:
        """Cleanup function to ensure all child processes are terminated."""
        from src.process.replica_manager import get_replica_manager

        logger.info("Running cleanup for all processes")

        # Cleanup the main runner first
        if self._runner:
            try:
                asyncio.run(self._runner.cleanup())
                logger.info("Main runner cleanup completed")
            except Exception as e:
                logger.error("Error cleaning up main runner: %s", str(e))

        # Get the replica manager and cleanup all child processes
        try:
            replica_manager = get_replica_manager()
            for name, process in list(replica_manager.children.items()):
                try:
                    if process.is_alive():
                        logger.info("Terminating child process '%s'", name)
                        process.kill()
                        logger.info("Successfully terminated child process '%s'", name)
                except Exception as e:
                    logger.error(
                        "Error terminating child process '%s': %s", name, str(e)
                    )
            logger.info("All child processes cleanup completed")
        except Exception as e:
            logger.error("Error during replica manager cleanup: %s", str(e))

    def _setup_cleanup_handlers(self) -> None:
        """Set up cleanup handlers for various exit scenarios."""
        atexit.register(self.cleanup_all_processes)
        signal.signal(signal.SIGTERM, lambda sig, frame: self.cleanup_all_processes())
        signal.signal(signal.SIGINT, lambda sig, frame: self.cleanup_all_processes())
        logger.debug("Cleanup handlers registered")


# Global cleanup instance
cleanup_manager = ProcessCleanup()
