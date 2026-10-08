# 04_ARCHITECTURE.md — System & Technical Architecture

## 1. Architectural Philosophy & Principles

WATERSHIELD is architected around a strict unidirectional data flow and clean separation of concerns:
```text
DATA INGESTION
      ↓
INTEGRITY & ALIGNMENT
      ↓
FEATURE & STATE ENGINE
      ↓
POLICY ARENA
      ↓
TEMPORAL REPLAY (LEAKAGE BARRIER)
      ↓
NETWORK METRICS
      ↓
INDEPENDENT VALIDATION & STRESS LAB
      ↓
DECISION & TRUST GATE
      ↓
SERIALIZED ARTIFACTS
      ↓
STREAMLIT DECISION CONSOLE
```

### Core Invariants:
1. **Frontend-Backend Decoupling:** The Streamlit user interface is strictly a visualization and presentation consumer. It **never** computes policy selections, residual errors, holdout folds, or decision gates.
2. **Authoritative Backend:** All domain logic and mathematical calculations reside within `src/`.
3. **Data Immutability:** Raw government files in `data/raw/` are read-only. Processed data and experiment artifacts are written to `data/processed/` and `results/`.
4. **Deterministic Reproducibility:** Every pipeline execution is parameterized by a centralized configuration object and explicit random seeds.

---

## 2. System Component Architecture

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                            STREAMLIT FRONTEND                            │
│  [Decision Console] [Policy Arena] [Replay] [Stress Lab] [Failure Map]   │
│                 [Stations] [Data Integrity] [Evidence]                   │
└────────────────────────────────────▲─────────────────────────────────────┘
                                     │ JSON / Dataframe Artifacts
┌────────────────────────────────────┴─────────────────────────────────────┐
│                          DECISION & AUDIT LAYER                          │
│   src/decision/reliability.py    src/decision/failure_boundary.py       │
│   src/decision/recommendation.py (TRUST / CONDITIONAL / ABSTAIN)        │
└────────────────────────────────────▲─────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴─────────────────────────────────────┐
│                       VALIDATION & STRESS LAB ENGINES                    │
│   src/validation/parameter_holdout.py  src/validation/district_random.py  │
│   src/stress/station_failure.py        src/stress/missing_data.py        │
└────────────────────────────────────▲─────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴─────────────────────────────────────┐
│                      REPLAY & EVALUATION ENGINE                          │
│   src/replay/temporal_replay.py  src/replay/baseline.py                  │
│   src/replay/metrics.py (Standardized Residual Error, Improvement vs Rnd)│
└────────────────────────────────────▲─────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴─────────────────────────────────────┐
│                           POLICY ARENA LAYER                             │
│   src/policies/base.py (Abstract Interface)                              │
│   [Random] [Risk] [Change] [Coverage] [Risk×Change]                      │
└────────────────────────────────────▲─────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴─────────────────────────────────────┐
│                      DATA & FEATURE PIPELINE                             │
│   src/data/loader.py (SHA256 dedup)    src/data/alignment.py (222/172)   │
│   src/data/cleaning.py                 src/data/features.py (hist scale) │
└────────────────────────────────────▲─────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴─────────────────────────────────────┐
│                             RAW DATA STORAGE                             │
│   data/raw/ (July 2025, August 2025, September 2025 NWMP MPCB CSVs)     │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Package Structure & Module Responsibilities

### 3.1 `src/config.py` — Central Configuration
Encapsulates all system constants, directories, budgets, seeds, parameter lists, and decision thresholds into structured, dataclass-based configurations:
- File paths for raw and processed datasets.
- Parameter schema: 12 core parameters, directional polarities (pollutants vs DO vs pH).
- Cohort specifications: 172 river stations vs 222 network stations.
- Budgets: $B \in \{10, 20, 40\}$.
- Stress testing grids: $\alpha \in [0.10, 0.50]$, $\beta \in [0.10, 0.30]$.
- Audit thresholds: minimum improvement, holdout generalization floor, matched diagnostic cutoff.

### 3.2 `src/data/` — Ingestion & State Preparation
- `loader.py`: Ingests raw CSVs, executes SHA-256 duplicate detection, ignores duplicate July file, and returns raw dataframes.
- `cleaning.py`: Sanitizes column names, coerces numeric parameters, flags missing values.
- `validation.py`: Asserts schema validity, checks parameter presence and valid geographic coordinates.
- `alignment.py`: Intersects monthly stations, verifies the 222 recurring network stations, and extracts the 172 river cohort (`Type Water Body == 'RIVER'`).
- `features.py`: Computes historical baseline scales ($\mu_p^{\text{hist}}, \sigma_p^{\text{hist}}$) using only July and August data. Explicitly prevents access to September data.

