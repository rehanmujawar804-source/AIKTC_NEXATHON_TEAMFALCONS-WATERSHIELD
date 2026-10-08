"""
WATERSHIELD Data Ingestion Module
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/02_REQUIREMENTS.md FR-DATA-01, FR-DATA-02

Loads raw MPCB NWMP monthly CSV files from data/raw/, verifies file integrity,
computes cryptographic SHA-256 hashes, detects duplicate source files,
and returns clean raw DataFrames along with a machine-readable manifest.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import os
import pandas as pd

from src.config import DEFAULT_CONFIG
from src.utils.hashing import compute_file_sha256
from src.utils.logger import get_logger
from src.utils.errors import DataIntegrityError

logger = get_logger("data.loader")


class NWMPDataLoader:
    """Ingests and deduplicates raw NWMP monthly datasets."""

    def __init__(self, raw_data_dir: Optional[Path] = None, reports_dir: Optional[Path] = None):
        self.raw_data_dir = Path(raw_data_dir or DEFAULT_CONFIG.paths.raw_data_dir)
        self.reports_dir = Path(reports_dir or DEFAULT_CONFIG.paths.reports_dir)

    def scan_raw_files(self) -> List[Path]:
        """Discovers all raw CSV files in the raw data directory."""
        if not self.raw_data_dir.exists():
            raise DataIntegrityError(
                f"Raw data directory does not exist: {self.raw_data_dir}",
                details="Expected data/raw containing NWMP CSV files."
            )
        files = sorted(list(self.raw_data_dir.glob("*.csv")))
        if not files:
            raise DataIntegrityError(
                f"No CSV files found in {self.raw_data_dir}",
                details="Raw NWMP data files are required."
            )
        return files

    def generate_manifest(self, save_report: bool = True) -> Dict[str, Any]:
        """
        Scans all raw CSV files, computes SHA-256 hashes, records file metadata,
        and identifies exact bit-for-bit duplicate files.
        """
        raw_files = self.scan_raw_files()
        manifest_entries: List[Dict[str, Any]] = []
        hashes_seen: Dict[str, str] = {}  # sha256 -> canonical filename

        for file_path in raw_files:
            file_size = file_path.stat().st_size
            file_hash = compute_file_sha256(file_path)

            # Detect month based on filename
            filename_lower = file_path.name.lower()
            if "july" in filename_lower:
                month = "July 2025"
            elif "august" in filename_lower:
                month = "August 2025"
            elif "september" in filename_lower:
                month = "September 2025"
            else:
                month = "Unknown"

            # Check duplicate status
            is_duplicate = file_hash in hashes_seen
            duplicate_of = hashes_seen.get(file_hash, None)
            if not is_duplicate:
                hashes_seen[file_hash] = file_path.name

            # Load rows/cols safely using latin1
            try:
                df = pd.read_csv(file_path, encoding="latin1")
                row_count = len(df)
                col_count = len(df.columns)
            except Exception as e:
                logger.error(f"Failed to read CSV for manifest: {file_path.name}: {e}")
                row_count = -1
                col_count = -1

            entry = {
                "filename": file_path.name,
                "file_path": str(file_path.as_posix()),
                "size_bytes": file_size,
                "sha256": file_hash,
                "row_count": row_count,
                "column_count": col_count,
                "month": month,
                "is_duplicate": is_duplicate,
                "duplicate_of": duplicate_of,
                "source_agency": DEFAULT_CONFIG.dataset.source_agency,
                "data_portal": DEFAULT_CONFIG.dataset.data_portal,
                "retrieval_identity": "not available in local artifact",
                "processing_status": "verified"
            }
            manifest_entries.append(entry)

        manifest = {
            "total_raw_files": len(raw_files),
            "unique_file_hashes": len(hashes_seen),
            "files": manifest_entries
        }

        if save_report:
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.reports_dir / "raw_manifest.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            logger.info(f"Raw data manifest saved to {report_path}")

        return manifest

    def load_raw_monthly_data(self) -> Dict[str, pd.DataFrame]:
        """
        Loads raw monthly CSVs, detects duplicate July files via SHA-256 hash,
        ignores redundant duplicates, and returns a dictionary of raw monthly DataFrames:
        {'July 2025': df_july, 'August 2025': df_aug, 'September 2025': df_sep}.
        """
        manifest = self.generate_manifest(save_report=True)
        monthly_dfs: Dict[str, pd.DataFrame] = {}

        # Canonical mapping by month
        for entry in manifest["files"]:
            month = entry["month"]
            if month not in ("July 2025", "August 2025", "September 2025"):
                continue

            if entry["is_duplicate"]:
                logger.warning(
                    f"Skipping duplicate raw file {entry['filename']} (bit-for-bit duplicate of {entry['duplicate_of']})"
                )
                continue

            if month in monthly_dfs:
                logger.warning(f"Multiple unique files for {month}; retaining first encountered.")
                continue

            file_path = self.raw_data_dir / entry["filename"]
            logger.info(f"Loading raw monthly dataset: {month} from {entry['filename']}")
            
            # Raw CSVs use Windows-1252 / latin1 encoding (e.g. byte 0xb0 for degree symbol)
            df = pd.read_csv(file_path, encoding="latin1")
            monthly_dfs[month] = df

        expected_months = {"July 2025", "August 2025", "September 2025"}
        missing_months = expected_months - set(monthly_dfs.keys())
        if missing_months:
            raise DataIntegrityError(
                f"Missing monthly datasets in data/raw: {sorted(list(missing_months))}",
                details=f"Expected datasets for July, August, and September 2025. Found: {list(monthly_dfs.keys())}"
            )

        return monthly_dfs
