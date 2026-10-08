"""
WATERSHIELD Data Contracts & Temporal Leakage Guards
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/03_SCIENTIFIC_SPEC.md §1, §2

Defines immutable data contracts governing:
1. Temporal partitioning: July + August (Historical) vs September (Hidden Future Evaluation).
2. Feature exclusions: 'Use Based Class' strictly barred from policy features.
3. Cohort partitioning: 172 River Primary Cohort vs 222 Network Stations.
4. Strict anti-leakage runtime assertion guards.
"""

from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Any, Union, Optional
import pandas as pd

from src.config import DEFAULT_CONFIG
from src.utils.errors import LeakageViolationError, DataIntegrityError
from src.utils.logger import get_logger

logger = get_logger("data.contracts")


@dataclass(frozen=True)
class TemporalPartitionContract:
    """Immutable contract governing temporal replay data availability."""
    historical_months: Tuple[str, ...] = ("July 2025", "August 2025")
    hidden_future_month: str = "September 2025"
    excluded_parameters: Tuple[str, ...] = ("Use Based Class",)
    primary_cohort_size: int = 172
    network_size: int = 222


DEFAULT_TEMPORAL_CONTRACT = TemporalPartitionContract()


def assert_no_future_data_access(
    data_or_context: Union[pd.DataFrame, Dict[str, Any], List[str], str],
    operation_context: str = "policy_construction"
) -> None:
    """
    CRITICAL ANTI-LEAKAGE GUARD:
    Asserts that September future data or references are NOT accessed or present
    in any policy construction, ranking, normalization, or feature extraction context.

    Raises:
        LeakageViolationError: If September future data is detected.
    """
    future_month_keywords = ["september", "sep_2025", "sept_2025", "09/2025", "2025-09"]

    if isinstance(data_or_context, str):
        val_lower = data_or_context.lower()
        for kw in future_month_keywords:
            if kw in val_lower:
                raise LeakageViolationError(
                    f"Temporal leakage detected in {operation_context}! "
                    f"Forbidden future data identifier '{data_or_context}' accessed.",
                    details="September 2025 observations must remain strictly hidden during policy construction."
                )

    elif isinstance(data_or_context, list):
        for item in data_or_context:
            assert_no_future_data_access(item, operation_context=operation_context)

    elif isinstance(data_or_context, dict):
        for k in data_or_context.keys():
            assert_no_future_data_access(str(k), operation_context=operation_context)

    elif isinstance(data_or_context, pd.DataFrame):
        # Check column names
        for col in data_or_context.columns:
            for kw in future_month_keywords:
                if kw in str(col).lower():
                    raise LeakageViolationError(
                        f"Temporal leakage detected in DataFrame columns during {operation_context}! Column: '{col}'",
                        details="Future evaluation data must not exist in policy feature DataFrame."
                    )
        # Check 'Month' column values if present
        if "Month" in data_or_context.columns:
            months_present = data_or_context["Month"].astype(str).str.lower().unique()
            for m in months_present:
                for kw in future_month_keywords:
                    if kw in m:
                        raise LeakageViolationError(
                            f"Temporal leakage detected: DataFrame contains '{m}' rows during {operation_context}!",
                            details="Only historical months (July, August) may be provided to policy constructors."
                        )


def assert_no_excluded_features(
    feature_names: Union[List[str], Tuple[str, ...], pd.Index],
    operation_context: str = "policy_feature_selection"
) -> None:
    """
    Asserts that unstable features like 'Use Based Class' are NOT included in policy features.

    Raises:
        DataIntegrityError: If 'Use Based Class' is found in feature names.
    """
    excluded = DEFAULT_CONFIG.dataset.excluded_parameters
    for feat in feature_names:
        for exc in excluded:
            if str(feat).strip().lower() == exc.lower():
                raise DataIntegrityError(
                    f"Illegal feature '{feat}' detected in {operation_context}!",
                    details=f"Features in {excluded} are unstable across months and strictly barred from policy scoring."
                )


@dataclass
class ProcessedDatasetFoundation:
    """Container for verified processed datasets generated in Phase 2."""
    recurring_222_df: pd.DataFrame
    river_172_df: pd.DataFrame
    historical_state_df: pd.DataFrame  # July + August observations for the 172 river cohort
    hidden_future_df: pd.DataFrame     # September observations for the 172 river cohort (hidden)
    recurring_codes: List[str]
    river_codes: List[str]
    contract: TemporalPartitionContract = field(default_factory=TemporalPartitionContract)

    def validate_isolation(self) -> bool:
        """Verifies that historical state contains NO September records and NO Use Based Class."""
        assert_no_future_data_access(self.historical_state_df, "ProcessedDatasetFoundation.validate_isolation")
        assert_no_excluded_features(self.historical_state_df.columns, "ProcessedDatasetFoundation.validate_isolation")
        return True
