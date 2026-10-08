# 03_SCIENTIFIC_SPEC.md — Scientific & Mathematical Specification

## 1. Mathematical Formalism & Notation

Let the monitoring network be represented as a set of $N$ recurring stations:
$$\mathcal{N} = \{1, 2, \dots, N\}, \quad |\mathcal{N}| = N = 172 \text{ (primary river cohort)}$$
Let the monitored water-quality parameters be indexed by $\mathcal{P}$:
$$\mathcal{P} = \{1, 2, \dots, P\}, \quad |\mathcal{P}| = P = 12$$
Let the discrete monthly observation epochs be:
$$t \in \{\text{Jul}, \text{Aug}, \text{Sep}\}$$
where $y_{i, p}^t \in \mathbb{R}$ represents the observed value of parameter $p$ at station $i$ in month $t$.

The operational sampling budget is denoted by $B \in \{10, 20, 40\}$, where $B \ll N$.

A station-selection policy $\pi$ is a mapping from historical information $\mathcal{H}$ to a subset of chosen monitoring stations $\mathcal{S}_B^\pi \subset \mathcal{N}$ of cardinality exactly $B$:
$$\pi: \mathcal{H} \times B \rightarrow \mathcal{S}_B^\pi \quad \text{s.t.} \quad |\mathcal{S}_B^\pi| = B$$

---

## 2. Temporal Partitioning & Leakage Barrier

### 2.1 Information States
The universe of observations is partitioned strictly into two non-overlapping information states:
1. **Historical Information Window ($\mathcal{H}$):**
   $$\mathcal{H} = \{y_{i, p}^t \mid i \in \mathcal{N}, p \in \mathcal{P}, t \in \{\text{Jul}, \text{Aug}\}\}$$
2. **Hidden Future Epoch ($\mathcal{F}$):**
   $$\mathcal{F} = \{y_{i, p}^{\text{Sep}} \mid i \in \mathcal{N}, p \in \mathcal{P}\}$$

### 2.2 Strict Anti-Leakage Invariant
Let $\mathcal{A}$ represent any algorithmic operation (scoring, ranking, parameter estimation, standard deviation computation, scaling, imputation, or clustering).
$$\mathcal{A} \text{ operating during policy construction} \implies \mathcal{A} \subseteq \sigma(\mathcal{H})$$
Under no circumstances may any statistic $\theta(\mathcal{F})$ enter the generation of $\mathcal{S}_B^\pi$. Any code violation of this property invalidates the scientific evaluation.

---

## 3. Historical Scaling & Normalization

To allow scale-invariant aggregation across disparate parameters (e.g., pH in $[6, 9]$ vs Fecal Coliform in $[10^1, 10^5]$), all parameters are normalized using pre-September statistics.

### 3.1 Historical Scale Factor ($\sigma_p^{\text{hist}}$)
For each parameter $p \in \mathcal{P}$, the historical scale factor is defined as the sample standard deviation of cross-station values observed during the historical window:
$$\mu_p^{\text{hist}} = \frac{1}{2N} \sum_{i \in \mathcal{N}} \sum_{t \in \{\text{Jul}, \text{Aug}\}} y_{i, p}^t$$
$$\sigma_p^{\text{hist}} = \sqrt{\frac{1}{2N - 1} \sum_{i \in \mathcal{N}} \sum_{t \in \{\text{Jul}, \text{Aug}\}} (y_{i, p}^t - \mu_p^{\text{hist}})^2}$$
If $\sigma_p^{\text{hist}} = 0$ (degenerate parameter), $\sigma_p^{\text{hist}}$ is set to $1.0$.

---

## 4. Policy Arena Formulations

### 4.1 Policy 1: Uniform Random Baseline ($\pi_{\text{rnd}}$)
Given a pseudo-random number generator initialized with seed $s$, select a uniform random subset:
$$\mathcal{S}_B^{\text{rnd}} \sim \text{UniformChoice}(\mathcal{N}, B; s)$$
For diagnostic stability, random baselines can be computed over $M = 100$ repetitions, and the expected error $\bar{e}_{\text{rnd}}$ is used as the denominator for improvement metrics.

