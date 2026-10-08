"""
WATERSHIELD Central Configuration Module
Traceability: DOCS/04_ARCHITECTURE.md §3.1, DOCS/03_SCIENTIFIC_SPEC.md §1

Encapsulates all system constants, directory paths, budgets, random seeds,
parameter lists, and decision thresholds into typed dataclasses.
No scientific constants or magic numbers should exist outside this module.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Literal


@dataclass(frozen=True)
class PathConfig:
    """Directory and file path locations relative to project root."""
    root_dir: Path = Path(".")
    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")
    reports_dir: Path = Path("data/reports")
    results_dir: Path = Path("results")
    
    # Raw NWMP MPCB files
    july_filename: str = "NWMP_July2025.csv"
    august_filename: str = "NWMP_August2025_MPCB_0.csv"
    september_filename: str = "NWMP_September2025_MPCB_0.csv"
    
    # Processed Parquet artifacts
    recurring_222_parquet: str = "recurring_stations_222.parquet"
    river_172_parquet: str = "river_cohort_172.parquet"
    historical_state_parquet: str = "historical_state_jul_aug.parquet"
    hidden_future_parquet: str = "hidden_future_sep.parquet"


@dataclass(frozen=True)
class DatasetConfig:
    """NWMP dataset definitions, parameters, and cohort boundaries."""
    source_agency: str = "Maharashtra Pollution Control Board (MPCB)"
    data_portal: str = "data.gov.in"
    program_name: str = "National Water Quality Monitoring Programme (NWMP)"
    
    # Temporal Partitioning
    historical_months: Tuple[str, ...] = ("July 2025", "August 2025")
    future_month: str = "September 2025"
    
    # Station Invariants
    total_recurring_stations: int = 222
    primary_river_cohort_stations: int = 172
    secondary_non_river_stations: int = 50
    water_body_river_filter: str = "RIVER"
    
    # 12 Core Evaluated Water-Quality Parameters
    core_parameters: Tuple[str, ...] = (
        "Dissolved O2",
        "pH",
        "BOD",
        "Conductivity",
        "Nitrate N",
        "Fecal Coliform",
        "Total Coliform",
        "Turbidity",
        "COD",
        "Amonia N",
        "Total Dissolved Solids",
        "Phosphate",
    )
    
    # Pollutants where higher values indicate degradation
    pollutant_parameters: Tuple[str, ...] = (
        "BOD",
        "Conductivity",
        "Nitrate N",
        "Fecal Coliform",
        "Total Coliform",
        "Turbidity",
        "COD",
        "Amonia N",
        "Total Dissolved Solids",
        "Phosphate",
    )
    
    # Excluded Feature: unstable classification across months
    excluded_parameters: Tuple[str, ...] = ("Use Based Class",)


@dataclass(frozen=True)
class PolicyConfig:
    """Approved Policy Arena specification and budgets."""
    # Approved Budgets B << N (N = 172)
    budgets: Tuple[int, ...] = (10, 20, 40)
    
    # 5 Approved Policy Identifiers (Uncertainty policy strictly rejected)
    policy_names: Tuple[str, ...] = (
        "Random",
        "Risk",
        "Change",
        "Coverage",
        "Risk_x_Change",
    )
    
    default_seed: int = 42


@dataclass(frozen=True)
class ValidationConfig:
    """Cross-parameter holdout and district-matched randomization settings."""
    # 4-Fold Cross-Parameter Holdout Groups (Folds of 3 parameters)
    holdout_folds: Tuple[Tuple[str, ...], ...] = (
        ("Dissolved O2", "pH", "BOD"),
        ("Conductivity", "Nitrate N", "Fecal Coliform"),
        ("Total Coliform", "Turbidity", "COD"),
        ("Amonia N", "Total Dissolved Solids", "Phosphate"),
    )
    
    # District-matched randomization diagnostics (Empirical tail proportion, NOT p-value)
    district_randomization_replicates: int = 3000
    randomization_seed: int = 42


@dataclass(frozen=True)
class StressConfig:
    """Controlled failure simulation grids (Station loss and missing telemetry)."""
    # Random station dropouts
    station_dropout_rates: Tuple[float, ...] = (0.10, 0.20, 0.30, 0.40, 0.50)
    
    # Input missingness with median imputation
    missing_data_rates: Tuple[float, ...] = (0.10, 0.20, 0.30)
    
    # Monte Carlo replicates for smooth degradation boundaries
    monte_carlo_replicates: int = 200
    stress_seed: int = 42


@dataclass(frozen=True)
class DecisionThresholds:
    """Evidence thresholds for TRUST / CONDITIONAL / ABSTAIN governance."""
    # Minimum nominal improvement over random to consider recommendation
    min_nominal_improvement_pct: float = 3.0
    
    # Policy must achieve positive improvement across all 4 holdout folds
    min_holdout_improvement_pct: float = 0.0
    
    # Empirical diagnostic tail proportion cutoff (q_diag <= 0.05)
    max_diagnostic_tail_proportion: float = 0.05
    
    # Critical stress failure boundary threshold
    strong_operational_limit: float = 0.15
    conditional_operational_limit: float = 0.35


@dataclass
class AppConfig:
    """Root application configuration aggregating all component configs."""
    paths: PathConfig = field(default_factory=PathConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    stress: StressConfig = field(default_factory=StressConfig)
    thresholds: DecisionThresholds = field(default_factory=DecisionThresholds)
    
    # Runtime Mode: DEMO (consumes results/) vs EXPERIMENT (live pipeline run)
    mode: Literal["DEMO", "EXPERIMENT"] = "DEMO"
    
    def get_results_path(self, category: str, filename: str) -> Path:
        """Helper to resolve result artifact file paths."""
        return self.paths.results_dir / category / filename


# Singleton default configuration instance
DEFAULT_CONFIG = AppConfig()
