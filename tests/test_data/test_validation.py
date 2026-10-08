"""
WATERSHIELD Phase 2 Tests: DataValidator & Schema Inspection
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/02_REQUIREMENTS.md FR-DATA-05
"""

import unittest
from pathlib import Path
import pandas as pd

from src.data.loader import NWMPDataLoader
from src.data.validation import DataValidator, REQUIRED_IDENTIFIERS
from src.config import DEFAULT_CONFIG
from src.utils.errors import DataIntegrityError


class TestDataValidator(unittest.TestCase):
    """Verifies schema validation, parameter presence, and coordinate checks."""

    @classmethod
    def setUpClass(cls):
        loader = NWMPDataLoader(raw_data_dir=Path("data/raw"))
        cls.monthly_dfs = loader.load_raw_monthly_data()
        cls.validator = DataValidator(reports_dir=Path("data/reports"))

    def test_schema_validation_all_months(self):
        """Verifies that all 3 raw monthly datasets pass schema validation."""
        for month, df in self.monthly_dfs.items():
            result = self.validator.validate_schema(df, month)
            self.assertEqual(result["status"], "VALID")
            self.assertEqual(len(result["core_parameters_present"]), 12)
            for param in DEFAULT_CONFIG.dataset.core_parameters:
                self.assertIn(param, result["core_parameters_present"])

    def test_schema_validation_missing_parameter_raises(self):
        """Verifies that missing core parameters trigger DataIntegrityError."""
        bad_df = pd.DataFrame({"STN Code": ["1001"], "Stn Name": ["Station 1"]})
        with self.assertRaises(DataIntegrityError):
            self.validator.validate_schema(bad_df, "Test Month")

    def test_coordinate_parsing_formats(self):
        """Tests parsing decimal degrees, DMS, and degrees decimal minutes."""
        # Decimal degrees
        self.assertAlmostEqual(self.validator.parse_coordinate("19.4877"), 19.4877, places=4)
        # Degrees Decimal Minutes
        self.assertAlmostEqual(self.validator.parse_coordinate("19°29.263'"), 19.4877, places=3)
        self.assertAlmostEqual(self.validator.parse_coordinate("75°22.272'"), 75.3712, places=3)
        # With cardinal directions and trailing quotes
        self.assertAlmostEqual(self.validator.parse_coordinate("20  ?09.010'N,"), 20.1502, places=3)
        # Missing / NA
        self.assertIsNone(self.validator.parse_coordinate("NA"))
        self.assertIsNone(self.validator.parse_coordinate("-"))
        self.assertIsNone(self.validator.parse_coordinate(""))

    def test_station_coordinate_bounds(self):
        """Verifies that parsed station coordinates fall within Maharashtra bounding box."""
        df_july = self.monthly_dfs["July 2025"]
        bounds_result = self.validator.validate_station_coordinates(df_july)
        self.assertEqual(bounds_result["total_stations"], 222)
        self.assertEqual(bounds_result["na_coordinates"], 6)
        self.assertEqual(bounds_result["valid_coordinates"], 216)
        self.assertEqual(bounds_result["out_of_bounds_count"], 0)


if __name__ == "__main__":
    unittest.main()
