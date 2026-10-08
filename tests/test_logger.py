"""
Unit Tests for Structured Logging Module
Traceability: src/utils/logger.py
"""

import unittest
import logging
from src.utils.logger import setup_logger, get_logger


class TestLogger(unittest.TestCase):
    """Verifies logger configuration and namespace naming."""

    def test_setup_logger_default(self):
        logger = setup_logger("watershield.test", level=logging.DEBUG)
        self.assertEqual(logger.name, "watershield.test")
        self.assertEqual(logger.level, logging.DEBUG)

    def test_get_logger_namespace(self):
        child_logger = get_logger("data.loader")
        self.assertEqual(child_logger.name, "watershield.data.loader")


if __name__ == "__main__":
    unittest.main()
