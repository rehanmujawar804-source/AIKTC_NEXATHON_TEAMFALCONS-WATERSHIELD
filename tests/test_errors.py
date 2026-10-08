"""
Unit Tests for Custom Exception Hierarchy
Traceability: src/utils/errors.py
"""

import unittest
from src.utils.errors import (
    WatershieldError,
    ConfigurationError,
    DataIntegrityError,
    LeakageViolationError,
    MissingArtifactError,
    BudgetConstraintError,
    PolicyError,
    ReplayError,
    ValidationError,
    StressTestError,
    DecisionError,
)


class TestErrors(unittest.TestCase):
    """Verifies that all domain exceptions derive from WatershieldError."""

    def test_inheritance(self):
        exception_classes = [
            ConfigurationError,
            DataIntegrityError,
            LeakageViolationError,
            MissingArtifactError,
            BudgetConstraintError,
            PolicyError,
            ReplayError,
            ValidationError,
            StressTestError,
            DecisionError,
        ]
        for exc_cls in exception_classes:
            with self.subTest(cls=exc_cls):
                self.assertTrue(issubclass(exc_cls, WatershieldError))

    def test_error_message_formatting(self):
        err = WatershieldError("Primary error message")
        self.assertEqual(str(err), "Primary error message")

        err_with_details = WatershieldError("Base error", details="Code 404")
        self.assertIn("Base error", str(err_with_details))
        self.assertIn("Code 404", str(err_with_details))


if __name__ == "__main__":
    unittest.main()
