# 05_PRODUCT_UI_UX.md — Product UI & UX Design Blueprint

## 1. Product Experience & Visual Design Direction

### 1.1 Persona & Aesthetic Goal
WATERSHIELD is an **operational decision-audit system** designed for environmental regulatory authorities, scientific review panels, and hackathon judges. 

It is emphatically **not**:
- A generic student dashboard or AI chatbot wrapper.
- A superficial marketing analytics template filled with gratuitous stat cards.
- An uncalibrated real-time sensor platform or speculative optimizer.

The visual direction is a **restrained, technical, dark scientific console**: high evidentiary density, clear typographic hierarchy, subtle interactive elevation, and unambiguous decision governance.

### 1.2 Core Visual Hierarchy
The interface strictly enforces an evidentiary hierarchy:
```text
1. AUDIT VERDICT BADGE & OPERATIONAL BOUNDARY (TRUST / CONDITIONAL / ABSTAIN)
      ↓
2. HEADLINE METRICS (Standardized Residual Error, Improvement vs Random, Active Budget)
      ↓
3. EVIDENTIARY AUDIT PANELS (Temporal Replay, Holdout Folds, Matched Randomization, Stress Curves)
      ↓
4. GRANULAR DRILLDOWN & STATION ATTRIBUTION (Station-Level Residuals, Parameter Decompositions)
```

---

## 2. Design System & Style Tokens

### 2.1 Color Tokens & Semantic Surface Architecture
All colors are curated to ensure high contrast, readability, and WCAG 2.1 AA compliance:

| Token Name | Hex Code | Purpose / Application |
|---|---|---|
| `--color-bg-base` | `#0B0E14` | Deep canvas background |
| `--color-bg-surface` | `#161B22` | Panel, sidebar, and container background |
| `--color-bg-elevated` | `#21262D` | Cards, modal surfaces, table headers |
| `--color-bg-hover` | `#30363D` | Interactive hover states |
| `--color-border-subtle` | `#30363D` | Default panel and card borders |
| `--color-border-focus` | `#58A6FF` | Keyboard focus ring and active inputs |
| `--color-text-primary` | `#F0F6FC` | High-contrast body text and titles |
| `--color-text-secondary` | `#C9D1D9` | Supporting descriptions, metadata labels |
| `--color-text-muted` | `#8B949E` | Footnotes, disabled text, units |
| `--color-verdict-trust` | `#2EA043` | TRUST status badge & accents |
| `--color-verdict-cond` | `#D29922` | CONDITIONAL status badge & accents |
| `--color-verdict-abstain`| `#DA3633` | ABSTAIN status badge & accents |
| `--color-accent-primary` | `#388BFD` | Primary selection toggles, interactive triggers |

#### Multi-Modal Verdict Rule:
**Never rely on color alone.** Every verdict must display:
1. Distinct semantic icon (`✓ [TRUST]`, `⚠ [CONDITIONAL]`, `⛛ [ABSTAIN]`).
2. High-contrast textual label in uppercase.
3. Explicit audit rationale explaining the governing condition.

### 2.2 Data Visualization Palette
Fixed, colorblind-distinguishable categorical palette for the 5 competing policies:
- **Random Baseline ($\pi_{\text{rnd}}$):** Neutral Slate Gray (`#6E7681`) — dashed stroke.
- **Risk Policy ($\pi_{\text{risk}}$):** Safety Amber / Ochre (`#F0883E`) — solid stroke.
- **Change Policy ($\pi_{\text{chg}}$):** Electric Scientific Blue (`#388BFD`) — solid stroke.
- **Coverage Policy ($\pi_{\text{cov}}$):** Emerald Mint (`#3FB950`) — solid stroke.
- **Risk × Change Policy ($\pi_{\text{r}\times\text{c}}$):** Royal Purple (`#BC8CFF`) — solid stroke.

### 2.3 Typography Scale
System font stack: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.  
Monospace stack (for numeric metrics, hashes, and station IDs): `"JetBrains Mono", SFMono-Regular, Menlo, Consolas, monospace`.

