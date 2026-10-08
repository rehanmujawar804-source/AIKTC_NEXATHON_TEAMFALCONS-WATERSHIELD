# 07_ROADMAP.md — Build Roadmap, Risk Register & Definition of Done

## 1. Project Roadmap & Build Phases

The implementation of WATERSHIELD follows a strict phased pipeline where empirical and scientific validity precede frontend visual presentation.

```text
PHASE 0: Documentation & Governance [COMPLETED]
    ↓
PHASE 1: Raw Data Ingestion & Deduplication
    ↓
PHASE 2: Data Pipeline & State Preparation (src/data/)
    ↓
PHASE 3: Policy Arena Implementation (src/policies/)
    ↓
PHASE 4: Temporal Replay & Leakage Barrier (src/replay/)
    ↓
PHASE 5: Validation Lab (Holdout & Randomization) (src/validation/)
    ↓
PHASE 6: Controlled Stress Lab (src/stress/)
    ↓
PHASE 7: Decision Gate & Failure Boundary (src/decision/)
    ↓
PHASE 8: Authoritative Experiment Runner & Artifacts (scripts/, results/)
    ↓
PHASE 9: Operational Decision Console Frontend (app.py, src/ui/)
    ↓
PHASE 10: Automated Verification Suite (tests/)
    ↓
PHASE 11: Demo Hardening & Rehearsal
```

---

## 2. Phase Breakdown & Deliverables

### Phase 0: Project Constitution & Documentation (Completed)
- **Deliverables:** `AGENTS.md` and `docs/01_MASTER_PROJECT.md` through `07_ROADMAP.md`.
- **Milestone:** Architecture and scientific specifications frozen.

### Phase 1: Environment Setup & Raw Data Ingestion
- **Deliverables:** 
  - Install dependencies (`requirements.txt` containing pandas, numpy, scipy, scikit-learn, plotly, streamlit, pytest).
  - Mirror verified NWMP raw CSV files to `data/raw/`.
  - Verify bit-for-bit SHA-256 duplicate July file.

### Phase 2: Data Pipeline & State Preparation
- **Deliverables:**
  - `src/config.py`: Centralized configuration.
  - `src/data/loader.py`: Cryptographic deduplication and ingestion.
  - `src/data/cleaning.py`: Parameter sanitization and numeric conversion.
  - `src/data/alignment.py`: Extraction of 222 recurring stations and 172 river cohort.
  - `src/data/features.py`: Computation of historical scaling parameters ($\mu_p^{\text{hist}}, \sigma_p^{\text{hist}}$).
  - `scripts/prepare_data.py`: CLI script generating processed parquets.

### Phase 3: Policy Arena
- **Deliverables:**
  - `src/policies/base.py`: Abstract contract enforcing uniform interface.
  - Implement `RandomPolicy`, `RiskPolicy`, `ChangePolicy`, `CoveragePolicy`, `RiskChangePolicy`.
  - Assert deterministic selection given seed and exact budget enforcement ($B \in \{10, 20, 40\}$).

### Phase 4: Temporal Replay & Leakage Prevention
- **Deliverables:**
  - `src/replay/baseline.py`: Persistence reconstruction logic.
  - `src/replay/temporal_replay.py`: Information isolation protocol.
  - `src/replay/metrics.py`: Standardized network residual error and improvement vs random.
  - Unit tests asserting zero September data leakage.

### Phase 5: Validation Lab
- **Deliverables:**
  - `src/validation/parameter_holdout.py`: 4-fold cross-parameter holdout pipeline.
  - `src/validation/district_randomization.py`: 3,000-replicate district-matched randomization engine.
  - `src/validation/sensitivity.py`: Parameter subset stability audits.

### Phase 6: Controlled Failure Stress Lab
- **Deliverables:**
  - `src/stress/station_failure.py`: Monte Carlo simulation of station dropouts ($10\% - 50\%$).
  - `src/stress/missing_data.py`: Perturbation of historical August inputs with median imputation.

### Phase 7: Decision Gate & Failure Boundary
- **Deliverables:**
  - `src/decision/reliability.py`: Deterministic multi-layer rules issuing `TRUST`, `CONDITIONAL`, or `ABSTAIN`.
  - `src/decision/failure_boundary.py`: Delineation of Strong, Conditional, and Reject operating zones.
  - `src/decision/recommendation.py`: Clean Winner vs Robust Winner reporting.

### Phase 8: Authoritative Runner & Results Serialization
- **Deliverables:**
  - `scripts/run_experiments.py`: One-command execution of all scientific evaluations.
  - Structured, validated JSON artifacts stored in `results/`.

