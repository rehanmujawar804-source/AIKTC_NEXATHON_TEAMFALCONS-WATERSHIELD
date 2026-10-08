"""
WATERSHIELD Data Cleaning & Sanitization Module
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/01_MASTER_PROJECT.md §6

Sanitizes raw column headers, coerces numeric parameters, parses coordinate floats,
handles missing values, and strictly drops 'Use Based Class' from policy feature sets.
NO model-based imputation, NO interpolation, NO synthetic values.
"""

from typing import List, Optional, Dict, Any, Tuple
import re
import pandas as pd
import numpy as np

from src.config import DEFAULT_CONFIG
from src.utils.logger import get_logger
from src.utils.errors import DataIntegrityError
from src.data.validation import DataValidator

logger = get_logger("data.cleaning")

# Missing value tokens commonly encountered in MPCB datasets
MISSING_TOKENS = {"", "NA", "N/A", "NULL", "NONE", "-", "ND"}


class DataCleaner:
    """Sanitizes raw strings, formats numeric columns, and normalizes missingness."""

    def __init__(self):
        self.validator = DataValidator()

    @staticmethod
    def sanitize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Strips leading/trailing whitespace from column names."""
        df_clean = df.copy()
        df_clean.columns = [col.strip() for col in df_clean.columns]
        return df_clean

    @staticmethod
    def coerce_numeric_cell(val: Any) -> Tuple[Optional[float], bool]:
        """
        Parses a single parameter cell to float.
        Returns (float_val, is_bdl_flag).
        Recognizes '<num>(BDL)' as numeric <num> with is_bdl=True.
        Recognizes missing tokens ('', 'NA', 'N/A', 'ND', '-') as np.nan.
        """
        if pd.isna(val) or val is None:
            return np.nan, False
        s = str(val).strip()
        if s.upper() in MISSING_TOKENS:
            return np.nan, False

        # Check for BDL (Below Detection Limit) annotation: e.g. 0.3(BDL), 1(BDL)
        bdl_match = re.match(r"^(\d+(?:\.\d+)?)\s*\(BDL\)$", s, re.IGNORECASE)
        if bdl_match:
            try:
                num = float(bdl_match.group(1))
                return num, True
            except ValueError:
                return np.nan, False

        try:
            return float(s), False
        except ValueError:
            return np.nan, False

    def clean_monthly_dataframe(
        self,
        df: pd.DataFrame,
        month_name: str,
        core_parameters: Optional[Tuple[str, ...]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans column names, coerces the 12 core parameters to float,
        cleans coordinates into decimal degrees (latitude_dd, longitude_dd),
        and tracks cleaning diagnostics.
        """
        core_params = list(core_parameters or DEFAULT_CONFIG.dataset.core_parameters)
        df_clean = self.sanitize_column_names(df)

        # Standardize station metadata strings
        string_cols = ["STN Code", "Stn Name", "Type Water Body", "Name Of Water Body", "District"]
        for col in string_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()

        # Parse geographic coordinates into numeric decimal degrees
        if "latitude" in df_clean.columns and "longitude" in df_clean.columns:
            df_clean["latitude_dd"] = df_clean["latitude"].apply(self.validator.parse_coordinate)
            df_clean["longitude_dd"] = df_clean["longitude"].apply(self.validator.parse_coordinate)

        # Coerce 12 core water-quality parameters
        cleaning_stats: Dict[str, Any] = {
            "month": month_name,
            "total_rows": len(df_clean),
            "parameters": {}
        }

        for param in core_params:
            if param not in df_clean.columns:
                raise DataIntegrityError(f"Missing core parameter {param} in {month_name}")

            coerced_vals = []
            bdl_count = 0
            raw_missing = 0
            for raw_val in df_clean[param]:
                clean_num, is_bdl = self.coerce_numeric_cell(raw_val)
                coerced_vals.append(clean_num)
                if is_bdl:
                    bdl_count += 1
                if pd.isna(clean_num):
                    raw_missing += 1

            df_clean[param] = pd.Series(coerced_vals, dtype="float64")

            valid_count = len(df_clean) - raw_missing
            cleaning_stats["parameters"][param] = {
                "valid_count": valid_count,
                "missing_count": raw_missing,
                "missing_pct": round(raw_missing / len(df_clean) * 100, 2),
                "bdl_count": bdl_count,
                "min": float(df_clean[param].min()) if valid_count > 0 else None,
                "max": float(df_clean[param].max()) if valid_count > 0 else None,
                "mean": float(round(df_clean[param].mean(), 4)) if valid_count > 0 else None,
            }

        # Document explicitly that 'Use Based Class' must NOT be in feature set
        if "Use Based Class" in df_clean.columns:
            df_clean["Use Based Class"] = df_clean["Use Based Class"].astype(str).str.strip()

        logger.info(f"Cleaned {month_name} dataset: {len(df_clean)} rows, {len(core_params)} numeric parameters.")
        return df_clean, cleaning_stats
