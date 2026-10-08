"""
WATERSHIELD CLI: Prepare & Align NWMP Data
Phase: Scheduled for Phase 3 (Data Pipeline)

Loads raw monthly CSVs from data/raw/, verifies bit-for-bit SHA-256 duplicate July files,
aligns 222 recurring stations, isolates 172 river cohort, computes pre-September scales,
and writes Parquet files to data/processed/.
"""

import sys
import argparse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="WATERSHIELD Data Preparation & Alignment Pipeline"
    )
    parser.add_argument(
        "--raw-dir", default="data/raw", help="Path to raw NWMP CSV directory"
    )
    parser.add_argument(
        "--output-dir", default="data/processed", help="Path to output processed Parquet directory"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("WATERSHIELD - Data Preparation Script (CLI Skeleton)")
    print("=" * 60)
    print(f"Target raw directory:     {args.raw_dir}")
    print(f"Target output directory:  {args.output_dir}")
    print("\n[STATUS] Data pipeline implementation is scheduled for Phase 3.")
    print("To execute, ensure NWMP raw CSV files are placed in data/raw/ during Phase 2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