### Phase 9: Decision Console Frontend
- **Deliverables:**
  - `app.py`: Streamlit entry point.
  - 8 core product views in `src/ui/`: Decision Console, Policy Arena, Replay, Stress Lab, Failure Map, Stations, Data Integrity, Evidence.
  - Demo Mode (instant artifact loading) and Experiment Mode (live computation).

### Phase 10: Testing Suite & Quality Assurance
- **Deliverables:**
  - Comprehensive pytest suite across all modules with $100\%$ pass rate.
  - Verification of no magic numbers or fake mock data.

### Phase 11: Demo Hardening & Rehearsal
- **Deliverables:**
  - End-to-end execution walkthrough.
  - Competitive judge defense preparation.

---

## 3. Definition of Done (DoD)

The project is complete and ready for submission when and only when:
1. **Data Invariant:** Raw NWMP datasets load reproducibly; SHA-256 duplicate check executes; exactly 222 recurring stations align; exactly 172 river stations are filtered.
2. **Scientific Invariant:** Policies produce exact budget selections; no September future data leaks into policy construction; nominal replay reproduces published empirical improvements.
3. **Validation Invariant:** 4-fold holdout confirms positive transfer; district-matched randomization diagnostics evaluate 3,000 portfolios and confirm spatial distinctness without claiming asymptotic inferential p-values.
4. **Stress Invariant:** Station loss and missingness simulations demonstrate the divergence between Clean Winner and Robust Winner.
5. **Decision Invariant:** The decision gate issues `TRUST`, `CONDITIONAL`, or `ABSTAIN` based on transparent rules; boundary analysis determines operational safety limits.
6. **Product Invariant:** Streamlit application renders all 8 core views flawlessly in dark operational aesthetic with $<500\text{ms}$ latency in Demo Mode.
7. **Engineering Invariant:** All automated tests in `tests/` pass with zero failures.

---

## 4. Risk Register & Mitigation Strategy

| Risk ID | Description | Severity | Likelihood | Mitigation Strategy |
|---|---|---|---|---|
| **R-01** | Future data leakage into policy scoring | Critical | Low | Strict architectural decoupling: `HistoricalState` object passed to policies; automated unit test verifying September tampering fails to alter selections. |
| **R-02** | Presentation latency during live competition demo | High | Med | Implement Demo Mode loading precomputed scientific JSON artifacts directly from `results/`. |
| **R-03** | Judge attacks on lack of long-term data | High | Med | Transparent scientific positioning: clearly state 3-month retrospective prototype scope; emphasize empirical audit protocol over long-term claims. |
| **R-04** | Accidental use of unstable features (`Use Based Class`) | High | Low | Pipeline schema validation drops `Use Based Class` at ingestion; unit tests assert only core 12 parameters used. |
| **R-05** | Accidental double-counting of duplicate July datasets | High | Low | Cryptographic hash check in `loader.py` automatically ignores redundant duplicate file. |

---

## 5. Competition Demo Narrative (Walkthrough Script)

1. **Step 1: Set the Problem (Decision Console):**
   - *"We have 172 recurring river monitoring stations in Maharashtra, but our logistics and laboratory budget only allow sampling 20 stations ($B=20$)."*
2. **Step 2: Introduce the Competing Policies (Policy Arena):**
   - *"Five policies compete: Random, Risk, Change, Coverage, and Risk × Change. Which one should we trust?"*
3. **Step 3: Reveal Hidden Replay (Replay View):**
   - *"We freeze all policy selections using July and August data, keeping September strictly hidden. When September is revealed, Change Policy reduces network residual error by $+24.7\%$ vs random. But can we trust this nominal winner?"*
4. **Step 4: Audit Generalization (Evidence & Holdout):**
   - *"We run a 4-fold cross-parameter holdout on excluded parameters and district-matched randomization (diagnostic tail proportion $\hat{q}_{\text{diag}} \le 0.001$ over 3,000 draws). The advantage transfers."*
5. **Step 5: Attack with Infrastructure Failure (Stress Lab & Failure Map):**
   - *"Now we stress-test: what if $20\%$ to $30\%$ of sampled stations fail or telemetry drops out? Under stress, the Clean Winner (Change) degrades, and Risk Policy becomes the Robust Winner!"*
6. **Step 6: Deliver Decision (Decision Console):**
   - *"WATERSHIELD does not blindly force an optimizer. It issues an audited verdict: CONDITIONAL. Trust Change if station availability is $>80\%$; switch to Risk if failure risk increases."*
   - **Closing Motto:** *"Don't trust the optimizer. Test the policy."*
