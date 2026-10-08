"""
Unit Tests for Central Configuration Module
Traceability: src/config.py
"""

import unittest
from pathlib import Path
from src.config import DEFAULT_CONFIG, AppConfig


class TestConfiguration(unittest.TestCase):
    """Verifies that all scientific constants and invariants match specification."""

    def test_default_config_instance(self):
        self.assertIsInstance(DEFAULT_CONFIG, AppConfig)
        self.assertEqual(DEFAULT_CONFIG.mode, "DEMO")

    def test_station_cohort_counts(self):
        # Invariant: exactly 222 recurring stations across 3 months
        self.assertEqual(DEFAULT_CONFIG.dataset.total_recurring_stations, 222)
        # Invariant: primary evaluation cohort is exactly 172 river stations
        self.assertEqual(DEFAULT_CONFIG.dataset.primary_river_cohort_stations, 172)
        # Invariant: 50 non-river secondary stations
        self.assertEqual(DEFAULT_CONFIG.dataset.secondary_non_river_stations, 50)
        self.assertEqual(
            DEFAULT_CONFIG.dataset.primary_river_cohort_stations
            + DEFAULT_CONFIG.dataset.secondary_non_river_stations,
            222,
        )

    def test_core_parameters(self):
        # Invariant: exactly 12 core parameters
        self.assertEqual(len(DEFAULT_CONFIG.dataset.core_parameters), 12)
        self.assertIn("Dissolved O2", DEFAULT_CONFIG.dataset.core_parameters)
        self.assertIn("pH", DEFAULT_CONFIG.dataset.core_parameters)
        self.assertIn("BOD", DEFAULT_CONFIG.dataset.core_parameters)
        self.assertIn("Total Coliform", DEFAULT_CONFIG.dataset.core_parameters)

    def test_excluded_feature(self):
        # Invariant: 'Use Based Class' must be excluded
        self.assertIn("Use Based Class", DEFAULT_CONFIG.dataset.excluded_parameters)

    def test_budgets(self):
        # Invariant: Approved budgets are B in {10, 20, 40}
        self.assertEqual(DEFAULT_CONFIG.policy.budgets, (10, 20, 40))

    def test_policy_arena(self):
        # Invariant: Exactly 5 candidate policies
        self.assertEqual(len(DEFAULT_CONFIG.policy.policy_names), 5)
        self.assertEqual(
            DEFAULT_CONFIG.policy.policy_names,
            ("Random", "Risk", "Change", "Coverage", "Risk_x_Change"),
        )

    def test_validation_replicates(self):
        # Invariant: Exactly 3,000 district-matched randomization portfolios
        self.assertEqual(
            DEFAULT_CONFIG.validation.district_randomization_replicates, 3000
        )
        # Invariant: 4 holdout folds of 3 parameters each
        self.assertEqual(len(DEFAULT_CONFIG.validation.holdout_folds), 4)
        for fold in DEFAULT_CONFIG.validation.holdout_folds:
            self.assertEqual(len(fold), 3)


if __name__ == "__main__":
    unittest.main()