| Role | Font Size | Line Height | Weight | Letter Spacing |
|---|---|---|---|---|
| **H1 (View Title)** | `28px` (`1.75rem`) | `34px` | `700` (Bold) | `-0.02em` |
| **H2 (Section Header)** | `20px` (`1.25rem`) | `26px` | `600` (SemiBold) | `-0.01em` |
| **H3 (Card / Metric Title)** | `15px` (`0.9375rem`)| `20px` | `600` (SemiBold) | `0.0em` |
| **Body Primary** | `14px` (`0.875rem`) | `20px` | `400` (Regular) | `0.0em` |
| **Body Secondary** | `12px` (`0.75rem`) | `16px` | `400` (Regular) | `0.01em` |
| **Metric Hero Number** | `32px` (`2.0rem`) | `36px` | `700` (Mono) | `-0.03em` |
| **Micro Caption / Tag** | `11px` (`0.6875rem`)| `14px` | `500` (Medium, Tracked) | `0.04em` |

### 2.4 Spacing Scale
Consistent 4px/8px modular scale:
- `space-xs`: `4px` (input padding, badge margin)
- `space-sm`: `8px` (button gap, inline spacing)
- `space-md`: `16px` (container inner padding, card gap)
- `space-lg`: `24px` (section separation, panel margin)
- `space-xl`: `32px` (major block separation)
- `space-2xl`: `48px` (view top padding)

### 2.5 Reusable Component Library
1. **`.audit-card`:** Surface `#161B22`, border `1px solid #30363D`, radius `6px`, padding `16px`. Subtle hover elevation: border transitions to `#58A6FF` (150ms ease).
2. **`.metric-card`:** Surface `#21262D`, contains uppercase micro-label, 32px mono value, and delta comparison tag (`+24.7% vs random`).
3. **`.verdict-badge`:** Pill component with solid dark background, 1px semantic border, icon, and uppercase text.
4. **`.segmented-control`:** Horizontal button group for budget selection ($B \in \{10, 20, 40\}$) with active state in `#388BFD`.
5. **`.callout-banner`:** High-contrast contextual callout for warnings, methodology notes, and abstention notices.

### 2.6 Charting System & Theming Tokens
Plotly charts share a strict dark configuration:
- Background: Paper `#161B22`, Plot `#161B22`.
- Gridlines: `#21262D` (subtle 1px solid horizontal only; vertical disabled).
- Axes: Font size 12px, font color `#8B949E`, zero-line enabled.
- Margins: Compact `l=40, r=20, t=30, b=40`.
- Hoverlabel: Background `#21262D`, border `#58A6FF`, font family Mono, size 12px.
- Tooltip template: `<extra></extra><b>%{x}</b><br>Residual Error: <b>%{y:.3f}</b>`.
- Accessibility toggle: Every chart container includes an expandable *"View as Accessible Table"* toggle.

### 2.7 Map Styling & Fallback Specification
- **Purpose:** Spatial inspection of station distributions across Maharashtra river basins.
- **Data Source:** Station latitude/longitude from validated NWMP metadata (`data/processed/river_cohort_172.parquet`).
- **Engine:** Plotly Scattermapbox or Cartesian Scatter (`longitude` vs `latitude`).
- **Tile Layer:** Carto-Positron Dark (open, no proprietary token required). Center: `[19.75, 75.71]`, Zoom: `6.0`.
- **Marker Styling:** Selected stations (Cyan, size 8, opacity 0.9); unselected stations (Slate Gray, size 4, opacity 0.4).
- **Graceful Fallback:** If internet access is unavailable or tile servers fail, the view automatically falls back to an offline Cartesian coordinate plot with district outlines. The product remains **100% functional without map tiles**.

---

