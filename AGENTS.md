# AGENTS.md — Instructions & Rules for AI Coding Agents

## Project Identity & Mandate
**WATERSHIELD: Water Monitoring Policy Reliability & Decision-Audit Engine**
Core Question: *"Which monitoring policy should we trust when we cannot monitor everything?"*
Core Principle: **"Don't trust the optimizer. Test the policy."**

You are operating as an engineering and scientific agent on the WATERSHIELD codebase. All modifications must adhere strictly to the rules, scientific specifications, and architectural boundaries set forth in this document and the `docs/` repository.
WATERSHIELD is a controlled scientific software project.

Antigravity may implement, refactor, test, and improve code within the approved specification.

Antigravity must not independently change:

the scientific objective,
evaluation methodology,
dataset definitions,
policy definitions,
experimental budgets,
validation methodology,
empirical results,
research claims,
novelty claims,
product scope,
or decision-gate semantics.

If implementation reveals a genuine ambiguity, inconsistency, missing dependency, or scientifically consequential design choice, STOP and report it instead of guessing.

Existing documentation is the source of truth.

Experimental results must come from executed experiments.

The UI must never fabricate scientific evidence.

No fake data.

No fake results.

No hardcoded experimental outcomes.

No invented citations.

No silent methodology changes.

No unnecessary feature expansion.

Implement the approved system. Do not redesign the research while coding it.

---

## 1. Prime Directives & Anti-Hallucination Rules
1. **Never Invent Data or Results:** Never fabricate numbers, stations, coordinates, parameters, baseline errors, holdout scores, or stress performance metrics. All numbers presented in the UI or documentation must originate from verified data or reproducible execution of the scientific engine.
2. **Never Silently Modify Science:** Do not change mathematical definitions, policy formulas, baseline reconstruction logic, residual error formulas, holdout partitions, or decision gate rules without explicit authorization.
3. **Never Add Scope:** Do not introduce LLMs, chatbots, multi-agent swarms, fake IoT sensors, blockchain, digital twins, or rainwater harvesting (RS-7). Keep the product focused on being an **independent policy-audit layer**.
4. **Enforce Leakage Prevention:** In any temporal replay experiment, future observations (September 2025) must remain strictly hidden during station selection and policy construction. September data must never influence normalization, scaling, ranking, or threshold tuning.
5. **No Magic Numbers:** All hyperparameters, weights, stress percentages, and decision thresholds must reside in centralized configuration (`src/config.py`).
6. **No Duplicated Science:** The frontend must never calculate scientific metrics or policy selections. The backend scientific engine is authoritative; the frontend consumes structured result artifacts.
7. **No Unsupported Inferential Claims:** Repeated station observations along river reaches are spatially and serially dependent. District-matched randomization diagnostics evaluate exactly 3,000 portfolios and represent empirical diagnostic tail proportions ($\hat{q}_{\text{diag}}$), NOT formal asymptotic hypothesis-test p-values. Never claim `p < 0.001`, statistical significance, or formal inferential certainty.
8. **Controlled Simulations vs Real-World Outages:** Synthetic missingness and station-dropout tests are controlled stress simulations to evaluate algorithmic robustness boundaries, not empirical evidence that real-world networks fail at these exact rates.
9. **No Hardcoded Scientific Outputs:** Empirical results must originate from experiment artifact files (`results/`), never hardcoded into computation logic or UI templates.

---

## 2. Classification of Information
When discussing or implementing features, strictly maintain these categories:
- **FACT:** Verified, empirical truth from data (e.g., exactly 222 recurring stations, 172 river stations, July duplicate file).
- **RESULT:** Numerically validated experiment outcome from the approved protocol.
- **DECISION:** Settled architectural or methodological choice (e.g., river-only primary cohort, 5 primary policies, 4-fold holdout).
- **ASSUMPTION:** Documented working assumption (e.g., unsampled station maintains previous month's value).
- **PROVISIONAL:** Intermediate or exploratory finding pending full pipeline validation.
- **REJECTED:** Explicitly excluded concepts (e.g., standalone Uncertainty policy, arbitrary weighted reliability score, RS-7).
- **FUTURE:** Out-of-scope extensions (e.g., multi-year data, real-time streams, downstream decision VoI).

---

## 3. Approved Claims Policy
- **Permitted Phrases:**
  - *"In our retrospective evaluation..."*
  - *"On the 172-station river cohort..."*
  - *"Under the July/August → September replay..."*
  - *"In our controlled station-loss simulation..."*
  - *"Compared with matched random portfolios..."*
  - *"Under the tested conditions..."*
- **Strictly Prohibited Phrases:**
  - *"Guaranteed optimal monitoring"*
  - *"Real-time contamination prevention"*
  - *"Government-ready / Officially adopted"*
  - *"Statistically significant"* (until formal dependence-aware inference is validated)
  - *"World's first / Nobody has done this"*

---

## 4. Coding & Architectural Standards
- **Language & Environment:** Python 3.11+, typed, modular, clean docstrings.
- **Stack:** pandas, numpy, scipy, scikit-learn, plotly, streamlit, pytest.
- **Separation of Concerns:**
  - `src/data/`: Data ingestion, validation, alignment, feature construction.
  - `src/policies/`: Standardized, deterministic policy implementations (`select_stations`).
  - `src/replay/`: Temporal replay and standardized network residual metrics.
  - `src/validation/`: Cross-parameter holdout, district-matched randomization.
  - `src/stress/`: Controlled station availability failure, missing data perturbation.
  - `src/decision/`: Evidence-based reliability gate (TRUST / CONDITIONAL / ABSTAIN), failure boundaries.
  - `pages/` & `app.py`: Streamlit presentation consuming backend artifacts.
- **Deterministic Reproducibility:** Every policy selection and randomization simulation must accept and enforce an explicit `seed`.
- **Precomputed Artifacts vs Live Execution:** Support both **Experiment Mode** (runs pipeline end-to-end) and **Demo Mode** (loads precomputed, validated scientific artifacts for fast, glitch-free presentation).

---

## 5. Agent Workflow & Verification
Before claiming any task is done:
1. Verify against `docs/03_SCIENTIFIC_SPEC.md` and `docs/02_REQUIREMENTS.md`.
2. Run automated tests with `pytest`.
3. Verify that temporal leakage tests pass.
4. Confirm no unexplained constants or hardcoded fake data in the UI.
5. Update documentation if any structural change was made.
