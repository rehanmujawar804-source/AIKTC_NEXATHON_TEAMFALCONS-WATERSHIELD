"""
WATERSHIELD Station Alignment & Cohort Stratification Module
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/02_REQUIREMENTS.md FR-DATA-03, FR-DATA-04

Verifies the 222 recurring stations across July, August, and September 2025.
Extracts and isolates the primary scientific evaluation cohort of 172 river stations.
Generates comprehensive alignment, cohort, metadata consistency, and data quality reports.
"""

from pathlib import Path
from typing import Dict, Tuple, List, Any, Optional
import json
from collections import Counter
import pandas as pd
import numpy as np

from src.config import DEFAULT_CONFIG
from src.utils.logger import get_logger
from src.utils.errors import DataIntegrityError

logger = get_logger("data.alignment")


class StationAligner:
    """Aligns monthly datasets across recurring station codes and partitions cohorts."""

    def __init__(self, reports_dir: Optional[Path] = None):
        self.reports_dir = Path(reports_dir or DEFAULT_CONFIG.paths.reports_dir)

    def extract_recurring_stations(
        self, monthly_dfs: Dict[str, pd.DataFrame], save_report: bool = True
    ) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
        """
        Intersects station codes across all three months.
        Verifies that exactly 222 unique station codes recur across July, August, September.
        Returns (recurring_registry_df, recurring_station_codes, alignment_report).
        """
        station_sets: Dict[str, set] = {}
        month_counts: Dict[str, int] = {}
        duplicates_by_month: Dict[str, int] = {}

        for month, df in monthly_dfs.items():
            stn_series = df["STN Code"].astype(str).str.strip()
            station_sets[month] = set(stn_series)
            month_counts[month] = len(stn_series)
            duplicates_by_month[month] = int(stn_series.duplicated().sum())

        months = list(monthly_dfs.keys())
        if len(months) < 3:
            raise DataIntegrityError(f"Expected 3 monthly datasets for alignment; found {len(months)}")

        # Intersect recurring station codes across all months
        common_stations = set.intersection(*[station_sets[m] for m in months])
        recurring_codes = sorted(list(common_stations))
        total_recurring = len(recurring_codes)

        logger.info(f"Empirically identified {total_recurring} recurring stations across {months}")

        # Verify against frozen scientific invariant (222)
        expected_recurring = DEFAULT_CONFIG.dataset.total_recurring_stations
        if total_recurring != expected_recurring:
            raise DataIntegrityError(
                f"Recurring station count discrepancy! Expected {expected_recurring}, computed {total_recurring}",
                details=f"Months analyzed: {months}. Individual monthly counts: {month_counts}"
            )

        # Build clean registry from the first historical month (July), retaining stable metadata
        base_df = monthly_dfs[months[0]]
        recurring_base = base_df[base_df["STN Code"].astype(str).str.strip().isin(common_stations)].copy()
        recurring_base = recurring_base.drop_duplicates(subset=["STN Code"]).sort_values("STN Code")

        alignment_report = {
            "evaluation_months": months,
            "monthly_station_counts": month_counts,
            "monthly_duplicate_station_records": duplicates_by_month,
            "total_recurring_stations": total_recurring,
            "expected_recurring_stations": expected_recurring,
            "recurrence_verified": True,
            "recurring_station_codes": recurring_codes
        }

        if save_report:
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.reports_dir / "alignment_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(alignment_report, f, indent=2)
            logger.info(f"Alignment report saved to {report_path}")

        return recurring_base, recurring_codes, alignment_report

    def filter_river_cohort(
        self, recurring_df: pd.DataFrame, save_report: bool = True
    ) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
        """
        Filters recurring stations to the 172-station river cohort (Type Water Body.str.upper() == 'RIVER').
        Asserts that exactly 172 river stations are present and 50 non-river stations remain.
        """
        df = recurring_df.copy()
        type_col = "Type Water Body"
        if type_col not in df.columns:
            raise DataIntegrityError(f"Missing '{type_col}' column in recurring dataset.")

        # Standardize water-body type string
        df["type_normalized"] = df[type_col].astype(str).str.strip().str.upper()

        river_mask = df["type_normalized"] == DEFAULT_CONFIG.dataset.water_body_river_filter
        river_df = df[river_mask].copy()
        non_river_df = df[~river_mask].copy()

        river_station_codes = sorted(river_df["STN Code"].astype(str).str.strip().tolist())
        non_river_station_codes = sorted(non_river_df["STN Code"].astype(str).str.strip().tolist())

        total_river = len(river_station_codes)
        total_non_river = len(non_river_station_codes)
        total_recurring = len(df)

        logger.info(f"Cohort stratification: {total_river} river stations, {total_non_river} non-river stations.")

        # Verify against frozen scientific invariant (172 river stations, 50 non-river)
        expected_river = DEFAULT_CONFIG.dataset.primary_river_cohort_stations
        expected_non_river = DEFAULT_CONFIG.dataset.secondary_non_river_stations

        if total_river != expected_river:
            raise DataIntegrityError(
                f"River cohort count discrepancy! Expected {expected_river}, computed {total_river}",
                details=f"Total recurring stations: {total_recurring}. Non-river count: {total_non_river}"
            )

        if total_non_river != expected_non_river:
            raise DataIntegrityError(
                f"Secondary non-river cohort count discrepancy! Expected {expected_non_river}, computed {total_non_river}"
            )

        # Count distribution across water-body types and districts
        type_counts = dict(Counter(df[type_col].astype(str).str.strip()))
        district_counts_river = dict(Counter(river_df["District"].astype(str).str.strip()))
        district_counts_all = dict(Counter(df["District"].astype(str).str.strip()))

        cohort_report = {
            "total_recurring_stations": total_recurring,
            "primary_river_cohort_stations": total_river,
            "secondary_non_river_stations": total_non_river,
            "river_cohort_verified": True,
            "water_body_type_distribution": type_counts,
            "district_distribution_river": district_counts_river,
            "district_distribution_all": district_counts_all,
            "river_station_codes": river_station_codes,
            "non_river_station_codes": non_river_station_codes
        }

        if save_report:
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.reports_dir / "cohort_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(cohort_report, f, indent=2)
            logger.info(f"Cohort report saved to {report_path}")

        # Drop temporary column
        river_df = river_df.drop(columns=["type_normalized"])
        return river_df, river_station_codes, cohort_report

    def check_metadata_consistency(
        self, monthly_dfs: Dict[str, pd.DataFrame], recurring_codes: List[str], save_report: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluates station metadata consistency across July, August, and September for recurring stations.
        Audits station name, water body type, water body name, district, coordinates, and Use Based Class.
        """
        months = ["July 2025", "August 2025", "September 2025"]
        data_by_stn: Dict[str, Dict[str, Dict[str, str]]] = {stn: {} for stn in recurring_codes}

        for m in months:
            df = monthly_dfs[m]
            for _, r in df.iterrows():
                stn = str(r["STN Code"]).strip()
                if stn in data_by_stn:
                    data_by_stn[stn][m] = {col.strip(): str(val).strip() for col, val in r.items()}

        fields_to_check = [
            ("Stn Name", "station_name"),
            ("Type Water Body", "water_body_type"),
            ("Name Of Water Body", "water_body_name"),
            ("District", "district"),
            ("latitude", "latitude"),
            ("longitude", "longitude"),
            ("Use Based Class", "use_based_class")
        ]

        field_summaries = {}
        for col_raw, field_label in fields_to_check:
            jul_aug_changes = []
            aug_sep_changes = []

            for stn in recurring_codes:
                stn_data = data_by_stn[stn]
                v_jul = stn_data.get("July 2025", {}).get(col_raw, "")
                v_aug = stn_data.get("August 2025", {}).get(col_raw, "")
                v_sep = stn_data.get("September 2025", {}).get(col_raw, "")

                if v_jul != v_aug:
                    jul_aug_changes.append({
                        "stn_code": stn,
                        "jul_value": v_jul,
                        "aug_value": v_aug
                    })
                if v_aug != v_sep:
                    aug_sep_changes.append({
                        "stn_code": stn,
                        "aug_value": v_aug,
                        "sep_value": v_sep
                    })

            field_summaries[field_label] = {
                "raw_column": col_raw,
                "july_to_august_change_count": len(jul_aug_changes),
                "august_to_september_change_count": len(aug_sep_changes),
                "july_to_august_changes": jul_aug_changes,
                "august_to_september_changes": aug_sep_changes,
            }

        report = {
            "evaluation_months": months,
            "recurring_stations_evaluated": len(recurring_codes),
            "metadata_fields": field_summaries,
            "use_based_class_excluded_from_features": True,
            "use_based_class_exclusion_rationale": (
                "Empirical audit verifies 'Use Based Class' changes across months "
                f"({field_summaries['use_based_class']['july_to_august_change_count']} Jul->Aug, "
                f"{field_summaries['use_based_class']['august_to_september_change_count']} Aug->Sep). "
                "It is unstable and strictly excluded from policy features."
            )
        }

        if save_report:
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.reports_dir / "metadata_consistency_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Metadata consistency report saved to {report_path}")

        return report

    def generate_missingness_report(
        self, monthly_dfs: Dict[str, pd.DataFrame], recurring_codes: List[str], save_report: bool = True
    ) -> Dict[str, Any]:
        """
        Profiles missing-value distributions per month, per core parameter, and per district.
        NO imputation is applied; profiling only.
        """
        core_params = list(DEFAULT_CONFIG.dataset.core_parameters)
        months_missingness = {}

        for month, df in monthly_dfs.items():
            stn_clean = df["STN Code"].astype(str).str.strip()
            df_rec = df[stn_clean.isin(recurring_codes)].copy()

            # Parameter level missingness
            param_missing = {}
            for param in core_params:
                missing_cnt = int(df_rec[param].isna().sum())
                param_missing[param] = {
                    "missing_count": missing_cnt,
                    "valid_count": len(df_rec) - missing_cnt,
                    "missing_percentage": round(missing_cnt / len(df_rec) * 100, 2)
                }

            # District level missingness across all core parameters
            district_missing = {}
            for district, grp in df_rec.groupby("District"):
                d_name = str(district).strip()
                total_cells = len(grp) * len(core_params)
                missing_cells = int(grp[core_params].isna().sum().sum())
                district_missing[d_name] = {
                    "station_count": len(grp),
                    "total_parameter_observations": total_cells,
                    "missing_observations": missing_cells,
                    "missing_percentage": round(missing_cells / total_cells * 100, 2) if total_cells > 0 else 0.0
                }

            months_missingness[month] = {
                "total_recurring_rows": len(df_rec),
                "parameter_missingness": param_missing,
                "district_missingness": district_missing
            }

        report = {
            "evaluation_months": list(monthly_dfs.keys()),
            "recurring_station_count": len(recurring_codes),
            "core_parameters_profiled": core_params,
            "monthly_profiles": months_missingness
        }

        if save_report:
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.reports_dir / "missingness_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Missingness report saved to {report_path}")

        return report

    def generate_numeric_quality_report(
        self, monthly_dfs: Dict[str, pd.DataFrame], river_codes: List[str], save_report: bool = True
    ) -> Dict[str, Any]:
        """
        Profiles statistical distributions (min, max, mean, median, std) for the 12 core parameters
        on the primary 172 river cohort. Flags suspicious environmental observations without deleting them.
        """
        core_params = list(DEFAULT_CONFIG.dataset.core_parameters)
        monthly_numeric_profiles = {}

        for month, df in monthly_dfs.items():
            stn_clean = df["STN Code"].astype(str).str.strip()
            df_river = df[stn_clean.isin(river_codes)].copy()

            param_profiles = {}
            for param in core_params:
                series = pd.to_numeric(df_river[param], errors="coerce")
                valid_cnt = int(series.count())
                missing_cnt = int(series.isna().sum())

                # Check for extreme or negative values
                negative_cnt = int((series < 0).sum())
                min_v = float(series.min()) if valid_cnt > 0 else None
                max_v = float(series.max()) if valid_cnt > 0 else None
                mean_v = float(round(series.mean(), 4)) if valid_cnt > 0 else None
                median_v = float(round(series.median(), 4)) if valid_cnt > 0 else None
                std_v = float(round(series.std(), 4)) if valid_cnt > 1 else None

                param_profiles[param] = {
                    "dtype": str(series.dtype),
                    "valid_count": valid_cnt,
                    "missing_count": missing_cnt,
                    "missing_percentage": round(missing_cnt / len(df_river) * 100, 2),
                    "negative_count": negative_cnt,
                    "min": min_v,
                    "max": max_v,
                    "median": median_v,
                    "mean": mean_v,
                    "std": std_v,
                }

            monthly_numeric_profiles[month] = {
                "river_station_count": len(df_river),
                "parameters": param_profiles
            }

        report = {
            "evaluation_cohort": "172 River Stations",
            "core_parameters_profiled": core_params,
            "monthly_profiles": monthly_numeric_profiles
        }

        if save_report:
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.reports_dir / "numeric_quality_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Numeric quality report saved to {report_path}")

        return report
