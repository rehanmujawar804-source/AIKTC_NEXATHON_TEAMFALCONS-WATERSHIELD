"""
WATERSHIELD Data Validation Module
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/02_REQUIREMENTS.md FR-DATA-05

Validates raw and cleaned schemas, verifies presence of all 12 core parameters,
validates geographic coordinates, and generates comprehensive schema reports.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import re
import pandas as pd
import numpy as np

from src.config import DEFAULT_CONFIG
from src.utils.logger import get_logger
from src.utils.errors import DataIntegrityError

logger = get_logger("data.validation")

REQUIRED_IDENTIFIERS = [
    "STN Code",
    "Stn Name",
    "Type Water Body",
    "Name Of Water Body",
    "District",
    "latitude",
    "longitude",
]


class DataValidator:
    """Validates dataframe schema and station attributes against specification."""

    def __init__(self, reports_dir: Optional[Path] = None):
        self.reports_dir = Path(reports_dir or DEFAULT_CONFIG.paths.reports_dir)

    def validate_schema(
        self,
        df: pd.DataFrame,
        month_name: str,
        required_identifiers: Optional[List[str]] = None,
        core_parameters: Optional[Tuple[str, ...]] = None,
    ) -> Dict[str, Any]:
        """
        Validates that required station identifiers and 12 core parameters are present.
        Documents additional columns without failing.
        """
        req_identifiers = required_identifiers or REQUIRED_IDENTIFIERS
        core_params = list(core_parameters or DEFAULT_CONFIG.dataset.core_parameters)

        # Normalize column names in df (strip whitespace) for matching
        df_cols_stripped = {col.strip(): col for col in df.columns}

        missing_identifiers = [col for col in req_identifiers if col not in df_cols_stripped]
        missing_core_params = [param for param in core_params if param not in df_cols_stripped]

        if missing_identifiers:
            raise DataIntegrityError(
                f"Schema validation failed for {month_name}: missing identifiers {missing_identifiers}",
                details=f"Required identifiers: {req_identifiers}"
            )

        if missing_core_params:
            raise DataIntegrityError(
                f"Schema validation failed for {month_name}: missing core parameters {missing_core_params}",
                details=f"All 12 core parameters must be present. Required: {core_params}"
            )

        # Identify additional / optional columns
        known_cols = set(req_identifiers) | set(core_params)
        additional_cols = [col for col in df_cols_stripped if col not in known_cols]

        logger.info(
            f"Schema validation passed for {month_name}: {len(req_identifiers)} identifiers, "
            f"{len(core_params)} core parameters, {len(additional_cols)} additional columns."
        )

        return {
            "month": month_name,
            "status": "VALID",
            "total_columns": len(df.columns),
            "total_rows": len(df),
            "identifiers_present": [col for col in req_identifiers if col in df_cols_stripped],
            "core_parameters_present": [param for param in core_params if param in df_cols_stripped],
            "additional_columns": sorted(additional_cols),
        }

    def validate_monthly_schemas(
        self,
        monthly_dfs: Dict[str, pd.DataFrame],
        save_report: bool = True
    ) -> Dict[str, Any]:
        """Validates schemas across all monthly datasets and generates schema_report.json."""
        month_reports = {}
        for month_name, df in monthly_dfs.items():
            month_reports[month_name] = self.validate_schema(df, month_name)

        overall_report = {
            "validation_timestamp": "deterministic",
            "required_identifiers": REQUIRED_IDENTIFIERS,
            "core_parameters": list(DEFAULT_CONFIG.dataset.core_parameters),
            "months": month_reports
        }

        if save_report:
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.reports_dir / "schema_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(overall_report, f, indent=2)
            logger.info(f"Schema validation report saved to {report_path}")

        return overall_report

    @staticmethod
    def parse_coordinate(coord_val: Any) -> Optional[float]:
        """
        Safely parses coordinate strings in Decimal Degrees, DMS, or Degrees Decimal Minutes format.
        Returns float in decimal degrees, or None if missing/unparseable/NaN.
        """
        if coord_val is None or pd.isna(coord_val):
            return None
        s = str(coord_val).strip()
        if not s or s.upper() in ("NA", "N/A", "NULL", "NONE", "-", "NAN"):
            return None
        try:
            val = float(s)
            if np.isnan(val):
                return None
            return val
        except ValueError:
            pass

        # Strip commas, quotes, and cardinal directions
        cleaned = s.strip().rstrip(",").strip()
        cleaned = re.sub(r"[NnEeSsWw,\'\"]+$", "", cleaned).strip()
        cleaned = re.sub(r"[\u2018\u2019\u201c\u201d\x91\x92\'\"\?]", " ", cleaned).strip()

        # Split components by non-numeric delimiters
        parts = re.split(r"[^\d.]+", cleaned)
        parts = [p for p in parts if p]
        if len(parts) == 2:
            try:
                deg = float(parts[0])
                mins = float(parts[1])
                return deg + mins / 60.0
            except ValueError:
                pass
        elif len(parts) == 3:
            try:
                deg = float(parts[0])
                mins = float(parts[1])
                secs = float(parts[2])
                return deg + mins / 60.0 + secs / 3600.0
            except ValueError:
                pass

        return None

    def validate_station_coordinates(
        self,
        df: pd.DataFrame,
        lat_bounds: Tuple[float, float] = (15.0, 22.5),
        lon_bounds: Tuple[float, float] = (72.0, 81.5),
    ) -> Dict[str, Any]:
        """
        Validates that station coordinates, when present, fall within the Maharashtra bounding box.
        Identifies and flags stations with unrecorded/NA coordinates without crashing.
        """
        df_cols_stripped = {col.strip(): col for col in df.columns}
        lat_col = df_cols_stripped.get("latitude")
        lon_col = df_cols_stripped.get("longitude")
        stn_col = df_cols_stripped.get("STN Code", "STN Code")

        if not lat_col or not lon_col:
            raise DataIntegrityError("Missing latitude or longitude column for coordinate validation.")

        valid_count = 0
        na_count = 0
        out_of_bounds = []

        for _, row in df.iterrows():
            stn = str(row[stn_col]).strip()
            lat = self.parse_coordinate(row[lat_col])
            lon = self.parse_coordinate(row[lon_col])

            if lat is None or lon is None or np.isnan(lat) or np.isnan(lon):
                na_count += 1
            else:
                if not (lat_bounds[0] <= lat <= lat_bounds[1] and lon_bounds[0] <= lon <= lon_bounds[1]):
                    out_of_bounds.append({"stn_code": stn, "lat": lat, "lon": lon})
                else:
                    valid_count += 1

        if out_of_bounds:
            logger.warning(f"Found {len(out_of_bounds)} coordinates outside Maharashtra bounding box: {out_of_bounds[:3]}")

        return {
            "total_stations": len(df),
            "valid_coordinates": valid_count,
            "na_coordinates": na_count,
            "out_of_bounds_count": len(out_of_bounds),
            "out_of_bounds_stations": out_of_bounds,
            "bounds": {"lat": lat_bounds, "lon": lon_bounds}
        }