### 3.3 `src/policies/` — The Policy Arena
- `base.py`: Defines the abstract base class `BasePolicy` enforcing:
  ```python
  def select_stations(
      self, 
      historical_state: pd.DataFrame, 
      budget: int, 
      seed: int = 42
  ) -> PolicyResult: ...
  ```
- `random_policy.py`: Uniform random station sampling.
- `risk_policy.py`: Historical water-quality degradation scoring.
- `change_policy.py`: July-to-August temporal movement scoring.
- `coverage_policy.py`: Geographic and district dispersion sampling.
- `risk_change_policy.py`: Multiplicative ranking combination of risk and change.

### 3.4 `src/replay/` — Temporal Replay Engine
- `baseline.py`: Implements the persistence baseline (unsampled stations retain August values).
- `temporal_replay.py`: Manages the temporal simulation, receives selected station IDs, reveals September observations exclusively for evaluation, and reconstructs the network.
- `metrics.py`: Computes standardized network residual error, station-level residuals, and improvement versus random.

### 3.5 `src/validation/` — Independent Validation Lab
- `parameter_holdout.py`: Orchestrates 4-fold cross-parameter holdout (folds of 3 parameters), evaluating policies constructed on 9 parameters against the 3 held-out variables.
- `district_randomization.py`: Samples random portfolios matching the exact district vector of candidate policies (3,000 permutations) to compute empirical diagnostics.
- `sensitivity.py`: Tests stability across parameter subsets (Core12, Chem5, Physical5).

### 3.6 `src/stress/` — Controlled Failure Lab
- `station_failure.py`: Simulates equipment loss by dropping a fraction $\alpha$ of selected stations and reverting them to baseline across 200 replicates.
- `missing_data.py`: Simulates input data loss by corrupting August observations at rate $\beta$ with median imputation across 200 replicates.

### 3.7 `src/decision/` — Decision & Audit Gate
- `reliability.py`: Applies multi-layer logical rules across replay, holdout, randomization, and stress outputs to issue **TRUST**, **CONDITIONAL**, or **ABSTAIN**.
- `failure_boundary.py`: Solves for the critical stress tolerance threshold $\alpha^*$ and delineates operational safety zones.
- `recommendation.py`: Synthesizes the Clean Winner vs Robust Winner analysis and outputs the operational audit verdict.

---

## 4. Execution Pipelines & Storage Architecture

### 4.1 Data Pipeline Flow
```text
Raw CSVs (data/raw/)
  → [loader.py]
  → [cleaning.py]
  → [alignment.py]
  → Processed Cohort Parquets (data/processed/):
      - recurring_stations_222.parquet
      - river_cohort_172.parquet
      - historical_state_jul_aug.parquet
      - hidden_future_sep.parquet
```

### 4.2 Experiment Pipeline Flow (`scripts/run_experiments.py`)
Executes the full scientific suite and serializes structured JSON and Parquet artifacts to `results/`:
- `results/replay/nominal_results.json`: Residual errors and improvement metrics for all 5 policies across budgets 10, 20, 40.
- `results/holdout/holdout_results.json`: Performance across all 4 holdout folds.
- `results/randomization/randomization_results.json`: Matched randomization distributions and diagnostic proportions (3,000 replicates).
- `results/stress/stress_results.json`: Station loss and missingness curves across 200 replicates.
- `results/decision/decision_audit.json`: Authoritative audit verdict, failure boundaries, Clean vs Robust winners.

### 4.3 Runtime Modes: Demo Mode vs Experiment Mode
1. **Demo Mode (Default):**
   - Streamlit UI loads precomputed, verified artifacts from `results/`.
   - Guarantees instantaneous loading ($<500\,\text{ms}$), zero lag during presentations, and $100\%$ determinism.
   - All presented values reflect actual scientific calculations performed by `scripts/run_experiments.py`.
2. **Experiment Mode (Interactive):**
   - User can trigger live execution from the UI or adjust parameters (seed, custom stress levels, custom budget).
   - Invokes backend Python functions with real-time progress indicators.
   - Invalidates in-memory caches to guarantee fresh scientific evaluations.

---

## 5. Backend Error Handling Architecture

The backend implements a structured exception hierarchy rooted in `WatershieldError`. Scientific computation errors must never be silently swallowed or replaced with fabricated placeholders.

