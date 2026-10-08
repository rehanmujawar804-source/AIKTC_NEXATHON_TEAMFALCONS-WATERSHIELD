"""
WATERSHIELD Historical State & Scaling Feature Module
Traceability: DOCS/03_SCIENTIFIC_SPEC.md §3, DOCS/04_ARCHITECTURE.md §3.2

Computes historical cross-station scale parameters (mu_p_hist, sigma_p_hist)
using strictly July and August observations.
ENFORCES ANTI-LEAKAGE INVARIANT: September future observations are strictly forbidden.
"""

from typing import Dict, Tuple, List
import pandas as pd


class FeatureEngine:
    """Prepares historical feature matrices and scale factors without future leakage."""

    def compute_historical_scales(
        self, historical_df: pd.DataFrame, parameters: List[str]
    ) -> Dict[str, Tuple[float, float]]:
        """
        Computes sample mean and standard deviation for each parameter
        across all stations in July and August.

        Implementation scheduled for Phase 3 (Data Pipeline).
        """
        raise NotImplementedError(
            "FeatureEngine.compute_historical_scales is scheduled for Phase 3 (Data Pipeline)."
        )
