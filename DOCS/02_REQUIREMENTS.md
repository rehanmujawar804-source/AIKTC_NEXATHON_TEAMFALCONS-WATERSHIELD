# 02_REQUIREMENTS.md — System & Product Requirements

## 1. System Vision & Scope
WATERSHIELD provides an independent, reproducible decision-audit engine for environmental monitoring authorities allocating constrained station-sampling budgets. This document specifies the functional, scientific, technical, and quality requirements necessary to deliver the production-ready MVP.

---

## 2. Functional Requirements (FR)

### 2.1 Data Ingestion & Integrity (FR-DATA)
- **FR-DATA-01 (Source Ingestion):** The system shall load monthly Maharashtra NWMP datasets for July 2025, August 2025, and September 2025 from local raw storage (`data/raw/`).
- **FR-DATA-02 (Duplicate Detection):** The data pipeline shall compute cryptographic hashes (SHA-256) of input files and deduplicate redundant raw files (specifically detecting the bit-for-bit identical July 2025 files).
- **FR-DATA-03 (Station Recurrence):** The pipeline shall identify and verify the recurrence of station codes across all three months, asserting that exactly 222 stations exist across the full dataset.
- **FR-DATA-04 (Cohort Stratification):** The system shall separate the network into:
  - **Primary Scientific Cohort:** Exactly 172 recurring river stations (`Type Water Body == 'RIVER'`).
  - **Secondary Network Cohort:** All 222 recurring stations (accessible for diagnostics only).
- **FR-DATA-05 (Parameter Enforcement):** The pipeline shall parse and clean the 12 core parameters: Dissolved O2, pH, BOD, Conductivity, Nitrate N, Fecal Coliform, Total Coliform, Turbidity, COD, Amonia N, Total Dissolved Solids, and Phosphate.
- **FR-DATA-06 (Feature Exclusion):** The feature engineering layer shall strictly exclude `Use Based Class` from policy features due to temporal classification instability.

### 2.2 Policy Arena Engine (FR-POL)
- **FR-POL-01 (Uniform Interface):** Every policy shall implement the common contract:
  $$\pi(\text{historical\_state}, B, \text{seed}, \text{config}) \rightarrow \mathcal{S}_B, \text{scores}, \text{metadata}$$
- **FR-POL-02 (Budget Enforcement):** The policy engine shall guarantee that every returned station selection contains exactly $B$ unique valid station identifiers, where $B \in \{10, 20, 40\}$.
- **FR-POL-03 (Determinism):** Given an identical random seed and input state, policy selection must be $100\%$ deterministic and reproducible.
- **FR-POL-04 (Arena Policies):** The system shall implement:
  1. `RandomPolicy`: Deterministic uniform sampling baseline.
  2. `RiskPolicy`: Prioritizing stations exhibiting historical water quality degradation.
  3. `ChangePolicy`: Prioritizing stations exhibiting large July-to-August temporal movement.
  4. `CoveragePolicy`: Spatial dispersion across districts and river reaches.
  5. `RiskChangePolicy`: Multiplicative/ranking combination of historical risk and rate of change.

### 2.3 Temporal Replay & Leakage Prevention (FR-REP)
- **FR-REP-01 (Information Boundary):** Station selection and policy feature normalization must execute exclusively on July + August 2025 observations.
- **FR-REP-02 (Leakage Gate):** September 2025 observations must remain strictly hidden until after station selection is frozen. No September statistics may influence normalization or scoring.
- **FR-REP-03 (Baseline Reconstruction):** For unsampled stations ($i \notin \mathcal{S}_B$), the system shall impute the September state using the persistence baseline ($y_{i,p}^{\text{Aug}}$). For sampled stations ($i \in \mathcal{S}_B$), the true observed September value shall be revealed ($y_{i,p}^{\text{Sep}}$).
- **FR-REP-04 (Error Evaluation):** The system shall compute the Standardized Network Residual Error ($e_\pi$) across all stations and parameters, scaled exclusively by historical scale factors ($\sigma_p^{\text{hist}}$).
- **FR-REP-05 (Improvement Metric):** The system shall compute percentage improvement over random:
  $$\Delta_\pi = \frac{e_{\text{random}} - e_\pi}{e_{\text{random}}} \times 100\%$$

### 2.4 Multi-Layer Validation (FR-VAL)
- **FR-VAL-01 (Cross-Parameter Holdout):** The system shall implement a 4-fold cross-parameter holdout where 3 parameters are excluded from policy construction, the policy is constructed on the remaining 9 parameters, and residual error is measured exclusively on the 3 held-out parameters.
- **FR-VAL-02 (District-Matched Randomization):** The validation engine shall compute district composition vectors for candidate policies and generate exactly 3,000 matched random portfolios to evaluate whether policy performance is confounded by geographic district distribution, computing the empirical diagnostic tail proportion ($\hat{q}_{\text{diag}}$) without claiming formal asymptotic p-values given network dependence.

### 2.5 Controlled Stress Testing (FR-STR)
- **FR-STR-01 (Station Availability Loss):** The stress engine shall simulate random station dropouts ($10\%, 20\%, 30\%, 40\%, 50\%$) where sampled stations fail to deliver measurements, forcing fallback to baseline.
- **FR-STR-02 (Missing-Data Perturbation):** The stress engine shall simulate input telemetry degradation by introducing missing values into August inputs and applying median-centered imputation prior to station selection.
- **FR-STR-03 (Failure Boundary Mapping):** The engine shall evaluate degradation curves across stress levels to identify the critical failure boundary where a policy ceases to outperform random sampling.

