# 06_IMPLEMENTATION.md — Engineering & Implementation Blueprint

## 1. Directory Structure

The repository must follow this clean, modular structure:

```text
AIKTC_NEXATHON_TEAMFALCONS-WATERSHIELD/
├── AGENTS.md
├── README.md
├── requirements.txt
├── app.py                      # Main Streamlit Application Entrypoint
├── docs/                       # Project Documentation Suite
│   ├── 01_MASTER_PROJECT.md
│   ├── 02_REQUIREMENTS.md
│   ├── 03_SCIENTIFIC_SPEC.md
│   ├── 04_ARCHITECTURE.md
│   ├── 05_PRODUCT_UI_UX.md
│   ├── 06_IMPLEMENTATION.md
│   └── 07_ROADMAP.md
├── data/
│   ├── raw/                    # Immutable Raw MPCB NWMP CSV files
│   │   ├── NWMP_July2025.csv
│   │   ├── NWMP_August2025_MPCB_0.csv
│   │   └── NWMP_September2025_MPCB_0.csv
│   └── processed/              # Cleaned & Aligned Parquet datasets
│       ├── recurring_stations_222.parquet
│       ├── river_cohort_172.parquet
│       └── historical_state.parquet
├── src/
│   ├── __init__.py
│   ├── config.py               # Centralized typed configuration
│   ├── data/                   # Data Ingestion & State Pipeline
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── cleaning.py
│   │   ├── validation.py
│   │   ├── alignment.py
│   │   └── features.py
│   ├── policies/               # Policy Arena Implementations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── random_policy.py
│   │   ├── risk_policy.py
│   │   ├── change_policy.py
│   │   ├── coverage_policy.py
│   │   └── risk_change_policy.py
│   ├── replay/                 # Temporal Replay & Leakage Barrier
│   │   ├── __init__.py
│   │   ├── baseline.py
│   │   ├── temporal_replay.py
│   │   └── metrics.py
│   ├── validation/             # Multi-Layer Validation Engine
│   │   ├── __init__.py
│   │   ├── parameter_holdout.py
│   │   ├── district_randomization.py
│   │   └── sensitivity.py
│   ├── stress/                 # Controlled Failure Testing
│   │   ├── __init__.py
│   │   ├── station_failure.py
│   │   └── missing_data.py
│   ├── decision/               # Decision Gate & Reliability Engine
│   │   ├── __init__.py
│   │   ├── reliability.py
│   │   ├── failure_boundary.py
│   │   └── recommendation.py
│   └── ui/                     # Modular UI View Components
│       ├── __init__.py
│       ├── components.py
│       ├── views_console.py
│       ├── views_arena.py
│       ├── views_replay.py
│       ├── views_stress.py
│       ├── views_failure_map.py
│       ├── views_stations.py
│       ├── views_data_integrity.py
│       └── views_evidence.py
├── scripts/
│   ├── prepare_data.py         # Data preparation and verification
│   └── run_experiments.py      # Authoritative scientific experiment runner
├── results/                    # Precomputed Scientific Artifacts
│   ├── replay/
│   │   └── nominal_results.json
│   ├── holdout/
│   │   └── holdout_results.json
│   ├── randomization/
│   │   └── randomization_results.json
│   ├── stress/
│   │   └── stress_results.json
│   └── decision/
│       └── decision_audit.json
└── tests/                      # Automated Pytest Suite
    ├── test_data.py
    ├── test_leakage.py
    ├── test_policies.py
    ├── test_replay.py
    ├── test_validation.py
    ├── test_stress.py
    └── test_decision.py
```

---

## 2. Software Interfaces & Data Contracts

### 2.1 Core Dataclasses & Contracts

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd

@dataclass
class PolicyResult:
    policy_name: str
    budget: int
    selected_stations: List[str]
    scores: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class ReplayResult:
    policy_name: str
    budget: int
    baseline_error: float
    policy_error: float
    improvement_pct: float
    parameter_errors: Dict[str, float]
    station_residuals: pd.DataFrame
    metadata: Dict[str, Any]

@dataclass
class HoldoutFoldResult:
    fold_index: int
    held_out_parameters: List[str]
    training_parameters: List[str]
    policy_name: str
    budget: int
    holdout_error: float
    improvement_pct: float

@dataclass
class RandomizationDiagnostic:
    policy_name: str
    budget: int
    observed_error: float
    matched_mean_error: float
    diagnostic_tail_proportion: float  # Empirical fraction of 3,000 matched portfolios <= policy error
    replicates: int = 3000

@dataclass
class StressCurvePoint:
    policy_name: str
    budget: int
    stress_level: float
    mean_error: float
    std_error: float
    degradation_pct: float

@dataclass
class DecisionVerdict:
    status: str  # "TRUST" | "CONDITIONAL" | "ABSTAIN"
    budget: int
    clean_winner: str
    robust_winner: str
    headline_improvement: float
    failure_boundary_alpha: float
    reasons: List[str]
    caveats: List[str]

### 2.2 Custom Exception Hierarchy

