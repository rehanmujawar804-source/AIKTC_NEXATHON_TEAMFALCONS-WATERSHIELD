"""
WATERSHIELD CLI: Reproducible Raw Data Ingestion & Alignment Pipeline
Phase 2 — Environment & Data Foundation
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/06_IMPLEMENTATION.md §2.2

End-to-end data preparation workflow:
1. Locates and scans raw NWMP CSV files in data/raw/
2. Computes SHA-256 hashes for all raw files and validates July duplicate
3. Validates raw and cleaned schemas for required identifiers and 12 core parameters
4. Cleans raw strings, coerces numeric parameters, parses coordinates, normalizes missingness
5. Aligns 222 recurring stations across July, August, September
6. Stratifies and verifies the primary 172 river cohort
7. Audits metadata consistency and verifies 'Use Based Class' instability
8. Generates machine-readable data quality and diagnostic reports in data/reports/
9. Writes reproducible processed datasets in data/processed/
10. Produces end-to-end cryptographic provenance & reproducibility manifest
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# Add workspace root to sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from src.config import DEFAULT_CONFIG
from src.utils.logger import get_logger
from src.utils.errors import DataIntegrityError, LeakageViolationError
from src.utils.hashing import compute_file_sha256, compute_dict_hash
from src.data.loader import NWMPDataLoader
from src.data.validation import DataValidator
from src.data.cleaning import DataCleaner
from src.data.alignment import StationAligner
from src.data.contracts import (
    assert_no_future_data_access,
    assert_no_excluded_features,
    ProcessedDatasetFoundation,
    DEFAULT_TEMPORAL_CONTRACT
)

logger = get_logger("scripts.prepare_data")


def run_pipeline(
    raw_dir: Path,
    processed_dir: Path,
    reports_dir: Path,
    strict: bool = True
) -> Dict[str, Any]:
    """Executes the complete Phase 2 data pipeline and generates all reports & artifacts."""
    logger.info("=" * 70)
    logger.info("WATERSHIELD PHASE 2 — RAW DATA FOUNDATION & PIPELINE")
    logger.info("=" * 70)

    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    reports_dir = Path(reports_dir)

    processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Loader & Duplicate Detection
    logger.info("Step 1: Discovering raw CSV files and computing SHA-256 hashes...")
    loader = NWMPDataLoader(raw_data_dir=raw_dir, reports_dir=reports_dir)
    manifest = loader.generate_manifest(save_report=True)

    # Confirm July duplicate files
    july_entries = [e for e in manifest["files"] if e["month"] == "July 2025"]
    if len(july_entries) >= 2:
        hashes = {e["sha256"] for e in july_entries}
        if len(hashes) == 1:
            logger.info("Bit-for-bit identical July duplicate source files empirically confirmed.")
        else:
            raise DataIntegrityError("Multiple distinct July source files detected with conflicting hashes!")

    raw_monthly_dfs = loader.load_raw_monthly_data()

    # 2. Schema Validation
    logger.info("Step 2: Validating schema across raw monthly datasets...")
    validator = DataValidator(reports_dir=reports_dir)
    schema_report = validator.validate_monthly_schemas(raw_monthly_dfs, save_report=True)

    # 3. Data Cleaning & Sanitization
    logger.info("Step 3: Cleaning strings, parsing coordinates, and coercing numeric parameters...")
    cleaner = DataCleaner()
    cleaned_monthly_dfs: Dict[str, pd.DataFrame] = {}
    cleaning_audit_reports: Dict[str, Any] = {}

    for month_name, df_raw in raw_monthly_dfs.items():
        df_clean, stats = cleaner.clean_monthly_dataframe(df_raw, month_name)
        cleaned_monthly_dfs[month_name] = df_clean
        cleaning_audit_reports[month_name] = stats

    # 4. Station Alignment & Recurrence Verification
    logger.info("Step 4: Intersecting station codes across July, August, September...")
    aligner = StationAligner(reports_dir=reports_dir)
    recurring_registry, recurring_codes, alignment_report = aligner.extract_recurring_stations(
        cleaned_monthly_dfs, save_report=True
    )

    # 5. River Cohort Stratification
    logger.info("Step 5: Stratifying primary 172 river cohort vs 50 non-river stations...")
    river_df, river_codes, cohort_report = aligner.filter_river_cohort(
        recurring_registry, save_report=True
    )

    # 6. Metadata Consistency Audit & Use Based Class Inspection
    logger.info("Step 6: Auditing cross-month metadata consistency and Use Based Class stability...")
    metadata_consistency_report = aligner.check_metadata_consistency(
        cleaned_monthly_dfs, recurring_codes, save_report=True
    )

    # 7. Missingness and Numeric Quality Profiling
    logger.info("Step 7: Profiling missingness and numeric statistical distributions...")
    missingness_report = aligner.generate_missingness_report(
        cleaned_monthly_dfs, recurring_codes, save_report=True
    )
    numeric_quality_report = aligner.generate_numeric_quality_report(
        cleaned_monthly_dfs, river_codes, save_report=True
    )

    # 8. Build Processed Datasets
    logger.info("Step 8: Constructing processed datasets and station registry...")
    core_params = list(DEFAULT_CONFIG.dataset.core_parameters)
    feature_columns = [
        "STN Code", "Month", "Stn Name", "District",
        "Type Water Body", "Name Of Water Body",
        "latitude_dd", "longitude_dd"
    ] + core_params

    # Filter to primary river cohort and retain clean observation rows
    historical_dfs = []
    for month_name in DEFAULT_TEMPORAL_CONTRACT.historical_months:
        df_m = cleaned_monthly_dfs[month_name]
        df_river_m = df_m[df_m["STN Code"].astype(str).str.strip().isin(river_codes)].copy()
        df_river_m["Month"] = month_name
        # Keep only allowed columns (strictly dropping 'Use Based Class' from features)
        cols_to_keep = [c for c in feature_columns if c in df_river_m.columns]
        historical_dfs.append(df_river_m[cols_to_keep])

    historical_state_df = pd.concat(historical_dfs, ignore_index=True)

    # Hidden future evaluation dataset (September 2025)
    df_sep = cleaned_monthly_dfs[DEFAULT_TEMPORAL_CONTRACT.hidden_future_month]
    df_river_sep = df_sep[df_sep["STN Code"].astype(str).str.strip().isin(river_codes)].copy()
    df_river_sep["Month"] = DEFAULT_TEMPORAL_CONTRACT.hidden_future_month
    cols_sep = [c for c in feature_columns if c in df_river_sep.columns]
    hidden_future_df = df_river_sep[cols_sep]

    # Full station registry (222 stations with metadata & cohort flag)
    station_registry_df = recurring_registry[[
        "STN Code", "Stn Name", "Type Water Body", "Name Of Water Body",
        "District", "latitude_dd", "longitude_dd"
    ]].copy()
    station_registry_df["is_river_cohort"] = station_registry_df["STN Code"].astype(str).str.strip().isin(river_codes)
    station_registry_df["total_months_available"] = 3

    # Validate data contracts and anti-leakage guards
    foundation = ProcessedDatasetFoundation(
        recurring_222_df=recurring_registry,
        river_172_df=river_df,
        historical_state_df=historical_state_df,
        hidden_future_df=hidden_future_df,
        recurring_codes=recurring_codes,
        river_codes=river_codes,
    )
    foundation.validate_isolation()
    assert_no_excluded_features(historical_state_df.columns, "prepare_data historical export")
    assert_no_future_data_access(historical_state_df, "prepare_data historical export")

    # 9. Save Processed Artifacts (both Parquet and CSV for portability)
    logger.info("Step 9: Writing processed Parquet and CSV artifacts to data/processed/...")
    
    # 222 recurring stations
    rec_parquet = processed_dir / DEFAULT_CONFIG.paths.recurring_222_parquet
    rec_csv = processed_dir / "recurring_stations_222.csv"
    recurring_registry.to_parquet(rec_parquet, index=False)
    recurring_registry.to_csv(rec_csv, index=False)

    # 172 river cohort
    river_parquet = processed_dir / DEFAULT_CONFIG.paths.river_172_parquet
    river_csv = processed_dir / "river_cohort_172.csv"
    river_df.to_parquet(river_parquet, index=False)
    river_df.to_csv(river_csv, index=False)

    # Historical state (July + August, 172 river cohort)
    hist_parquet = processed_dir / DEFAULT_CONFIG.paths.historical_state_parquet
    hist_csv = processed_dir / "historical_state_jul_aug.csv"
    historical_state_df.to_parquet(hist_parquet, index=False)
    historical_state_df.to_csv(hist_csv, index=False)

    # Hidden future state (September, 172 river cohort)
    future_parquet = processed_dir / DEFAULT_CONFIG.paths.hidden_future_parquet
    future_csv = processed_dir / "hidden_future_sep.csv"
    hidden_future_df.to_parquet(future_parquet, index=False)
    hidden_future_df.to_csv(future_csv, index=False)

    # Station registry
    registry_csv = processed_dir / "station_registry.csv"
    station_registry_df.to_csv(registry_csv, index=False)

    # 10. Cryptographic Provenance Manifest
    logger.info("Step 10: Generating reproducibility manifest...")
    output_files = [
        rec_parquet, rec_csv, river_parquet, river_csv,
        hist_parquet, hist_csv, future_parquet, future_csv, registry_csv
    ]
    output_hashes = {f.name: compute_file_sha256(f) for f in output_files if f.exists()}

    reproducibility_manifest = {
        "pipeline_phase": "Phase 2 (Environment & Data Foundation)",
        "source_agency": DEFAULT_CONFIG.dataset.source_agency,
        "input_files": {entry["filename"]: entry["sha256"] for entry in manifest["files"]},
        "output_artifacts": output_hashes,
        "invariants_verified": {
            "total_recurring_stations": len(recurring_codes),
            "primary_river_cohort": len(river_codes),
            "secondary_non_river_cohort": len(recurring_codes) - len(river_codes),
            "core_parameters_count": len(core_params),
            "historical_state_rows": len(historical_state_df),
            "hidden_future_state_rows": len(hidden_future_df),
            "use_based_class_excluded": True,
            "future_leakage_prevented": True
        }
    }

    manifest_path = reports_dir / "reproducibility_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(reproducibility_manifest, f, indent=2)

    logger.info(f"Reproducibility manifest saved to {manifest_path}")
    logger.info("=" * 70)
    logger.info("PHASE 2 DATA PREPARATION PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)

    return reproducibility_manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="WATERSHIELD Phase 2: Reproducible Data Ingestion & Alignment"
    )
    parser.add_argument(
        "--raw-dir", default=str(DEFAULT_CONFIG.paths.raw_data_dir), help="Path to raw NWMP CSV directory"
    )
    parser.add_argument(
        "--output-dir", default=str(DEFAULT_CONFIG.paths.processed_data_dir), help="Path to processed output directory"
    )
    parser.add_argument(
        "--reports-dir", default=str(DEFAULT_CONFIG.paths.reports_dir), help="Path to reports directory"
    )
    args = parser.parse_args()

    try:
        run_pipeline(
            raw_dir=Path(args.raw_dir),
            processed_dir=Path(args.output_dir),
            reports_dir=Path(args.reports_dir),
        )
        return 0
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        print(f"\n[FATAL ERROR] Data preparation pipeline failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
