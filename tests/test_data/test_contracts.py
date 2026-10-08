"""
WATERSHIELD Phase 2 Tests: Data Contracts & Leakage Prevention Guards
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/03_SCIENTIFIC_SPEC.md §1
"""

import unittest
import pandas as pd

from src.data.contracts import (
    assert_no_future_data_access,
    assert_no_excluded_features,
    TemporalPartitionContract,
    DEFAULT_TEMPORAL_CONTRACT
)
from src.utils.errors import LeakageViolationError, DataIntegrityError


class TestDataContractsAndLeakage(unittest.TestCase):
    """Verifies that future September data and excluded features are strictly blocked."""

    def test_default_temporal_contract(self):
        """Asserts contract specifies July+August as historical and September as hidden future."""
        contract = DEFAULT_TEMPORAL_CONTRACT
        self.assertEqual(contract.historical_months, ("July 2025", "August 2025"))
        self.assertEqual(contract.hidden_future_month, "September 2025")
        self.assertEqual(contract.primary_cohort_size, 172)
        self.assertEqual(contract.network_size, 222)
        self.assertIn("Use Based Class", contract.excluded_parameters)

    def test_leakage_guard_string_detection(self):
        """Asserts string references to September trigger LeakageViolationError."""
        with self.assertRaises(LeakageViolationError):
            assert_no_future_data_access("September 2025", operation_context="test_policy")

        with self.assertRaises(LeakageViolationError):
            assert_no_future_data_access("NWMP_September2025_MPCB_0.csv", operation_context="test_policy")

    def test_leakage_guard_dataframe_columns(self):
        """Asserts DataFrames with September column headers trigger LeakageViolationError."""
        leaky_df = pd.DataFrame({"STN Code": ["101"], "BOD_September_2025": [4.5]})
        with self.assertRaises(LeakageViolationError):
            assert_no_future_data_access(leaky_df, operation_context="policy_scoring")

    def test_leakage_guard_dataframe_rows(self):
        """Asserts DataFrames with September month rows trigger LeakageViolationError."""
        leaky_df = pd.DataFrame({"STN Code": ["101"], "Month": ["September 2025"], "BOD": [4.5]})
        with self.assertRaises(LeakageViolationError):
            assert_no_future_data_access(leaky_df, operation_context="policy_scoring")

    def test_leakage_guard_valid_historical_dataframe(self):
        """Asserts DataFrames with only July/August rows pass without error."""
        clean_df = pd.DataFrame({"STN Code": ["101", "102"], "Month": ["July 2025", "August 2025"], "BOD": [3.2, 4.1]})
        # Should not raise
        assert_no_future_data_access(clean_df, operation_context="policy_scoring")

    def test_excluded_features_guard(self):
        """Asserts that 'Use Based Class' raises DataIntegrityError when present in features."""
        with self.assertRaises(DataIntegrityError):
            assert_no_excluded_features(["BOD", "pH", "Use Based Class"], "policy_features")

        # Clean features pass without error
        assert_no_excluded_features(["BOD", "pH", "Conductivity"], "policy_features")


if __name__ == "__main__":
    unittest.main()