## 3. Persistent Application Shell & Navigation

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  🛡️ WATERSHIELD   "Don't trust the optimizer. Test the policy."                        │
│  Dataset: NWMP Maharashtra | Cohort: 172 River Stations | Budget: [10][20][40] | Demo  │
└────────────────────────────────────────────────────────────────────────────────────────┘
│ Sidebar Nav:                                                                           │
│ [1. Decision Console] [2. Policy Arena] [3. Replay] [4. Stress Lab]                    │
│ [5. Failure Map]      [6. Stations]     [7. Data Integrity] [8. Evidence]              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Global Context Bar:**
  - **Cohort Selector:** `172 River Stations (Primary)` (active) | `222 Network Stations (Exploratory)`.
  - **Budget Selector:** `B = 10` | `B = 20` | `B = 40`.
  - **Runtime Switcher:** `Demo Mode (Verified)` | `Experiment Mode (Live)`.
  - **Verdict Indicator:** Dynamic badge reflecting the audit outcome for the selected budget.

---

## 4. View-by-View Functional Specifications

### 4.1 View 1: Decision Console (Primary Landing)
1. **User Question & Purpose:** *"Which monitoring policy should we trust under current operational constraints, and under what conditions does that trust terminate?"*
2. **Information Hierarchy:**
   - 1. Executive Verdict Card (Status + Clean Winner + Robust Winner + Operational Caveat).
   - 2. Headline Metric Trio (Nominal Baseline Error, Policy Error, % Improvement vs Random).
   - 3. Failure Boundary Summary Gauge.
   - 4. Quick Action Bar (Budget switch, Re-audit trigger).
3. **Components & Layout:**
   - Top Hero Banner: Core question in 20px semi-bold.
   - 2-Column Split: Left = Primary Verdict Card; Right = 3 Vertical Metric Cards.
   - Bottom Row: Operating Safety Zone bar and Clean vs Robust winner matrix.
4. **Available Interactions:**
   - Toggle budget selector ($B=10, 20, 40$) — instantaneously re-renders verdict and headline metrics.
   - Click *"Audit Details"* — navigates directly to View 8 (Evidence).
   - Click *"Inspect Selected Stations"* — filters View 6 (Stations) to the winner's chosen set.
5. **Data Source & Contract:** Consumes `results/decision/decision_audit.json` (`DecisionVerdict` dataclass).
6. **State Handling:**
   - *Loading:* Skeleton card pulse (200ms).
   - *Empty/Missing:* High-contrast alert prompting execution of `scripts/run_experiments.py`.
   - *Abstain State:* Displays prominent amber/red Decision Abstention Notice explaining why no policy is recommended.
7. **Responsive Behavior:** 2-column layout stacks vertically below 1024px.
8. **Accessibility:** Focus ring on budget buttons; table summary of metrics for screen readers.

---

### 4.2 View 2: Policy Arena
1. **User Question & Purpose:** *"How do all 5 candidate policies rank against the random baseline and each other across budgets?"*
2. **Information Hierarchy:**
   - 1. Comparative Leaderboard Table (Ranks, Policies, Residual Errors, % Improvements, District Spreads).
   - 2. Comparative Bar Chart with Random Reference Line.
   - 3. Multi-Budget Scaling Line Chart ($B=10 \rightarrow 20 \rightarrow 40$).
3. **Components & Layout:**
   - Top: Arena Leaderboard Table with sortable columns.
   - Bottom Left: Plotly Horizontal Bar Chart (Residual error by policy).
   - Bottom Right: Plotly Line Chart (Improvement trajectory across budgets).
4. **Available Interactions:**
   - Click on any policy row in the table to open an **In-Place Drawer** showing the exact station codes selected.
   - Hover over bar chart to view exact residual error and improvement delta.
   - Toggle budget switcher to watch rank re-ordering.
5. **Data Source & Contract:** Consumes `results/replay/nominal_results.json` (`ReplayResult` mapping).
6. **State Handling:**
   - *Success:* 5 policies displayed with clear error bars for random baseline.
   - *Error:* Notice if nominal replay artifact has invalid schema.
7. **Responsive Behavior:** Side-by-side charts stack on screens $<1024\text{px}$.
8. **Accessibility:** Table is navigable via keyboard arrow keys; ARIA sort attributes on headers.

---

