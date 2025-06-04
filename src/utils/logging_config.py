# Create new file: src/utils/logging_config.py
import logging


def setup_logger(name: str, level: int | None = None) -> logging.Logger:
    """Create and configure a logger instance for the given module.

    Sets up a logger with consistent formatting and configuration options
    across the application. The logging level is determined in this order:
    1. Level parameter if provided
    2. LOG_LEVEL environment variable
    3. Level from config file
    4. Default to INFO if none of the above are set

    Args:
        name: The name of the module (typically __name__).
        level: Optional override for the logging level.

    Returns:
        A configured logger instance.

    """
    logger = logging.getLogger(name)

    # Only add handler if the logger doesn't already have one
    if not logger.handlers:
        handler = logging.StreamHandler()
        
        # Get format from config if available
        try:
            from src.config.config_manager import get_config_manager
            config = get_config_manager()
            if hasattr(config, 'logging') and hasattr(config.logging, 'format'):
                format_str = config.logging.format
            else:
                format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        except Exception:
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            
        formatter = logging.Formatter(format_str)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Determine logging level
    if level is not None:
        log_level = level
    else:
        import os
        env_level = os.getenv('LOG_LEVEL', '').upper()
        if env_level and hasattr(logging, env_level):
            log_level = getattr(logging, env_level)
        else:
            try:
                from src.config.config_manager import get_config_manager
                config = get_config_manager()
                if hasattr(config, 'logging') and hasattr(config.logging, 'level'):
                    log_level = getattr(logging, config.logging.level.upper())
                else:
                    log_level = logging.INFO
            except Exception:
                log_level = logging.INFO

    logger.setLevel(log_level)
    return logger
