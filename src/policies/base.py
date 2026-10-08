"""
WATERSHIELD Policy Arena Base Interface
Traceability: DOCS/04_ARCHITECTURE.md §3.3, DOCS/06_IMPLEMENTATION.md §2.2

Defines the abstract interface for all candidate station-selection policies.
All policies receive ONLY historical state (July + August) and must NEVER
receive, query, or infer from hidden future observations (September).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

try:
    import pandas as pd
except ImportError:
    pd = Any  # type: ignore

from src.utils.errors import BudgetConstraintError, LeakageViolationError


@dataclass
class PolicyResult:
    """
    Standardized result contract returned by any BasePolicy implementation.
    """
    policy_name: str
    budget: int
    selected_stations: List[str]
    scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePolicy(ABC):
    """
    Abstract Base Class enforcing the uniform station-selection policy contract.
    """

    def __init__(self, name: str):
        self.name = name

    def validate_budget(self, budget: int, max_available: int) -> None:
        """
        Validates that budget is positive and does not exceed available candidate stations.
        """
        if budget <= 0:
            raise BudgetConstraintError(f"Budget must be positive, got {budget}")
        if budget > max_available:
            raise BudgetConstraintError(
                f"Budget ({budget}) cannot exceed available candidate stations ({max_available})"
            )

    @abstractmethod
    def select_stations(
        self,
        historical_state: pd.DataFrame,
        budget: int,
        candidate_stations: Optional[List[str]] = None,
        seed: int = 42,
        **kwargs: Any,
    ) -> PolicyResult:
        """
        Selects exactly `budget` stations using historical data ONLY.

        Args:
            historical_state: Cleaned observations from July + August.
            budget: Number of stations to sample (e.g. 10, 20, 40).
            candidate_stations: Optional subset of allowed station codes (e.g. 172 river cohort).
            seed: Explicit random seed for deterministic reproducibility.
            **kwargs: Policy-specific parameters.

        Returns:
            PolicyResult containing list of chosen station codes and scores.

        Raises:
            LeakageViolationError: If future September data is passed into historical_state.
            BudgetConstraintError: If budget is invalid or unenforceable.
        """
        pass
