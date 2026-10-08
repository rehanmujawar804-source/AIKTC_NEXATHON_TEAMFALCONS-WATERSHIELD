"""
WATERSHIELD Policy Arena Package
Contains the BasePolicy contract and the 5 approved candidate policy classes.
"""

from src.policies.base import BasePolicy, PolicyResult
from src.policies.random_policy import RandomPolicy
from src.policies.risk_policy import RiskPolicy
from src.policies.change_policy import ChangePolicy
from src.policies.coverage_policy import CoveragePolicy
from src.policies.risk_change_policy import RiskChangePolicy

__all__ = [
    "BasePolicy",
    "PolicyResult",
    "RandomPolicy",
    "RiskPolicy",
    "ChangePolicy",
    "CoveragePolicy",
    "RiskChangePolicy",
]
