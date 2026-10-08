"""
WATERSHIELD Phase 2 Tests: StationAligner & Cohort Stratification
Traceability: DOCS/04_ARCHITECTURE.md §3.2, DOCS/02_REQUIREMENTS.md FR-DATA-03, FR-DATA-04
"""

import unittest
from pathlib import Path
import pandas as pd

from src.data.loader import NWMPDataLoader
from src.data.cleaning import DataCleaner
from src.data.alignment import StationAligner
from src.config import DEFAULT_CONFIG


class TestStationAligner(unittest.TestCase):
    """Verifies station recurrence (222 stations), river cohort (172 stations), and metadata audits."""

    @classmethod
    def setUpClass(cls):
        loader = NWMPDataLoader(raw_data_dir=Path("data/raw"))
        raw_dfs = loader.load_raw_monthly_data()
        cleaner = DataCleaner()
        cls.cleaned_dfs = {m: cleaner.clean_monthly_dataframe(df, m)[0] for m, df in raw_dfs.items()}
        cls.aligner = StationAligner(reports_dir=Path("data/reports"))

    def test_recurring_stations_count(self):
        """Empirically verifies exactly 222 recurring stations across July, August, September."""
        base_df, recurring_codes, report = self.aligner.extract_recurring_stations(
            self.cleaned_dfs, save_report=False
        )
        self.assertEqual(len(recurring_codes), 222)
        self.assertEqual(len(base_df), 222)
        self.assertTrue(report["recurrence_verified"])
        self.assertEqual(report["total_recurring_stations"], DEFAULT_CONFIG.dataset.total_recurring_stations)

    def test_river_cohort_filtering(self):
        """Empirically verifies exactly 172 river stations and 50 non-river stations."""
        base_df, recurring_codes, _ = self.aligner.extract_recurring_stations(
            self.cleaned_dfs, save_report=False
        )
        river_df, river_codes, report = self.aligner.filter_river_cohort(base_df, save_report=False)

        self.assertEqual(len(river_codes), 172)
        self.assertEqual(len(river_df), 172)
        self.assertEqual(report["primary_river_cohort_stations"], DEFAULT_CONFIG.dataset.primary_river_cohort_stations)
        self.assertEqual(report["secondary_non_river_stations"], DEFAULT_CONFIG.dataset.secondary_non_river_stations)
        self.assertEqual(report["water_body_type_distribution"]["River"], 172)
        self.assertEqual(report["water_body_type_distribution"]["Creek"], 20)
        self.assertEqual(report["water_body_type_distribution"]["Sea"], 15)
        self.assertEqual(report["water_body_type_distribution"]["Nala"], 10)
        self.assertEqual(report["water_body_type_distribution"]["Dam"], 4)
        self.assertEqual(report["water_body_type_distribution"]["Lake"], 1)

    def test_metadata_consistency_checks(self):
        """Verifies metadata consistency audits across months."""
        _, recurring_codes, _ = self.aligner.extract_recurring_stations(
            self.cleaned_dfs, save_report=False
        )
        report = self.aligner.check_metadata_consistency(
            self.cleaned_dfs, recurring_codes, save_report=False
        )
        fields = report["metadata_fields"]

        # Station Name: exactly 1 Jul->Aug change, 0 Aug->Sep
        self.assertEqual(fields["station_name"]["july_to_august_change_count"], 1)
        self.assertEqual(fields["station_name"]["august_to_september_change_count"], 0)

        # Invariant spatial/geographic metadata: 0 changes
        self.assertEqual(fields["water_body_type"]["july_to_august_change_count"], 0)
        self.assertEqual(fields["water_body_name"]["july_to_august_change_count"], 0)
        self.assertEqual(fields["district"]["july_to_august_change_count"], 0)
        self.assertEqual(fields["latitude"]["july_to_august_change_count"], 0)
        self.assertEqual(fields["longitude"]["july_to_august_change_count"], 0)

        # Use Based Class: changes exist across months (empirically justifying exclusion)
        self.assertGreater(fields["use_based_class"]["july_to_august_change_count"], 0)
        self.assertGreater(fields["use_based_class"]["august_to_september_change_count"], 0)
        self.assertTrue(report["use_based_class_excluded_from_features"])

    def test_missingness_and_numeric_reports(self):
        """Verifies missingness and numeric profiling report generation without failure."""
        base_df, recurring_codes, _ = self.aligner.extract_recurring_stations(
            self.cleaned_dfs, save_report=False
        )
        river_df, river_codes, _ = self.aligner.filter_river_cohort(base_df, save_report=False)

        miss_report = self.aligner.generate_missingness_report(
            self.cleaned_dfs, recurring_codes, save_report=False
        )
        self.assertEqual(len(miss_report["monthly_profiles"]), 3)

        num_report = self.aligner.generate_numeric_quality_report(
            self.cleaned_dfs, river_codes, save_report=False
        )
        self.assertEqual(len(num_report["monthly_profiles"]), 3)
        for m in self.cleaned_dfs.keys():
            self.assertEqual(num_report["monthly_profiles"][m]["river_station_count"], 172)


if __name__ == "__main__":
    unittest.main()
