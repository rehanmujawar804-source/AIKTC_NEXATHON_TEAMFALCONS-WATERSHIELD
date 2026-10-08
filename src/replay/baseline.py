"""
WATERSHIELD Persistence Baseline Reconstruction Model
Traceability: DOCS/03_SCIENTIFIC_SPEC.md §5.1, DOCS/04_ARCHITECTURE.md §3.4

Implements the persistence baseline:
- If station i in S_B (sampled): y_hat_i,p^Sep = y_i,p^Sep (revealed observation, zero residual error)
- If station i not in S_B (unsampled): y_hat_i,p^Sep = y_i,p^Aug (prior month observation retained)
"""

from typing import List, Dict
import pandas as pd


class BaselineReconstructor:
    """Reconstructs full network state using sampled observations and persistence fallback."""

    def reconstruct_network(
        self,
        selected_stations: List[str],
        august_state: pd.DataFrame,
        september_ground_truth: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Builds the reconstructed September state.

        Implementation scheduled for Phase 5 (Temporal Replay Engine).
        """
        raise NotImplementedError(
            "BaselineReconstructor.reconstruct_network is scheduled for Phase 5 (Temporal Replay Engine)."
        )