### 4.2 Policy 2: Risk-First Selection ($\pi_{\text{risk}}$)
Prioritizes stations with historically severe water-quality degradation.
For each parameter $p \in \mathcal{P}$, define a normalized directional risk indicator $r_{i, p}$:
- **Pollutants where high values indicate degradation** ($\mathcal{P}_{\text{pollutant}} = \{\text{BOD, COD, Fecal Coliform, Total Coliform, Nitrate N, Amonia N, Turbidity, Phosphate, TDS, Conductivity}\}$):
  $$r_{i, p} = \max\left(0, \frac{y_{i, p}^{\text{Aug}} - \mu_p^{\text{hist}}}{\sigma_p^{\text{hist}}}\right)$$
- **Dissolved Oxygen (DO), where low values indicate hypoxia**:
  $$r_{i, \text{DO}} = \max\left(0, \frac{\mu_{\text{DO}}^{\text{hist}} - y_{i, \text{DO}}^{\text{Aug}}}{\sigma_{\text{DO}}^{\text{hist}}}\right)$$
- **pH, where deviations from neutral (7.0) indicate chemical stress**:
  $$r_{i, \text{pH}} = \frac{|y_{i, \text{pH}}^{\text{Aug}} - 7.0|}{\sigma_{\text{pH}}^{\text{hist}}}$$

The composite risk score for station $i$ is:
$$R_i = \frac{1}{|\mathcal{P}|} \sum_{p \in \mathcal{P}} r_{i, p}$$
The policy selects the $B$ stations with the highest composite risk:
$$\mathcal{S}_B^{\text{risk}} = \operatorname{arg top-B}_{i \in \mathcal{N}}(R_i)$$

### 4.3 Policy 3: Temporal Change Selection ($\pi_{\text{chg}}$)
Prioritizes stations exhibiting the largest absolute temporal movement between July and August:
$$\delta_{i, p}^{\text{hist}} = \frac{|y_{i, p}^{\text{Aug}} - y_{i, p}^{\text{Jul}}|}{\sigma_p^{\text{hist}}}$$
$$C_i = \frac{1}{|\mathcal{P}|} \sum_{p \in \mathcal{P}} \delta_{i, p}^{\text{hist}}$$
The policy selects:
$$\mathcal{S}_B^{\text{chg}} = \operatorname{arg top-B}_{i \in \mathcal{N}}(C_i)$$

### 4.4 Policy 4: Spatial Coverage Selection ($\pi_{\text{cov}}$)
Prioritizes spatial and administrative dispersion to avoid localized sensor clustering.
Stations are partitioned across administrative districts $\mathcal{D}$. The algorithm iterates round-robin across districts sorted by unmonitored station count, selecting the station that maximizes the minimum geographic distance (Euclidean distance on normalized latitude/longitude) to already selected stations:
$$i^* = \operatorname{arg max}_{i \in \mathcal{N} \setminus \mathcal{S}} \min_{j \in \mathcal{S}} \|\mathbf{x}_i - \mathbf{x}_j\|_2$$
until $|\mathcal{S}| = B$.

### 4.5 Policy 5: Risk × Change Selection ($\pi_{\text{r}\times\text{c}}$)
Balances degradation severity with temporal rate of change.
Let $\text{rank}(R_i) \in [1, N]$ and $\text{rank}(C_i) \in [1, N]$ be the ordinal ranks of stations under the Risk and Change policies respectively (where rank $N$ is highest).
The composite score is defined as:
$$S_i^{\text{r}\times\text{c}} = \frac{\text{rank}(R_i)}{N} \times \frac{\text{rank}(C_i)}{N}$$
$$\mathcal{S}_B^{\text{r}\times\text{c}} = \operatorname{arg top-B}_{i \in \mathcal{N}}(S_i^{\text{r}\times\text{c}})$$

---

## 5. Reconstruction Model & Evaluation Metrics

### 5.1 Persistence Baseline Reconstruction
In an operational monitoring network where only $B$ stations are sampled at epoch $t = \text{Sep}$, the monitoring agency retains the prior month's observation for unsampled stations:
$$\hat{y}_{i, p}^{\text{Sep}}(\mathcal{S}_B) = \begin{cases} 
y_{i, p}^{\text{Sep}} & \text{if } i \in \mathcal{S}_B \text{ (station sampled)} \\ 
y_{i, p}^{\text{Aug}} & \text{if } i \notin \mathcal{S}_B \text{ (station unsampled, persistence)} 
\end{cases}$$

