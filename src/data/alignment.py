"""
WATERSHIELD Station Alignment & Cohort Stratification Module
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/02_REQUIREMENTS.md FR-DATA-03, FR-DATA-04

Verifies the 222 recurring stations across July, August, and September 2025.
Extracts and isolates the primary scientific evaluation cohort of 172 river stations.
"""

from typing import Dict, Tuple, List
import pandas as pd


class StationAligner:
    """Aligns monthly datasets across recurring station codes and partitions cohorts."""

    def extract_recurring_stations(
        self, monthly_dfs: Dict[str, pd.DataFrame]
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Intersects station codes across all three months.
        Asserts that exactly 222 unique station codes recur across July, August, September.

        Implementation scheduled for Phase 3 (Data Pipeline).
        """
        raise NotImplementedError(
            "StationAligner.extract_recurring_stations is scheduled for Phase 3 (Data Pipeline)."
        )

    def filter_river_cohort(
        self, recurring_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Filters recurring stations to the 172-station river cohort (Type Water Body == 'RIVER').
        Asserts that exactly 172 river stations are present.

        Implementation scheduled for Phase 3 (Data Pipeline).
        """
        raise NotImplementedError(
            "StationAligner.filter_river_cohort is scheduled for Phase 3 (Data Pipeline)."
        )
