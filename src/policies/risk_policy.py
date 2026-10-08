"""
Policy 2: Risk-First Selection Policy (pi_risk)
Traceability: DOCS/03_SCIENTIFIC_SPEC.md §4.2

Ranks stations by historical water-quality degradation (high BOD, low DO, high coliforms, high COD)
normalized against historical baseline scales (July + August).
"""

from typing import List, Optional, Any

try:
    import pandas as pd
except ImportError:
    pd = Any  # type: ignore

from src.policies.base import BasePolicy, PolicyResult


class RiskPolicy(BasePolicy):
    """Historical water-quality degradation prioritization policy."""

    def __init__(self):
        super().__init__(name="Risk")

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
            "RiskPolicy implementation is scheduled for Phase 4 (Policy Arena)."
        )