### 4.3 View 3: Replay & Evidence
1. **User Question & Purpose:** *"How was the temporal evaluation conducted, and is it mathematically proven that future data remained strictly hidden?"*
2. **Information Hierarchy:**
   - 1. Visual Temporal Pipeline Timeline (July $\rightarrow$ August $\rightarrow$ [BARRIER] $\rightarrow$ Selection $\rightarrow$ September Revealed).
   - 2. Anti-Leakage Compliance Checklist (Verification of pre-September scaling).
   - 3. Parameter-Level Error Breakdown Chart.
   - 4. Station-Level Residual Distribution Histogram.
3. **Components & Layout:**
   - Top: 5-step horizontal graphical timeline.
   - Middle Left: Parameter Residual Bar Chart (comparing baseline vs winner parameter-by-parameter).
   - Middle Right: Station Residual Distribution Histogram.
   - Bottom: Expandable Parameter Drilldown Table.
4. **Available Interactions:**
   - Click on a parameter bar (e.g., `BOD` or `Dissolved O2`) to filter the station histogram to residuals for that parameter alone.
   - Expand *"Mathematical Model"* accordion to view exact baseline equations and normalization factors.
5. **Data Source & Contract:** Consumes `results/replay/nominal_results.json` (`parameter_errors` dictionary and `station_residuals` DataFrame).
6. **State Handling:**
   - *Success:* Clean timeline with verified green checkmarks on anti-leakage invariants.
7. **Responsive Behavior:** Horizontal timeline wraps gracefully into a vertical step-list on mobile/tablet ($<1024\text{px}$).
8. **Accessibility:** Textual transcript of timeline steps provided for screen readers.

---

### 4.4 View 4: Stress Lab
1. **User Question & Purpose:** *"What happens to policy reliability when stations fail or telemetry data is missing?"*
2. **Information Hierarchy:**
   - 1. Interactive Stress Slider Controls (Station Availability Loss $\alpha \in [0, 50\%]$; Missing Data $\beta \in [0, 30\%]$).
   - 2. Multi-Line Stress Trajectory Chart (Error vs Stress Level across all 5 policies).
   - 3. Winner Crossover Point Indicator (Clean Winner vs Robust Winner divergence).
   - 4. Synthetic Distinction Warning Callout.
3. **Components & Layout:**
   - Top: Dual interactive sliders + Seed indicator.
   - Center: Plotly line chart showing error degradation curves with shaded Monte Carlo confidence bands.
   - Bottom Callout: Explaining the crossover point where Risk policy overtakes Change policy.
4. **Available Interactions:**
   - Adjust station dropout slider ($\alpha$) — moves vertical indicator on chart and updates live Monte Carlo distribution metrics.
   - Toggle between *"Station Loss"* and *"Telemetry Missingness"* stress tabs.
   - Inspect individual Monte Carlo replicates via expandable quantile table.
5. **Data Source & Contract:** Consumes `results/stress/stress_results.json` (`StressCurvePoint` list across 200 replicates).
6. **State Handling:**
   - *Success:* Curves plotted with distinct policy colors; clear crossover point highlighted.
   - *Warning:* Prominent callout noting stress is a controlled synthetic simulation.
7. **Responsive Behavior:** Controls placed above chart; chart height dynamically adjusts to viewport.
8. **Accessibility:** Slider values announce changes to screen readers; accessible table alternative provided.

---

### 4.5 View 5: Failure Map
1. **User Question & Purpose:** *"Where are the exact operational boundaries where policy recommendations cease to be trustworthy?"*
2. **Information Hierarchy:**
   - 1. Operational Safety Zones Demarcation Table (`Strong [0–15%]`, `Conditional [15–35%]`, `Reject [>35%]`).
   - 2. Critical Boundary Gauge ($\alpha^*$ threshold where policy advantage reaches 0).
   - 3. Multi-Regime Failure Decision Matrix.
3. **Components & Layout:**
   - Top: Critical Failure Gauge card showing $\alpha^* = 34.2\%$ for Change policy at $B=20$.
   - Center: Three-tier colored zone diagram with explicit operational rules.
   - Bottom: Policy comparison table under stress thresholds ($10\%, 20\%, 30\%, 40\%$).
