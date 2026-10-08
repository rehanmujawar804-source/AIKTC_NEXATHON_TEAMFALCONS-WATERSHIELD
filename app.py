"""
WATERSHIELD: Water Monitoring Policy Reliability & Decision-Audit Engine
Main Application Entrypoint

Core Question: "Which monitoring policy should we trust when we cannot monitor everything?"
Core Principle: "Don't trust the optimizer. Test the policy."

Traceability: DOCS/05_PRODUCT_UI_UX.md §2, DOCS/04_ARCHITECTURE.md §2
NOTE: This is the Phase 1 application skeleton. UI screens and visualizations are scheduled
for implementation in Phase 12-14. This module contains no scientific calculations or fake data.
"""

import streamlit as st
from src.config import DEFAULT_CONFIG


def main() -> None:
    st.set_page_config(
        page_title="WATERSHIELD — Policy Reliability Audit Engine",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Global Top Header & Branding
    st.title("🛡️ WATERSHIELD")
    st.caption("Water Monitoring Policy Reliability & Decision-Audit Engine")
    st.markdown("> **'Don't trust the optimizer. Test the policy.'**")

    # Global Sidebar Context Controls
    with st.sidebar:
        st.header("Operational Context")
        
        # Cohort Selection
        cohort = st.selectbox(
            "Evaluation Cohort",
            options=["172 River Stations (Primary)", "222 Full Network (Exploratory)"],
            index=0,
            help="Primary scientific evaluation is restricted to 172 recurring river stations to avoid water-body confounding.",
        )

        # Budget Selection (B in {10, 20, 40})
        budget = st.select_slider(
            "Sampling Budget (B)",
            options=[10, 20, 40],
            value=20,
            help="Operational constraint: number of stations monitored out of 172.",
        )

        # Execution Mode Switcher
        mode = st.radio(
            "Execution Mode",
            options=["Demo Mode (Precomputed)", "Experiment Mode (Live)"],
            index=0,
            help="Demo Mode loads verified scientific artifacts (<500ms). Experiment Mode executes the pipeline live.",
        )

        st.divider()
        st.markdown("**Navigation**")
        st.markdown(
            """
            - 🛡️ `pages/decision_console.py`
            - ⚔️ `pages/policy_arena.py`
            - ⏱️ `pages/replay.py`
            - 🧪 `pages/stress_lab.py`
            - 🗺️ `pages/failure_map.py`
            - 📍 `pages/stations.py`
            - 🔍 `pages/data_integrity.py`
            - 📚 `pages/evidence.py`
            """
        )

    # Landing Notice
    st.info(
        "**[Phase 1 Foundation]** The WATERSHIELD application skeleton is initialized. "
        "The complete interactive Decision Console and evidentiary views are scheduled for "
        "Phases 12–15 per the project roadmap.\n\n"
        "Use the sidebar or multipage navigation to preview view structures."
    )

    # Operational Specifications Card
    with st.expander("System Specifications (Frozen)", expanded=True):
        st.markdown(
            f"""
            - **Domain Dataset:** Maharashtra NWMP (July, August, September 2025)
            - **Primary Scientific Cohort:** {DEFAULT_CONFIG.dataset.primary_river_cohort_stations} River Stations
            - **Candidate Policies:** {", ".join(DEFAULT_CONFIG.policy.policy_names)}
            - **Sampling Budgets:** $B \\in \\{{{", ".join(map(str, DEFAULT_CONFIG.policy.budgets))}\\}}$
            - **Temporal Replay:** July + August (Historical) $\\rightarrow$ September (Hidden Future)
            - **Validation Layers:** 4-Fold Parameter Holdout, 3,000 District-Matched Randomization, Controlled Stress Lab
            - **Decision Verdicts:** `TRUST` | `CONDITIONAL` | `ABSTAIN`
            """
        )


if __name__ == "__main__":
    main()
