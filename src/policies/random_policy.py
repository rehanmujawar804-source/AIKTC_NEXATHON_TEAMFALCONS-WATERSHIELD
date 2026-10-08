"""
Policy 1: Uniform Random Baseline Policy (pi_rnd)
Traceability: DOCS/03_SCIENTIFIC_SPEC.md §4.1

Selects a uniform random subset of B stations without replacement given seed s.
Serves as the empirical denominator for all percentage improvement calculations.
"""

from typing import List, Optional, Any

try:
    import pandas as pd
except ImportError:
    pd = Any  # type: ignore

from src.policies.base import BasePolicy, PolicyResult


class RandomPolicy(BasePolicy):
    """Uniform random station selection baseline."""

    def __init__(self):
        super().__init__(name="Random")

    def select_stations(
        self,
        historical_state: pd.DataFrame,
        budget: int,
        candidate_stations: Optional[List[str]] = None,
        seed: int = 42,
        **kwargs: Any,
    ) -> PolicyResult:
        # Implementation scheduled for Phase 4 (Policy Arena)
        raise NotImplementedError(
            "RandomPolicy implementation is scheduled for Phase 4 (Policy Arena)."
        )