4. **Available Interactions:**
   - Budget selector updates critical failure boundaries dynamically.
   - Hover on boundary cards to read operational guidance for field teams.
5. **Data Source & Contract:** Consumes `results/decision/decision_audit.json` (`failure_boundary_alpha` and operating zones).
6. **State Handling:**
   - *Success:* Clean visualization of safety boundaries.
7. **Responsive Behavior:** Three-tier cards stack vertically on tablets and mobile screens.
8. **Accessibility:** Operating zones labeled with clear text headers, not color alone.

---

### 4.6 View 6: Stations Explorer
1. **User Question & Purpose:** *"Which exact monitoring stations were selected, where are they located, and why were they chosen?"*
2. **Information Hierarchy:**
   - 1. Geographic Station Distribution (Map / Cartesian Scatter).
   - 2. Station Filter & Search Bar (Filter by District, Water Body, Selection Status).
   - 3. Granular Station Table (Station Code, Name, District, Coordinates, Scores, Selection Status).
   - 4. Selected Station Inspector Drawer.
3. **Components & Layout:**
   - Left (or Top on Mobile): Map / Cartesian plot showing selected (Cyan) vs unselected (Slate) stations.
   - Right (or Bottom on Mobile): Filterable, sortable station table.
   - Drilldown Drawer: Opens on station row click showing historical parameter time-series (Jul/Aug/Sep).
4. **Available Interactions:**
   - Click any point on the map or row in the table to open the **Station Inspector Drawer** with exact parameter values.
   - Filter dropdown by administrative district (e.g., Pune, Thane, Nagpur).
   - Toggle: *"Show Selected Only"* checkbox.
5. **Data Source & Contract:** Consumes `data/processed/river_cohort_172.parquet` joined with `selected_stations` list from `PolicyResult`.
6. **State Handling:**
   - *Map Fallback:* If map tile fails, renders Cartesian scatter plot seamlessly without error.
   - *Empty Filter:* Displays *"No stations match selected filters"* with Reset button.
7. **Responsive Behavior:** 2-column layout on desktop (>1024px); map on top, table below on mobile.
8. **Accessibility:** Table supports standard keyboard navigation; search bar has clear ARIA label.

---

### 4.7 View 7: Data Integrity Dashboard
1. **User Question & Purpose:** *"Can we trust the underlying government data before we trust the policy recommendations?"*
2. **Information Hierarchy:**
   - 1. Ingestion & Provenance Cards (Source: NWMP MPCB via data.gov.in, SHA-256 Hashes).
   - 2. Duplicate Resolution Verification (Detection and deduplication of July duplicate file).
   - 3. Recurrence Audit (Verification of exactly 222 recurring stations across all 3 months).
   - 4. Cohort Partitioning Breakdown (172 River Stations vs 50 non-river stations).
   - 5. Parameter Quality Matrix (12 core parameters, missing value counts, numeric conversion status).
   - 6. Feature Exclusion Audit (Documenting exclusion of unstable `Use Based Class`).
3. **Components & Layout:**
   - Grid of 6 Verification Cards with green audit badges.
   - Parameter Health Table showing missingness rates and scale parameters ($\mu_p^{\text{hist}}, \sigma_p^{\text{hist}}$).
4. **Available Interactions:**
   - Expand SHA-256 card to inspect raw file hashes.
   - Toggle cohort inspect between River (172) and Full Network (222).
5. **Data Source & Contract:** Consumes `data/processed/data_integrity_report.json` generated by `scripts/prepare_data.py`.
6. **State Handling:**
   - *Success:* All integrity invariants flagged with verified checks.
   - *Failure:* Prominent red card if any station code fails recurrence.
7. **Responsive Behavior:** Cards wrap in 3 columns on desktop, 2 on laptop, 1 on tablet/mobile.
8. **Accessibility:** Semantic audit lists with text descriptions for all verification states.

---