### 5.2 Residual Error Formulation
The reconstruction error for station $i$ and parameter $p$ is:
$$\epsilon_{i, p}(\mathcal{S}_B) = |y_{i, p}^{\text{Sep}} - \hat{y}_{i, p}^{\text{Sep}}(\mathcal{S}_B)| = \begin{cases} 
0 & \text{if } i \in \mathcal{S}_B \\ 
|y_{i, p}^{\text{Sep}} - y_{i, p}^{\text{Aug}}| & \text{if } i \notin \mathcal{S}_B 
\end{cases}$$

### 5.3 Standardized Network Residual Error ($e_\pi$)
The primary evaluation metric aggregates standardized absolute residuals across the entire evaluation network $\mathcal{N}$ and all parameters $\mathcal{P}$:
$$e(\mathcal{S}_B) = \frac{1}{|\mathcal{N}| |\mathcal{P}|} \sum_{i \in \mathcal{N}} \sum_{p \in \mathcal{P}} \frac{|y_{i, p}^{\text{Sep}} - \hat{y}_{i, p}^{\text{Sep}}(\mathcal{S}_B)|}{\sigma_p^{\text{hist}}}$$
**Property:** $e(\mathcal{S}_B)$ is strictly non-negative; lower is better. Zero error is achieved if and only if $B = N$.

### 5.4 Primary Headline Metric: Improvement vs Random ($\Delta_\pi$)
$$\Delta_\pi = \frac{\bar{e}_{\text{rnd}} - e(\mathcal{S}_B^\pi)}{\bar{e}_{\text{rnd}}} \times 100\%$$
where $\bar{e}_{\text{rnd}}$ is the expected residual error under uniform random sampling. Positive $\Delta_\pi$ indicates that policy $\pi$ preserves more network information than random allocation.

---

## 6. Multi-Layer Validation Protocols

### 6.1 4-Fold Cross-Parameter Holdout
The 12 parameters are partitioned into 4 disjoint groups of 3:
- **Fold 1:** $\mathcal{P}_{\text{test}}^{(1)} = \{\text{Dissolved O2, pH, BOD}\}$
- **Fold 2:** $\mathcal{P}_{\text{test}}^{(2)} = \{\text{Conductivity, Nitrate N, Fecal Coliform}\}$
- **Fold 3:** $\mathcal{P}_{\text{test}}^{(3)} = \{\text{Total Coliform, Turbidity, COD}\}$
- **Fold 4:** $\mathcal{P}_{\text{test}}^{(4)} = \{\text{Amonia N, Total Dissolved Solids, Phosphate}\}$

For each fold $k \in \{1, 2, 3, 4\}$:
1. Define training parameters: $\mathcal{P}_{\text{train}}^{(k)} = \mathcal{P} \setminus \mathcal{P}_{\text{test}}^{(k)}$.
2. Construct policy scores and select station subset $\mathcal{S}_{B, (k)}^\pi$ using **only** $\mathcal{P}_{\text{train}}^{(k)}$ over July and August.
3. Reveal September data **only** for $\mathcal{P}_{\text{test}}^{(k)}$.
4. Compute holdout network error:
   $$e_{\text{holdout}}^{(k)}(\mathcal{S}_{B, (k)}^\pi) = \frac{1}{|\mathcal{N}| |\mathcal{P}_{\text{test}}^{(k)}|} \sum_{i \in \mathcal{N}} \sum_{p \in \mathcal{P}_{\text{test}}^{(k)}} \frac{|y_{i, p}^{\text{Sep}} - \hat{y}_{i, p}^{\text{Sep}}(\mathcal{S}_{B, (k)}^\pi)|}{\sigma_p^{\text{hist}}}$$
5. Calculate holdout improvement relative to matched random sampling on the same held-out parameters.

### 6.2 District-Matched Randomization Diagnostics
To verify that policy superiority is not a trivial artifact of geographical over-sampling in volatile districts:
1. Compute the district allocation vector for candidate policy selection $\mathcal{S}_B^\pi$:
   $$\mathbf{d}_\pi = [d_1, d_2, \dots, d_{|\mathcal{D}|}], \quad \sum d_j = B$$
   where $d_j$ is the count of selected stations in district $j$.
