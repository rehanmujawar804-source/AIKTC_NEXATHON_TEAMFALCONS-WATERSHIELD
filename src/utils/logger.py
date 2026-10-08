"""
WATERSHIELD Structured Logging Module
Traceability: DOCS/04_ARCHITECTURE.md §7

Provides consistent, development-friendly, and audit-safe logging across all modules.
Logs must never expose secrets, personal data, or hardcoded fake scientific outputs.
"""

import logging
import sys
from typing import Optional


DEFAULT_LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str = "watershield",
    level: int = logging.INFO,
    run_id: Optional[str] = None
) -> logging.Logger:
    """
    Initializes and returns a configured logger instance.

    Args:
        name: Logger hierarchy identifier (e.g. 'watershield.data').
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
        run_id: Optional experiment execution identifier for audit provenance.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if logger was already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        if run_id:
            formatter = logging.Formatter(
                f"[%(asctime)s] [%(levelname)s] [%(name)s] [run_id={run_id}]: %(message)s",
                datefmt=DATE_FORMAT,
            )
        else:
            formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DATE_FORMAT)

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(module_name: str) -> logging.Logger:
    """Convenience helper to obtain a namespaced child logger."""
    return logging.getLogger(f"watershield.{module_name}")