```text
WatershieldError (Base)
├── DataLoadingError           (Raw CSV missing, unreadable, corrupt)
├── SchemaValidationError      (Missing columns, unrecognized parameters, invalid datatypes)
├── DataIntegrityError         (Station recurrence mismatch, missing coordinates, non-river ambiguity)
├── LeakageViolationError      (September future data accessed during historical state construction)
├── ArtifactNotFoundError      (Precomputed results JSON missing in Demo Mode)
├── InvalidBudgetError         (Budget B not in {10, 20, 40} or B > N)
├── PolicyConfigError          (Invalid policy parameters or unknown policy key)
└── StressConfigError          (Stress rate outside allowed bounds [0.0, 1.0])
```

### Error Recovery & User-Facing Behavior:
1. **Data Ingestion Failures:** If raw files in `data/raw/` are missing or corrupted, `loader.py` raises `DataLoadingError` with the expected path and SHA-256 signature. The UI catches this and renders an informative alert directing the operator to run `scripts/prepare_data.py`.
2. **Integrity Failures:** If station recurrence across the 3 months does not equal exactly 222 stations, `alignment.py` raises `DataIntegrityError`. The pipeline halts; no partial runs are permitted.
3. **Leakage Gate Trigger:** If September observations or statistics are detected in feature scaling or station selection, `LeakageViolationError` is raised immediately, terminating the run to preserve scientific integrity.
4. **Missing Artifacts (Demo Mode):** If a user attempts to view a screen in Demo Mode before `scripts/run_experiments.py` has produced artifacts, `ArtifactNotFoundError` triggers an operational fallback banner: *"Precomputed artifact missing. Switch to Experiment Mode to generate results, or run `python scripts/run_experiments.py`."*
5. **No Silent Fallbacks:** Under no circumstances will the system substitute mock metrics or hardcoded scores when an experiment fails.

---

## 6. Caching Architecture & Invalidation

To maintain $<500\,\text{ms}$ presentation latency while preventing scientific stale-state issues, caching is strictly partitioned:

### 6.1 Streamlit Cache Rules
- **Data Ingestion & Alignment (`@st.cache_data`):**
  - Cached function: `load_processed_cohort(cohort_name: str, processed_dir: Path)`
  - Cache Key: Includes file modification timestamps and SHA-256 content hashes of the underlying Parquet files.
- **Precomputed Artifact Loading (`@st.cache_data`):**
  - Cached function: `load_experiment_artifact(artifact_name: str, results_dir: Path)`
  - Cache Key: Path and file modification timestamp. In Demo Mode, artifacts are loaded into memory once and reused.
- **Experiment Mode Invalidation:**
  - When the user clicks **Run Pipeline** in Experiment Mode, `st.cache_data.clear()` is called for experimental keys, and calculations execute live.
  - A unique `experiment_run_id` (UUID4) is attached to the session state to isolate live results from cached demo artifacts.

### 6.2 Preprocessing Cache (Parquet)
- Heavy operations (raw CSV parsing, string sanitization, coordinate verification, 3-month alignment) are performed once by `scripts/prepare_data.py` and written to immutable Parquet files in `data/processed/`.
- Backend modules read directly from `data/processed/`, eliminating repeat CSV parsing overhead.

---

## 7. Logging & Provenance Architecture

Structured logging ensures total reproducibility and transparent audit trails.

### 7.1 Configuration & Logger Structure
- Centralized logger factory in `src/utils/logger.py`:
  ```python
  import logging

  def get_logger(name: str) -> logging.Logger:
      logger = logging.getLogger(f"watershield.{name}")
      # Standard format: [%(asctime)s] [%(levelname)s] [%(name)s] [run_id=%(run_id)s]: %(message)s
      return logger
  ```

### 7.2 Log Levels & Usage
- **`INFO`:** Major pipeline stage milestones (e.g., *"Ingested 222 recurring stations"*, *"Frozen station selection for budget B=20"*), high-level metric summaries, run start/completion.
- **`WARNING`:** Non-fatal conditions (e.g., *"Parameter Phosphate has 3 missing values in August; applying historical median imputation"*), operating boundary proximity ($\alpha \ge 0.25$).
- **`ERROR`:** Integrity check failures, schema mismatches, leakage violations, unhandled computation errors.
- **`DEBUG`:** Station-by-station scores, intermediate distance matrices in Coverage policy, Monte Carlo replicate progress.