### 4.8 View 8: Evidence & Research Console
1. **User Question & Purpose:** *"What is the complete scientific evidence behind this system, what are its limits, and how does it defend against academic criticism?"*
2. **Information Hierarchy:**
   - 1. Empirical Evidence Deck (Nominal Replay, 4-Fold Parameter Holdout, District Randomization).
   - 2. Statistical Caveats & Limitations Panel (Network dependence, 3-month retrospective prototype).
   - 3. Judge Attack & Defense Collapsible FAQ.
   - 4. System Claims Boundary Matrix (What is claimed vs what is NOT claimed).
3. **Components & Layout:**
   - Top: 4 modular evidence cards summarizing empirical results.
   - Middle: 4-Fold Cross-Parameter Holdout results table (Folds 1–4 across budgets).
   - Bottom: Collapsible Judge Defense Matrix (6 attack questions with verified scientific responses).
4. **Available Interactions:**
   - Expand/collapse individual judge attack questions.
   - Switch holdout budget tabs ($B=10, 20, 40$) to inspect transferability across held-out parameter groups.
5. **Data Source & Contract:** Consumes `results/holdout/holdout_results.json` and `results/randomization/randomization_results.json`.
6. **State Handling:**
   - *Statistical Rigor:* Strictly presents randomization results as empirical diagnostics ($\hat{q}_{\text{diag}}$ over 3,000 draws), not asymptotic p-values.
7. **Responsive Behavior:** Clean vertical accordion format scales across all devices.
8. **Accessibility:** Standard HTML `<details>` and `<summary>` styling ensuring full screen-reader support.

---

## 5. Responsive Behavior & Breakpoint Specifications

| Viewport | Width Range | Layout Rules & Adaptations |
|---|---|---|
| **Desktop** | `> 1440px` | Max container width `1400px`. Multi-column layouts (3-column metric cards, 2-column chart grids). Map and station table side-by-side. |
| **Laptop** | `1024px – 1440px` | Primary optimization target. 2-column layouts. Sidebar navigation visible. Tight container padding (`16px`). |
| **Tablet** | `768px – 1024px` | Sidebar collapses to top hamburger / dropdown menu. Metric cards stack into 2 columns. Charts expand to full container width. Tables enable horizontal scrolling. |
| **Mobile** | `< 768px` | Single-column linear layout. Top view selector converts to dropdown. Metric cards stack vertically. Charts set to minimum height (`300px`) with touch tooltips. Station table scrolls horizontally with sticky headers. Map shows simplified Cartesian plot. |

---

## 6. Accessibility & Usability Standards (WCAG 2.1 AA)

1. **Color Contrast:** All body text maintains $\ge 4.5:1$ contrast against background; headers and large metric numbers maintain $\ge 3:1$.
2. **Keyboard Navigation:** Every interactive element (budget switches, tabs, sliders, search inputs) is reachable via `Tab` and activatable via `Enter` / `Space`.
3. **Focus Indicators:** Explicit 2px solid `#58A6FF` outline on focused interactive elements with 2px offset.
4. **Screen Reader Alternatives:** All data visualizations include an expandable *"View as Accessible Table"* toggle presenting raw numbers in semantic HTML `<table>` elements.
5. **Zoom Tolerance:** Layout gracefully tolerates up to $200\%$ browser zoom without horizontal text clipping or overlapping elements.
6. **Non-Color Statuses:** All operational statuses (TRUST, CONDITIONAL, ABSTAIN) always include explicit text labels and standard unicode status symbols.

---

## 7. Motion & Micro-Interactions

- **Interaction Latency:** Micro-interactions (hover, focus, tab switch) complete in $\le 150\,\text{ms}$ with `ease-out` timing.
- **Card Hover:** Subtle border color change (`#30363D` $\rightarrow$ `#58A6FF`) without jarring physical displacement.
- **No Blocking Animations:** Zero slow progress spinners or artificial delays. Data is rendered immediately from cached artifacts in Demo Mode.
- **Loading State:** Clean skeleton loader with subtle pulse animation during live pipeline computation.
