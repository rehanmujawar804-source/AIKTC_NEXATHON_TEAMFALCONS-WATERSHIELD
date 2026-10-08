"""
Policy 5: Risk x Change Selection Policy (pi_rxc)
Traceability: DOCS/03_SCIENTIFIC_SPEC.md §4.5

Combines degradation severity (Risk rank) with temporal dynamics (Change rank)
via normalized product scoring: S_i = (rank(R_i)/N) * (rank(C_i)/N).
"""

from typing import List, Optional, Any

try:
    import pandas as pd
except ImportError:
    pd = Any  # type: ignore

from src.policies.base import BasePolicy, PolicyResult


class RiskChangePolicy(BasePolicy):
    """Multiplicative ranking policy combining historical risk and rate-of-change."""

    def __init__(self):
        super().__init__(name="Risk_x_Change")

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
            "RiskChangePolicy implementation is scheduled for Phase 4 (Policy Arena)."
        )
