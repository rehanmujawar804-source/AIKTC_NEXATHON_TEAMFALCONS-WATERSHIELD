"""
Unit Tests for Base Policy Interface
Traceability: src/policies/base.py
"""

import unittest
from typing import List, Optional, Any

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

from src.policies.base import BasePolicy, PolicyResult
from src.utils.errors import BudgetConstraintError


class ConcreteDummyPolicy(BasePolicy):
    """Minimal concrete implementation to test BasePolicy validation logic."""

    def select_stations(
        self,
        historical_state: Any,
        budget: int,
        candidate_stations: Optional[List[str]] = None,
        seed: int = 42,
        **kwargs: Any,
    ) -> PolicyResult:
        candidates = candidate_stations or ["S1", "S2", "S3"]
        self.validate_budget(budget, len(candidates))
        return PolicyResult(
            policy_name=self.name,
            budget=budget,
            selected_stations=candidates[:budget],
        )


class TestBasePolicy(unittest.TestCase):
    """Verifies interface contract and budget constraint enforcement."""

    def test_cannot_instantiate_abstract_base_policy(self):
        with self.assertRaises(TypeError):
            BasePolicy("AbstractTest")  # type: ignore

    def test_valid_budget(self):
        policy = ConcreteDummyPolicy("TestPolicy")
        result = policy.select_stations(None, budget=2, candidate_stations=["A", "B", "C"])
        self.assertEqual(result.budget, 2)
        self.assertEqual(result.selected_stations, ["A", "B"])

    def test_invalid_negative_or_zero_budget(self):
        policy = ConcreteDummyPolicy("TestPolicy")
        with self.assertRaises(BudgetConstraintError):
            policy.select_stations(None, budget=0, candidate_stations=["A", "B"])
        with self.assertRaises(BudgetConstraintError):
            policy.select_stations(None, budget=-5, candidate_stations=["A", "B"])

    def test_budget_exceeds_available_stations(self):
        policy = ConcreteDummyPolicy("TestPolicy")
        with self.assertRaises(BudgetConstraintError):
            policy.select_stations(None, budget=10, candidate_stations=["A", "B"])


if __name__ == "__main__":
    unittest.main()
