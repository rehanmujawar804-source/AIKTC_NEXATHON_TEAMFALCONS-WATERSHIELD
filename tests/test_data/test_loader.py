"""
WATERSHIELD Phase 2 Tests: NWMPDataLoader & File Integrity
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/02_REQUIREMENTS.md FR-DATA-01, FR-DATA-02
"""

import unittest
from pathlib import Path
import pandas as pd

from src.data.loader import NWMPDataLoader
from src.utils.hashing import compute_file_sha256
from src.utils.errors import DataIntegrityError


class TestNWMPDataLoader(unittest.TestCase):
    """Verifies raw CSV scanning, SHA-256 hash calculation, and duplicate detection."""

    def setUp(self):
        self.raw_dir = Path("data/raw")
        self.reports_dir = Path("data/reports")
        self.loader = NWMPDataLoader(raw_data_dir=self.raw_dir, reports_dir=self.reports_dir)

    def test_raw_files_discovery(self):
        """Asserts all expected NWMP raw CSV files are discovered."""
        files = self.loader.scan_raw_files()
        filenames = [f.name for f in files]
        self.assertIn("NWMP_July2025.csv", filenames)
        self.assertIn("NWMP_August2025_MPCB_0.csv", filenames)
        self.assertIn("NWMP_September2025_MPCB_0.csv", filenames)
        self.assertGreaterEqual(len(files), 3)

    def test_raw_manifest_generation(self):
        """Verifies manifest contains valid hashes and row counts."""
        manifest = self.loader.generate_manifest(save_report=False)
        self.assertIn("files", manifest)
        self.assertGreaterEqual(manifest["total_raw_files"], 3)

        for entry in manifest["files"]:
            self.assertIn("filename", entry)
            self.assertIn("sha256", entry)
            self.assertEqual(len(entry["sha256"]), 64)
            self.assertGreater(entry["size_bytes"], 0)
            self.assertEqual(entry["row_count"], 222)

    def test_july_duplicate_detection(self):
        """Verifies that duplicate July source files are detected as bit-for-bit identical."""
        manifest = self.loader.generate_manifest(save_report=False)
        july_entries = [e for e in manifest["files"] if e["month"] == "July 2025"]

        if len(july_entries) >= 2:
            h1 = july_entries[0]["sha256"]
            h2 = july_entries[1]["sha256"]
            self.assertEqual(h1, h2, "July source files should have identical SHA-256 digests.")
            duplicates = [e for e in july_entries if e["is_duplicate"]]
            self.assertEqual(len(duplicates), 1)

    def test_load_raw_monthly_data_deduplication(self):
        """Verifies loader returns exactly 3 canonical monthly DataFrames with 222 rows each."""
        monthly_dfs = self.loader.load_raw_monthly_data()
        self.assertEqual(set(monthly_dfs.keys()), {"July 2025", "August 2025", "September 2025"})

        for month, df in monthly_dfs.items():
            self.assertEqual(len(df), 222, f"{month} should contain exactly 222 raw records.")
            self.assertIn("STN Code", [c.strip() for c in df.columns])


if __name__ == "__main__":
    unittest.main()