2. Generate $K = 3,000$ independent random station portfolios $\mathcal{S}_{\text{matched}}^{(k)}$ that draw exactly $d_j$ stations uniformly at random from district $j$.
3. Compute the distribution of residual errors: $\{e(\mathcal{S}_{\text{matched}}^{(k)})\}_{k=1}^K$.
4. Calculate the empirical randomization diagnostic tail proportion:
   $$\hat{q}_{\text{diag}} = \frac{1}{K} \sum_{k=1}^K \mathbb{I}\left(e(\mathcal{S}_{\text{matched}}^{(k)}) \le e(\mathcal{S}_B^\pi)\right)$$

**Statistical Non-Equivalence Caveat:** $\hat{q}_{\text{diag}}$ is an empirical randomization diagnostic, **NOT** an asymptotic hypothesis testing $p$-value. Because environmental stations along hydrologic reaches exhibit spatial network autocorrelation and multi-month serial correlation, observations violate the independent and identically distributed (i.i.d.) assumption. WATERSHIELD presents $\hat{q}_{\text{diag}}$ strictly as an empirical spatial diagnostic without claiming formal inferential statistical significance.

---

## 7. Controlled Stress Testing Formulations

### 7.1 Station Availability Failure
Simulates equipment malfunction, physical inaccessibility, or communication link loss. Note: this is a controlled synthetic simulation to evaluate robustness boundaries, not an empirical record of real-world historical outage rates.
- Given selected policy set $\mathcal{S}_B^\pi$, randomly drop a fraction $\alpha \in \{0.10, 0.20, 0.30, 0.40, 0.50\}$ of selected stations.
- For dropped stations $j \in \mathcal{S}_{\text{failed}} \subset \mathcal{S}_B^\pi$, measurement fails and reverts to the August persistence baseline.
- Evaluate over $M = 200$ Monte Carlo replicates:
  $$e_{\text{stress}}(\pi; \alpha) = \mathbb{E}_{\mathcal{S}_{\text{failed}}} \left[ e\left(\mathcal{S}_B^\pi \setminus \mathcal{S}_{\text{failed}}\right) \right]$$

### 7.2 Input Missing-Data Perturbation
Simulates degraded telemetry or laboratory delays during the decision window.
- In the historical August inputs, introduce missingness at rate $\beta \in \{0.10, 0.20, 0.30\}$ completely at random.
- Apply median-centered column imputation using historical distributions.
- Run policy selection on perturbed inputs and measure out-of-sample September error against ground truth over $M = 200$ replicates.

---

## 8. Decision Gate Engine Logic

The decision gate executes explicit logical rules to issue an operational audit verdict:

```text
IF min_k(Delta_holdout(k)) < 0.0 OR Delta_nominal < 3.0%:
    VERDICT = ABSTAIN (Reason: Failed independent parameter generalization or negligible advantage)
ELIF rank_inversion_under_stress(alpha=0.20) IS TRUE:
    VERDICT = CONDITIONAL (Reason: Policy ranking sensitive to station dropout; Robust Winner differs from Clean Winner)
ELIF q_diag > 0.05:
    VERDICT = CONDITIONAL (Reason: Geographic clustering explains policy advantage)
ELSE:
    VERDICT = TRUST (Reason: Robust outperformance across replay, holdout, randomization, and stress)
```

### Clean Winner vs Robust Winner
- **Clean Winner ($\pi^*$):**
  $$\pi^* = \operatorname{arg max}_{\pi} \Delta_\pi(\text{nominal})$$
- **Robust Winner ($\pi_{\text{rob}}^*$):**
  $$\pi_{\text{rob}}^* = \operatorname{arg min}_{\pi} \left[ e_{\text{stress}}(\pi; \alpha = 0.30) \right]$$
When $\pi^* \ne \pi_{\text{rob}}^*$, the system flags a **Regime Split** and downgrades the recommendation to **CONDITIONAL**, specifying the operational condition required for each policy.

---

## 9. Failure Boundary Identification

The failure boundary $\alpha^*$ is defined as the critical stress level at which policy $\pi$ loses its statistical advantage over random sampling:
$$\alpha^* = \inf \left\{ \alpha \in [0, 1] \mid e_{\text{stress}}(\pi; \alpha) \ge \bar{e}_{\text{rnd}} \right\}$$
The UI dynamically categorizes operating zones:
- $[0, 0.15]$: **STRONG OPERATIONAL ZONE**
- $[0.15, \alpha^*]$: **CONDITIONAL OPERATIONAL ZONE**
- $> \alpha^*$: **UNACCEPTABLE / REJECT ZONE**