### 7.3 Provenance Records
Every experiment run automatically generates an execution provenance record embedded in its output JSON:
- `run_id`: Unique execution identifier.
- `timestamp`: UTC ISO-8601 timestamp.
- `git_commit`: Short Git commit hash (if available).
- `input_hashes`: SHA-256 hashes of input raw and processed datasets.
- `config`: Complete serialization of `AppConfig` dataclass (seeds, budgets, stress parameters).
- `system_info`: OS, Python version, library versions (pandas, numpy, scipy, sklearn).

---

## 8. Data & Module Contracts

Strict data contracts are enforced between all system layers:

### 8.1 Ingestion & Feature Layer (`src/data/`)
- **Inputs:** Raw CSV files in `data/raw/` (`NWMP_July2025.csv`, `NWMP_August2025_MPCB_0.csv`, `NWMP_September2025_MPCB_0.csv`).
- **Outputs:** 
  - `HistoricalState`: Typed container holding July and August cleaned observations, station metadata, and pre-September normalization parameters ($\mu_p^{\text{hist}}, \sigma_p^{\text{hist}}$).
  - `FutureState`: Strictly isolated container holding September observations for evaluation only.
- **Validation:** Assert exactly 222 recurring stations; assert 172 river stations; assert 12 core parameters present.
- **Failure Behavior:** Raises `DataIntegrityError` or `SchemaValidationError`.

### 8.2 Policy Layer (`src/policies/`)
- **Inputs:** `HistoricalState` dataframe, `budget: int` ($B \in \{10, 20, 40\}$), `seed: int`, `config: PolicyConfig`.
- **Outputs:** `PolicyResult(policy_name: str, budget: int, selected_stations: List[str], scores: Dict[str, float], metadata: Dict[str, Any])`.
- **Validation:** `len(set(selected_stations)) == budget`; all IDs in 172 river cohort.
- **Failure Behavior:** Raises `InvalidBudgetError` or `PolicyConfigError`.

### 8.3 Replay Layer (`src/replay/`)
- **Inputs:** `selected_stations: List[str]`, `HistoricalState`, `FutureState`, `config: ReplayConfig`.
- **Outputs:** `ReplayResult(policy_name: str, budget: int, baseline_error: float, policy_error: float, improvement_pct: float, parameter_errors: Dict[str, float], station_residuals: pd.DataFrame, metadata: Dict[str, Any])`.
- **Validation:** Error non-negative; persistence baseline strictly computed from August for unsampled stations.
- **Failure Behavior:** Raises `LeakageViolationError` if future data influenced input selection.

### 8.4 Validation & Stress Layer (`src/validation/`, `src/stress/`)
- **Inputs:** `HistoricalState`, `FutureState`, policy definitions, stress grids ($\alpha, \beta$), seed.
- **Outputs:** `HoldoutFoldResult` (4 folds), `RandomizationDiagnostic` (3,000 permutations), `StressCurvePoint` (replicates across $\alpha \in [0.1, 0.5]$).
- **Validation:** Replicate counts match configuration; random seeds strictly recorded.
- **Failure Behavior:** Raises `StressConfigError` on invalid parameter grids.

### 8.5 Decision Gate Layer (`src/decision/`)
- **Inputs:** Replay results, holdout results, randomization diagnostics, stress curves.
- **Outputs:** `DecisionVerdict(status: str ["TRUST" | "CONDITIONAL" | "ABSTAIN"], budget: int, clean_winner: str, robust_winner: str, headline_improvement: float, failure_boundary_alpha: float, reasons: List[str], caveats: List[str])`.
- **Validation:** Verdict must be one of the three enumerated states; clean and robust winners explicitly mapped.
- **Failure Behavior:** If metrics are missing or contradictory, defaults safely to `ABSTAIN` with explanatory audit logging.

### 8.6 Frontend Presentation Layer (`app.py`, `src/ui/`)
- **Role:** Pure presentation consumer.
- **Rule:** The UI **must never** compute policy scores, residuals, holdout folds, or decision gates inline. All displayed metrics originate directly from backend artifacts.

---

## 9. Security, Deployment & Environmental Invariants
- **Platform Compatibility:** Windows 10/11, Linux (Ubuntu 22.04+), macOS (12+).
- **Python Runtime:** Python 3.11+.
- **No External Services:** Completely self-contained; zero reliance on cloud databases, Redis, Docker daemons, or remote APIs.
- **Data Integrity:** Read-only access to raw files prevents accidental data modification during experiment runs.
- **Resource Constraints:** Runs comfortably on 4-core CPU, 8GB RAM laptop with $<15$s experiment runtimes.
