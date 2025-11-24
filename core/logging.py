"""
Core logging module for application-wide logging configuration.

This module provides centralized logging setup using loguru and exports
a module-level logger instance for consistent logging across the application.
"""

import sys
from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    """Configure loguru logging for the application.

    Sets up loguru with a standard format and console output.
    This function should be called once at application startup.

    Args:
        level: Logging level as string (default: "INFO")
              Valid values: "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
    """
    # Remove default handler
    logger.remove()

    # Add custom handler with specified format
    logger.add(
        sys.stdout,
        format="[{time}] {level} - {name} - {message}",
        level=level,
    )


# Export loguru's logger instance for easy importing
# Other modules can use: from core.logging import logger
__all__ = ["logger", "setup_logging"]
