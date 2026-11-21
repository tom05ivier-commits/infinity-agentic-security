# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian modul privasi."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.privacy import LABELS, redact, sanitize_tree, scan  # noqa: E402


class PrivacyTests(unittest.TestCase):
    def test_scan_returns_counts_only(self) -> None:
        text = "user@domain.test 081234567890 (__sig__) password: rahasia"
        result = scan(text)
        self.assertEqual(set(result), set(LABELS))
        self.assertGreater(result["email"], 0)
        self.assertGreater(result["whatsapp"], 0)
        self.assertNotIn("user@domain.test", str(result))

    def test_redact_removes_sensitive_values(self) -> None:
        text = "user@domain.test 081234567890 (__sig__) password: rahasia"
        cleaned = redact(text)
        for secret in ("user@domain.test", "081234567890", "__sig__", "rahasia"):
            self.assertNotIn(secret, cleaned)
        self.assertIn("owner@example.invalid", cleaned)
        self.assertIn("(__signature__)", cleaned)
        self.assertIn("[REDACTED]", cleaned)

    def test_sanitize_tree(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "sample.md"
            doc.write_text("email: user@domain.test", encoding="utf-8")
            code = Path(tmp) / "sample.py"
            code.write_text("token = 'abc'", encoding="utf-8")
            result = sanitize_tree(Path(tmp))
            self.assertEqual(result["changed"], 1)
            self.assertNotIn("user@domain.test", doc.read_text(encoding="utf-8"))
            self.assertEqual(code.read_text(encoding="utf-8"), "token = 'abc'")

    def test_code_literal_replaced_safely(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            code = Path(tmp) / "sample.py"
            code.write_text(
                'SIGNATURE = "(__signature__)"\nphone = "000000000000"\n',
                encoding="utf-8",
            )
            sanitize_tree(Path(tmp))
            result = code.read_text(encoding="utf-8")
            self.assertIn("(__signature__)", result)
            self.assertIn("000000000000", result)
            # Sintaks tetap valid.
            compile(result, "sample.py", "exec")


if __name__ == "__main__":
    unittest.main(verbosity=2)