### 2.6 Decision Gate & Governance (FR-DEC)
- **FR-DEC-01 (Audit Verdicts):** The decision gate shall evaluate empirical evidence against deterministic rules to issue:
  - **TRUST**
  - **CONDITIONAL**
  - **ABSTAIN**
- **FR-DEC-02 (Winner Distinction):** The gate shall explicitly report both the **Clean Winner** (best under nominal conditions) and the **Robust Winner** (best under tested failure regimes).
- **FR-DEC-03 (Abstention Handling):** If policies are indistinguishable, holdout fails, or stress degradation is catastrophic, the system shall formally issue **ABSTAIN** with explanatory evidence.

---

## 3. Frontend & Presentation Requirements (FR-UI)

- **FR-UI-01 (Product Persona):** The frontend shall present an operational decision-audit console with high data density, clear visual hierarchy, and scientific rigor. It shall not resemble a student project or consumer SaaS template.
- **FR-UI-02 (Core Views):** The UI shall provide 8 dedicated functional areas:
  1. **Decision Console:** Primary landing view displaying the core question, current winner, audit verdict (TRUST/CONDITIONAL/ABSTAIN), headline metrics, and key warnings.
  2. **Policy Arena:** Comparative ranking of all 5 policies across budgets $B \in \{10, 20, 40\}$.
  3. **Replay & Evidence:** Step-by-step visual audit trail of the temporal replay protocol and leakage barrier.
  4. **Stress Lab:** Interactive simulation of station loss and missing data perturbation.
  5. **Failure Map:** Multi-level failure boundary curves indicating when trust terminates.
  6. **Stations View:** Detailed table and geographic distribution of selected vs unselected stations with scores and selection rationales.
  7. **Data Integrity:** Verification dashboard showing recurrence, duplicate detection, metadata stability, and missingness audits.
  8. **Evidence & Research:** Academic evidence cards summarizing nominal results, holdouts, randomization, limitations, and judge defense.
- **FR-UI-03 (Execution Modes):** The UI shall support:
  - **Demo Mode:** Instantaneous rendering using precomputed, validated scientific artifacts (`results/`).
  - **Experiment Mode:** Triggering live execution of the scientific pipeline with progress tracking.
- **FR-UI-04 (Strict Separation):** The UI layer shall never calculate policy scores, residuals, holdout folds, or decision gates inline. All displayed metrics must originate from backend artifacts.

---

## 4. Technical & Non-Functional Requirements (NFR)

### 4.1 Architecture & Modularity
- **NFR-MOD-01:** The codebase shall be modularized into distinct packages: `data`, `policies`, `replay`, `validation`, `stress`, and `decision`.
- **NFR-MOD-02:** Centralized configuration shall reside in `src/config.py`. No magic numbers or hardcoded thresholds may exist in pipeline logic or UI templates.

### 4.2 Performance & Resource Utilization
- **NFR-PERF-01 (Runtime Constraints):** The entire application and experiment suite must execute seamlessly on standard laptop hardware (4-core x86_64, 8GB RAM, no GPU required).
- **NFR-PERF-02 (UI Responsiveness):** In Demo Mode, page transitions and budget changes must render in $< 500\,\text{ms}$.
- **NFR-PERF-03 (Experiment Execution):** A full retrospective replay across all 5 policies and 3 budgets shall execute in $< 15\,\text{seconds}$.

### 4.3 Data Security & Code Integrity
- **NFR-SEC-01:** No external API keys, database credentials, or proprietary telemetry endpoints are required or permitted in the repository.
- **NFR-SEC-02:** Raw government data in `data/raw/` must remain immutable. Processed artifacts shall be written to `data/processed/` and `results/`.

---

## 5. Acceptance Criteria (AC)

- **AC-01 (Data Reproducibility):** Ingesting raw NWMP files produces exactly 222 recurring stations and filters to exactly 172 river stations without manual overrides.
- **AC-02 (Temporal Isolation):** Automated tests prove that zero records from September 2025 are passed to feature engineering or policy scoring functions.
- **AC-03 (Budget Exactness):** Every policy returns exactly $B$ unique stations for $B \in \{10, 20, 40\}$.
- **AC-04 (Result Fidelity):** On the 172-station river cohort, the nominal replay reproduces the established empirical findings:
  - $B=10$: Risk $+7.1\%$, Change $+6.1\%$, R×C $+6.8\%$
  - $B=20$: Risk $+10.6\%$, Change $+24.7\%$, R×C $+13.4\%$
  - $B=40$: Risk $+13.2$, Change $+27.8\%$, R×C $+14.8\%$
- **AC-05 (Holdout Validation):** Cross-parameter holdout executes across all 4 folds and logs positive transfer across folds.
- **AC-06 (Randomization Verification):** District-matched randomization diagnostics evaluate 3,000 portfolios and confirm that Change and Risk×Change outperform geographically matched random portfolios with empirical diagnostic tail proportions $\hat{q}_{\text{diag}} \le 0.022$ at $B=10$ and $\hat{q}_{\text{diag}} \le 0.004$ at $B=20$, without claiming asymptotic inferential significance on dependent stations.
- **AC-07 (Stress Reproducibility):** Station-loss and missing-data stress simulations execute 200 replicates and demonstrate the divergence between Clean Winner (Change) and Robust Winner (Risk).
- **AC-08 (Decision Gate Operation):** The decision gate outputs valid enum states (`TRUST`, `CONDITIONAL`, `ABSTAIN`) and triggers `ABSTAIN` when synthetic severe noise is injected.
- **AC-09 (Test Coverage):** Pytest test suite executes and passes $100\%$ of unit and integration tests.
- **AC-10 (Demo Readiness):** Streamlit application launches without error via `streamlit run app.py` and provides immediate interactive navigation across all 8 views in Demo Mode.
