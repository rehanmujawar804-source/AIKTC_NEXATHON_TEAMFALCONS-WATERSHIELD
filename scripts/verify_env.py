"""
WATERSHIELD — Environment & Dependency Verification Script
Checks Python version and imports of all core dependencies.
"""
import sys
import importlib

REQUIRED_PACKAGES = [
    ("pandas", "2.0.0"),
    ("numpy", "1.24.0"),
    ("pyarrow", "14.0.0"),
    ("scipy", "1.11.0"),
    ("sklearn", "1.3.0"),
    ("plotly", "5.15.0"),
    ("streamlit", "1.28.0"),
    ("pytest", "7.4.0"),
]

def main() -> int:
    print("=" * 60)
    print("WATERSHIELD - Environment Verification")
    print("=" * 60)
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version:    {sys.version.split()[0]}")

    if sys.version_info < (3, 11):
        print("\n[WARNING] Python 3.11+ is recommended for WATERSHIELD.")
    else:
        print("[OK] Python version compatible.")

    print("\nChecking required packages...")
    all_ok = True
    for package, min_version in REQUIRED_PACKAGES:
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, "__version__", "unknown")
            print(f"  [OK] {package:<15} (installed: {version})")
        except ImportError:
            print(f"  [MISSING] {package:<15} (minimum required: >={min_version})")
            all_ok = False

    print("=" * 60)
    if all_ok:
        print("Status: ALL CORE DEPENDENCIES AVAILABLE")
        return 0
    else:
        print("Status: MISSING DEPENDENCIES. Please run:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
