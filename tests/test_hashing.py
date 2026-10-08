"""
Unit Tests for Cryptographic Hashing Utilities
Traceability: src/utils/hashing.py
"""

import unittest
import tempfile
from pathlib import Path
from src.utils.hashing import (
    compute_file_sha256,
    compute_string_sha256,
    compute_dict_hash,
    verify_file_hash,
)


class TestHashing(unittest.TestCase):
    """Verifies deterministic behavior of hashing routines."""

    def test_compute_string_sha256(self):
        # Known SHA-256 for empty string: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        expected_empty = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
        self.assertEqual(compute_string_sha256(""), expected_empty)

    def test_compute_dict_hash_order_invariance(self):
        d1 = {"budget": 20, "policy": "Risk", "seed": 42}
        d2 = {"seed": 42, "budget": 20, "policy": "Risk"}
        self.assertEqual(compute_dict_hash(d1), compute_dict_hash(d2))

    def test_compute_file_sha256_and_verify(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("WATERSHIELD TEST PAYLOAD")
            tmp_path = Path(tmp.name)

        try:
            file_hash = compute_file_sha256(tmp_path)
            self.assertEqual(len(file_hash), 64)
            self.assertTrue(verify_file_hash(tmp_path, file_hash))
            self.assertFalse(verify_file_hash(tmp_path, "INCORRECT_HASH"))
        finally:
            tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
