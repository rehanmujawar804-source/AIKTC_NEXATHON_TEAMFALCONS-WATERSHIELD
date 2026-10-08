"""
WATERSHIELD Evaluation Metrics Module
Traceability: DOCS/03_SCIENTIFIC_SPEC.md §5.3, §5.4

Calculates:
1. Standardized Network Residual Error (e_pi):
   Aggregated standardized absolute residuals across all N stations and P parameters,
   scaled strictly by pre-September historical scale factors (sigma_p_hist).
2. Headline Improvement vs Random (%):
   Delta_pi = ((e_random - e_pi) / e_random) * 100%
"""

from typing import Dict, Tuple
import pandas as pd


class NetworkResidualMetric:
    """Calculates standardized residual error and percentage improvement over random."""

    def compute_network_residual_error(
        self,
        reconstructed_state: pd.DataFrame,
        september_ground_truth: pd.DataFrame,
        historical_scales: Dict[str, Tuple[float, float]],
    ) -> float:
        """
        Computes network-wide standardized residual error.

        Implementation scheduled for Phase 5 (Temporal Replay Engine).
        """
        raise NotImplementedError(
            "NetworkResidualMetric.compute_network_residual_error is scheduled for Phase 5."
        )

    def compute_improvement_pct(
        self, policy_error: float, random_baseline_error: float
    ) -> float:
        """Computes ((random_error - policy_error) / random_error) * 100%."""
        if random_baseline_error <= 0:
            return 0.0
        return ((random_baseline_error - policy_error) / random_baseline_error) * 100.0