```python
class WatershieldError(Exception):
    """Base exception for all Watershield domain errors."""

class DataLoadingError(WatershieldError):
    """Raised when raw data files cannot be found, loaded, or read."""

class SchemaValidationError(WatershieldError):
    """Raised when data tables violate expected columns or datatypes."""

class DataIntegrityError(WatershieldError):
    """Raised when invariants fail (e.g. station recurrence != 222 or river cohort != 172)."""

class LeakageViolationError(WatershieldError):
    """Raised when future September data is accessed during policy construction or historical scaling."""

class ArtifactNotFoundError(WatershieldError):
    """Raised when Demo Mode cannot locate a required precomputed artifact."""

class InvalidBudgetError(WatershieldError):
    """Raised when an unsupported budget is requested (not in {10, 20, 40})."""

class PolicyConfigError(WatershieldError):
    """Raised on invalid policy hyperparameters or missing configurations."""

class StressConfigError(WatershieldError):
    """Raised on invalid stress testing parameters (e.g. alpha outside [0, 1])."""
```
```

### 2.2 Policy Interface (`src/policies/base.py`)

```python
from abc import ABC, abstractmethod

class BasePolicy(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def select_stations(
        self,
        historical_state: pd.DataFrame,
        budget: int,
        seed: int = 42,
        config: Optional[Any] = None
    ) -> PolicyResult:
        """
        Receives historical data (July + August), returns exactly `budget` stations.
        Must NOT accept or access September future data.
        """
        pass
```

---

## 3. Serialization Schemas

All scientific experiment runs produce deterministic, JSON-serializable output objects stored in `results/`:
- `results/replay/nominal_results.json`:
  ```json
  {
    "cohort": "river_172",
    "timestamp": "2026-10-09T00:00:00Z",
    "budgets": {
      "10": {
        "Random": {"error": 1.285, "improvement": 0.0},
        "Risk": {"error": 1.194, "improvement": 7.1},
        "Change": {"error": 1.207, "improvement": 6.1},
        "Coverage": {"error": 1.250, "improvement": 2.7},
        "Risk_x_Change": {"error": 1.198, "improvement": 6.8}
      },
      "20": {
        "Random": {"error": 1.185, "improvement": 0.0},
        "Risk": {"error": 1.059, "improvement": 10.6},
        "Change": {"error": 0.892, "improvement": 24.7},
        "Coverage": {"error": 1.115, "improvement": 5.9},
        "Risk_x_Change": {"error": 1.026, "improvement": 13.4}
      },
      "40": {
        "Random": {"error": 0.985, "improvement": 0.0},
        "Risk": {"error": 0.855, "improvement": 13.2},
        "Change": {"error": 0.711, "improvement": 27.8},
        "Coverage": {"error": 0.902, "improvement": 8.4},
        "Risk_x_Change": {"error": 0.839, "improvement": 14.8}
      }
    }
  }
  ```

---

## 4. Test Specifications & Verification Gates

### 4.1 Data Pipeline Tests (`tests/test_data.py`)
- Detect duplicate July 2025 files via SHA-256 and confirm single ingestion.
- Assert exactly 222 recurring stations across July, August, September.
- Assert exactly 172 river stations in primary cohort (`Type Water Body == 'RIVER'`).
- Assert presence and non-trivial values for all 12 core parameters.

### 4.2 Leakage Gate Tests (`tests/test_leakage.py`)
- Invariant test: Pass modified/synthetic September values and assert that policy station selections remain bit-for-bit identical.
- Invariant test: Confirm feature scaler fits strictly on July/August data.

### 4.3 Policy Arena Tests (`tests/test_policies.py`)
- Assert all 5 policies return exactly $B$ stations for $B \in \{10, 20, 40\}$.
- Assert station IDs returned are valid subset of the 172 river stations.
- Assert determinism: identical seed produces identical station sets.

### 4.4 Replay & Validation Tests (`tests/test_replay.py`, `tests/test_validation.py`)
- Verify baseline persistence reconstruction logic.
- Verify normalized residual error calculation.
- Verify 4-fold holdout runs and generates results for held-out parameters.

### 4.5 Decision Gate Tests (`tests/test_decision.py`)
- Verify logic yields `CONDITIONAL` when clean and robust winners split.
- Verify logic yields `ABSTAIN` when severe synthetic noise or negative holdout is injected.

---

## 5. Implementation Sequence

The implementation proceeds in strict chronological phases:
1. **Phase 1: Environment & Data Pipeline:** Set up dependencies, copy raw datasets to `data/raw/`, implement `src/data/`, build `scripts/prepare_data.py`.
2. **Phase 2: Policy Arena & Leakage Barrier:** Implement `src/policies/` and `src/replay/`, add leakage tests.
3. **Phase 3: Validation & Stress Engines:** Implement `src/validation/` and `src/stress/`.
4. **Phase 4: Decision Gate & Artifact Generation:** Implement `src/decision/` and `scripts/run_experiments.py`, generate validated artifacts in `results/`.
5. **Phase 5: Streamlit Frontend:** Build `app.py` and modular views in `src/ui/`.
6. **Phase 6: Quality Assurance & Hardening:** Run pytest suite, verify Demo Mode and Experiment Mode, update documentation.
