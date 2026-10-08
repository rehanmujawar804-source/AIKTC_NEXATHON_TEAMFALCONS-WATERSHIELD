"""
WATERSHIELD Hashing and Provenance Utilities
Traceability: DOCS/04_ARCHITECTURE.md §7.3, DOCS/02_REQUIREMENTS.md FR-DATA-02

Provides cryptographic SHA-256 file and configuration hashing utilities.
Supports duplicate detection, cache invalidation, and experiment reproducibility.
Hashes must be computed directly from actual file contents or config dictionaries, never fabricated.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Union


def compute_file_sha256(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    """
    Computes the SHA-256 hex digest of a file in chunks to handle large datasets.

    Args:
        file_path: Absolute or relative path to the file.
        chunk_size: Byte chunk size for reading (default: 64KB).

    Returns:
        Uppercase hex string of the SHA-256 hash.

    Raises:
        FileNotFoundError: If the target file does not exist.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Cannot compute hash: file does not exist at {path}")

    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)

    return sha256.hexdigest().upper()


def compute_string_sha256(data: str) -> str:
    """Computes SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest().upper()


def compute_dict_hash(data: Dict[str, Any]) -> str:
    """
    Computes deterministic SHA-256 hash of a dictionary by sorting keys.
    Useful for creating cache keys from configuration objects.
    """
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest().upper()


def verify_file_hash(file_path: Union[str, Path], expected_hash: str) -> bool:
    """Verifies whether a file matches the expected SHA-256 hash."""
    actual_hash = compute_file_sha256(file_path)
    return actual_hash.upper() == expected_hash.strip().upper()
