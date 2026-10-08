"""
WATERSHIELD Phase 2 Tests: DataCleaner & Numeric Sanitization
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/01_MASTER_PROJECT.md §6
"""

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

from src.data.loader import NWMPDataLoader
from src.data.cleaning import DataCleaner
from src.config import DEFAULT_CONFIG


class TestDataCleaner(unittest.TestCase):
    """Verifies column sanitization, numeric parameter coercion, and BDL normalization."""

    @classmethod
    def setUpClass(cls):
        loader = NWMPDataLoader(raw_data_dir=Path("data/raw"))
        cls.monthly_dfs = loader.load_raw_monthly_data()
        cls.cleaner = DataCleaner()

    def test_sanitize_column_names(self):
        """Verifies whitespace is stripped from column headers."""
        dirty_df = pd.DataFrame({" STN Code ": ["101"], " BOD ": [3.2]})
        clean_df = self.cleaner.sanitize_column_names(dirty_df)
        self.assertListEqual(list(clean_df.columns), ["STN Code", "BOD"])

    def test_coerce_numeric_cell_bdl(self):
        """Verifies Below Detection Limit strings are coerced to numeric detection limits."""
        val, is_bdl = self.cleaner.coerce_numeric_cell("0.3(BDL)")
        self.assertEqual(val, 0.3)
        self.assertTrue(is_bdl)

        val, is_bdl = self.cleaner.coerce_numeric_cell("1(BDL)")
        self.assertEqual(val, 1.0)
        self.assertTrue(is_bdl)

        val, is_bdl = self.cleaner.coerce_numeric_cell("1.8(BDL)")
        self.assertEqual(val, 1.8)
        self.assertTrue(is_bdl)

    def test_coerce_numeric_cell_missing(self):
        """Verifies missing tokens are coerced to np.nan without BDL flag."""
        for token in ["", "NA", "N/A", "ND", "-", "null"]:
            val, is_bdl = self.cleaner.coerce_numeric_cell(token)
            self.assertTrue(np.isnan(val))
            self.assertFalse(is_bdl)

    def test_clean_monthly_dataframe(self):
        """Verifies full cleaning of monthly dataframes."""
        for month, raw_df in self.monthly_dfs.items():
            df_clean, stats = self.cleaner.clean_monthly_dataframe(raw_df, month)
            self.assertEqual(len(df_clean), 222)
            self.assertIn("latitude_dd", df_clean.columns)
            self.assertIn("longitude_dd", df_clean.columns)

            for param in DEFAULT_CONFIG.dataset.core_parameters:
                self.assertIn(param, df_clean.columns)
                self.assertTrue(np.issubdtype(df_clean[param].dtype, np.floating))
                self.assertIn(param, stats["parameters"])


if __name__ == "__main__":
    unittest.main()
