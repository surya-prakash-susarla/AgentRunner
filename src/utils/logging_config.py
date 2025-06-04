# Create new file: src/utils/logging_config.py
import logging


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Creates and configures a logger instance for the given module

    Args:
        name: The name of the module (typically __name__)
        level: The logging level to use

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handler if the logger doesn't already have one
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger
