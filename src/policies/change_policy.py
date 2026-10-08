"""
Policy 3: Temporal Change Selection Policy (pi_chg)
Traceability: DOCS/03_SCIENTIFIC_SPEC.md §4.3

Prioritizes stations exhibiting the largest standardized absolute temporal movement
between July and August across monitored parameters.
"""

from typing import List, Optional, Any

try:
    import pandas as pd
except ImportError:
    pd = Any  # type: ignore

from src.policies.base import BasePolicy, PolicyResult


class ChangePolicy(BasePolicy):
    """Historical temporal volatility/rate-of-change prioritization policy."""

    def __init__(self):
        super().__init__(name="Change")

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
            "ChangePolicy implementation is scheduled for Phase 4 (Policy Arena)."
        )
