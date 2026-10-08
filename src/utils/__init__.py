"""
WATERSHIELD Utilities Package
Exposes core exceptions, logger factory, and cryptographic hashing tools.
"""

from src.utils.errors import (
    WatershieldError,
    ConfigurationError,
    DataIntegrityError,
    LeakageViolationError,
    MissingArtifactError,
    BudgetConstraintError,
    PolicyError,
    ReplayError,
    ValidationError,
    StressTestError,
    DecisionError,
)
from src.utils.logger import setup_logger, get_logger
from src.utils.hashing import (
    compute_file_sha256,
    compute_string_sha256,
    compute_dict_hash,
    verify_file_hash,
)

__all__ = [
    "WatershieldError",
    "ConfigurationError",
    "DataIntegrityError",
    "LeakageViolationError",
    "MissingArtifactError",
    "BudgetConstraintError",
    "PolicyError",
    "ReplayError",
    "ValidationError",
    "StressTestError",
    "DecisionError",
    "setup_logger",
    "get_logger",
    "compute_file_sha256",
    "compute_string_sha256",
    "compute_dict_hash",
    "verify_file_hash",
]
