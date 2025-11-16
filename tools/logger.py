"""
Logging utilities for the Claude conversation analysis tools.

This module provides centralized logging configuration with proper error handling
and verbose output for debugging purposes.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from config import LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up and configure a logger with consistent formatting.

    Args:
        name: Name of the logger (typically __name__ from calling module).
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Defaults to LOG_LEVEL from config.
        log_file: Optional path to log file. If provided, logs to both file and console.

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        ValueError: If invalid log level is provided.
        IOError: If log file cannot be created or written to.
    """
    # Validate parameters
    if not name:
        raise ValueError("Logger name cannot be empty")

    if level is None:
        level = LOG_LEVEL

    # Validate log level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            # Ensure parent directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"Logging to file: {log_file}")
        except (OSError, IOError) as e:
            logger.error(f"Failed to create log file handler: {e}")
            raise IOError(f"Cannot write to log file {log_file}: {e}") from e

    logger.debug(f"Logger '{name}' initialized at {level} level")

    return logger


def log_exception(logger: logging.Logger, exception: Exception, context: str = "") -> None:
    """
    Log an exception with full context and traceback.

    Args:
        logger: Logger instance to use.
        exception: The exception to log.
        context: Additional context about where/why the exception occurred.

    Raises:
        ValueError: If logger is None.
    """
    if logger is None:
        raise ValueError("Logger cannot be None")

    error_msg = f"Exception occurred"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {type(exception).__name__}: {str(exception)}"

    logger.error(error_msg, exc_info=True)


if __name__ == "__main__":
    # Test the logger
    test_logger = setup_logger("test_logger", "DEBUG")
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        log_exception(test_logger, e, "logger test")
