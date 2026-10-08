# WATERSHIELD
### Water Monitoring Policy Reliability & Decision-Audit Engine

> **"Don't trust the optimizer. Test the policy."**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Specification & Setup Complete](https://img.shields.io/badge/status-specification%20ready-success.svg)](#)
[![Domain: Environmental Decision-Audit](https://img.shields.io/badge/domain-water%20monitoring-teal.svg)](#)

---

## 1. Project Overview & Core Question

Monitoring authorities responsible for environmental water quality face strict operational and economic constraints. While an ambient network may comprise hundreds of designated monitoring stations, available logistics, personnel, and laboratory capacity often permit sampling only a small fraction $B \ll N$ during any given monitoring cycle.

The central dilemma is:

> **"Which monitoring policy should we trust when we cannot monitor everything?"**

Standard engineering practice assumes that optimizing an objective function produces an optimal monitoring network. However, in non-stationary and data-scarce environmental systems:
1. Historical optimality does not guarantee future information preservation.
2. An optimizer can overfit to specific observed parameters.
3. A policy may collapse when stations fail or telemetry data is missing.

**WATERSHIELD reframes the problem:** Instead of proposing another sensor placement optimizer, it treats competing monitoring policies as candidates undergoing an **independent, empirical decision audit**. It evaluates whether a policy's nominal advantage survives out-of-sample temporal replay, transfers across independent parameters, outperforms district-matched random allocations, and endures controlled infrastructure stress.

---

## 2. What WATERSHIELD Is and Is Not

### What WATERSHIELD Is:
- An independent empirical policy-audit layer.
- A leakage-safe temporal replay engine (July/August 2025 $\rightarrow$ September 2025).
- A standardized evaluation arena for 5 competing policies (Random, Risk, Change, Coverage, Risk × Change).
- A multi-layer validation engine (4-fold cross-parameter holdout, 3,000 district-matched random diagnostic portfolios).
- A controlled failure stress testing lab (station availability loss and telemetry missingness).
- A decision system yielding **TRUST**, **CONDITIONAL**, or **ABSTAIN** verdicts with failure boundary demarcation.
- A reproducible scientific prototype.

### What WATERSHIELD Is NOT:
- **NOT** a sensor placement optimizer or automated sensor installation engine.
- **NOT** an IoT telemetry platform or hardware sensor array.
- **NOT** a real-time contamination alert or early-warning system.
- **NOT** a machine-learning contamination forecasting model.
- **NOT** a digital twin or hydraulic simulation.
- **NOT** an LLM chatbot, AI agent swarm, or conversational assistant.
- **NOT** a blockchain verification system.
- **NOT** an officially deployed government platform or regulatory replacement.

---

## 3. Scientific Scope & Known Limitations

1. **Temporal Horizon:** Three monthly observation snapshots (July, August, September 2025) from the National Water Quality Monitoring Programme (NWMP), Maharashtra Pollution Control Board (MPCB). Suitable for a retrospective prototype audit, not multi-season climate modeling.
2. **Primary Cohort:** Evaluated strictly on the **172 recurring river monitoring stations** (`Type Water Body == 'RIVER'`). The broader network of 222 recurring stations includes non-river bodies (wells, lakes, canals) retained for secondary exploratory inspection.
3. **Controlled Synthetic Stress:** Stress tests simulate random station dropouts ($10\%–50\%$) and input missingness ($10\%–30\%$). These are controlled simulations to evaluate algorithmic robustness boundaries, not empirical records of real-world equipment failure rates.
4. **Spatial & Serial Dependence:** Monitoring stations along river reaches exhibit spatial autocorrelation, and repeated observations exhibit temporal serial correlation. Randomization results (3,000 matched portfolios) are presented as **empirical spatial diagnostics** ($\hat{q}_{\text{diag}}$), NOT asymptotic i.i.d. hypothesis-test $p$-values.

---

## 4. Repository Structure

```text
AIKTC_NEXATHON_TEAMFALCONS-WATERSHIELD/
├── AGENTS.md                   # Permanent instructions & governance for AI coding agents
├── README.md                   # This project guide and operational reference
├── requirements.txt            # Python dependency manifest
├── DOCS/                       # Authoritative Project Documentation Suite
│   ├── 01_MASTER_PROJECT.md    # Project constitution, problem, scope & claims
│   ├── 02_REQUIREMENTS.md     # Functional & technical system requirements
│   ├── 03_SCIENTIFIC_SPEC.md   # Mathematical equations, policies & audit rules
│   ├── 04_ARCHITECTURE.md      # Modules, error handling, caching & contracts
│   ├── 05_PRODUCT_UI_UX.md     # Visual design system, responsive layouts & 8 views
│   ├── 06_IMPLEMENTATION.md    # Engineering interfaces, schemas & test plans
│   ├── 07_ROADMAP.md           # Implementation phases, risks & Definition of Done
│   └── WATERSHIELD_MASTER_PROJECT_DOCUMENT.md # Comprehensive project archive
├── data/
│   ├── raw/                    # Immutable raw MPCB NWMP CSV files (July, August, Sept)
│   └── processed/              # Cleaned & aligned Parquet cohorts (prepared)
├── src/                        # Authoritative Scientific Backend & UI View Modules
│   ├── config.py               # Centralized typed configuration dataclass
│   ├── utils/                  # Logging, error types & helper routines
│   ├── data/                   # Data ingestion, SHA-256 deduplication & alignment
│   ├── policies/               # Standardized policy implementations (Random, Risk, Change, Cov, R×C)
│   ├── replay/                 # Persistence baseline & standardized residual metrics
│   ├── validation/             # 4-fold holdout & 3,000 district-matched randomization
│   ├── stress/                 # Controlled station loss & missing data simulations
│   ├── decision/               # Reliability engine, failure boundary & recommendation
│   └── ui/                     # Modular Streamlit view renderers (8 views)
├── scripts/
│   ├── verify_env.py           # Environment & dependency verification script
│   ├── prepare_data.py         # Data alignment and Parquet generation (Phase 2)
│   └── run_experiments.py      # Scientific experiment runner producing JSON artifacts (Phase 8)
├── results/                    # Validated scientific experiment JSON artifacts
└── tests/                      # Automated Pytest suite
```

---

## 5. Environment Setup & Dependency Installation

### 5.1 Prerequisites
- **Operating System:** Windows 10/11, Linux (Ubuntu 22.04+), or macOS (12+)
- **Python Version:** Python 3.11+ (Python 3.11, 3.12, 3.13, 3.14 supported)

### 5.2 Create Virtual Environment

On Windows (PowerShell):
```powershell
# Using Python Launcher
py -3 -m venv .venv

# Or using direct Python 3.11+ path
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

On Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5.3 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.4 Verify Environment
Run the environment verification script to confirm all core packages are installed:
```powershell
python scripts/verify_env.py
# Or on Windows with py launcher:
py -3 scripts/verify_env.py
```

---

## 6. Execution Modes & Workflow

WATERSHIELD operates in two distinct operational modes:

### 6.1 Demo Mode (Instantaneous, Precomputed)
- Consumes verified scientific artifacts stored in `results/`.
- Renders all 8 interactive views in $<500\,\text{ms}$ with zero calculation lag.
- Guaranteed $100\%$ determinism for presentation panels and live evaluations.

Launch command (Phase 9):
```bash
streamlit run app.py
```

### 6.2 Experiment Mode (Live Scientific Pipeline)
- Triggers end-to-end execution of data preparation, policy scoring, hidden temporal replay, holdout folds, 3,000-draw district randomization, and 200-replicate stress tests.
- Re-generates all artifacts in `results/` from live data.

Execution commands (Planned for build phases):
```bash
# 1. Prepare and align data
python scripts/prepare_data.py

# 2. Run full scientific experiment suite
python scripts/run_experiments.py
```

---

## 7. Testing & Quality Assurance

Automated unit and integration tests enforce scientific invariants:
```bash
pytest tests/ -v
```

Key verification gates:
- **Temporal Leakage Test:** Asserts that September future observations are never passed to feature scalers or policy scorers.
- **Data Recurrence Test:** Asserts exactly 222 recurring stations across all three months and exactly 172 river cohort stations.
- **Budget Exactness Test:** Asserts every policy returns exactly $B$ unique stations for $B \in \{10, 20, 40\}$.
- **Decision Gate Test:** Asserts proper issuance of `TRUST`, `CONDITIONAL`, or `ABSTAIN` verdicts without hardcoded mocks.

---

## 8. Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `Python was not found...` on Windows | Windows App Execution Alias stub is intercepting `python` command | Run with `py -3 <script>` using the Windows Python Launcher, or call the virtual environment Python directly: `.\.venv\Scripts\python.exe <script>`. |
| `Missing dependency: pandas...` | Dependencies not installed in active environment | Activate your virtual environment and run `pip install -r requirements.txt`. Run `python scripts/verify_env.py` to check. |
| `ArtifactNotFoundError` in UI | Running in Demo Mode before results have been compiled | Run `python scripts/run_experiments.py` to generate validated JSON artifacts into `results/`. |
| Script execution disabled in PowerShell | PowerShell execution policy restricts scripts | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. |

---

## 9. Citation & Governance

If referencing WATERSHIELD in research or evaluation:
> **WATERSHIELD:** A Failure-Aware Decision Framework for Reliable Water-Quality Monitoring Under Limited Sampling Resources (AIKTC Nexathon 2026).

All agent contributions must strictly follow [`AGENTS.md`](file:///c:/Users/rrmss/Desktop/WATERSHIELD/AIKTC_NEXATHON_TEAMFALCONS-WATERSHIELD/AGENTS.md) and the approved claims policy.