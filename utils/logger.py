"""
Logging configuration for Soplos Plymouth Manager.
"""

import logging
import sys
from pathlib import Path
from utils.constants import LOG_FILE, LOG_FORMAT, LOG_LEVEL

def setup_logger(name: str = "plymouth-manager") -> logging.Logger:
    """
    Set up and configure the application logger.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    try:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as e:
        logger.warning(f"Could not create log file: {e}")

    return logger

# Global logger instance
logger = setup_logger()