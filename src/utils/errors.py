"""
WATERSHIELD Domain Exception Hierarchy
Traceability: DOCS/04_ARCHITECTURE.md §5, DOCS/06_IMPLEMENTATION.md §2.2

Scientific failures must never be silently swallowed or substituted with fabricated results.
All exceptions derive from WatershieldError to ensure explicit, structured error handling.
"""


class WatershieldError(Exception):
    """Base exception for all WATERSHIELD domain and pipeline errors."""
    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(WatershieldError):
    """Raised when application configuration or hyperparameters are invalid."""
    pass


class DataIntegrityError(WatershieldError):
    """Raised when data fails schema, recurrence, or cohort invariants."""
    pass


class LeakageViolationError(WatershieldError):
    """
    CRITICAL: Raised when September future observations or statistics
    leak into policy scoring, feature normalization, or station selection.
    """
    pass


class MissingArtifactError(WatershieldError):
    """Raised when precomputed result artifacts in results/ are missing in Demo Mode."""
    pass


class BudgetConstraintError(WatershieldError):
    """Raised when sampling budget B is invalid (e.g., B not in {10, 20, 40} or B > N)."""
    pass


class PolicyError(WatershieldError):
    """Raised when policy construction or station selection fails."""
    pass


class ReplayError(WatershieldError):
    """Raised when temporal replay or baseline reconstruction encounters an invalid state."""
    pass


class ValidationError(WatershieldError):
    """Raised when cross-parameter holdout or matched randomization fails to execute."""
    pass


class StressTestError(WatershieldError):
    """Raised when stress testing grid parameters or Monte Carlo simulations fail."""
    pass


class DecisionError(WatershieldError):
    """Raised when the reliability decision gate encounters invalid evidence inputs."""
    pass
