# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian koneksi OpenCode ↔ OpenCode AI dan data bersama."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.shared_data import verify  # noqa: E402


class SharedDataTests(unittest.TestCase):
    def test_connected(self) -> None:
        report = verify()
        self.assertEqual(report["status"], "TERHUBUNG")
        self.assertEqual(report["workspace"], str(ROOT))

    def test_all_checks_ok(self) -> None:
        report = verify()
        for name, check in report["checks"].items():
            self.assertEqual(check["status"], "OK", f"{name}: {check}")

    def test_mcp_has_required_servers(self) -> None:
        mcp = verify()["checks"]["mcp"]
        self.assertGreaterEqual(mcp["connected"], 7)
        for name in ("filesystem", "github", "new-mcp-server", "playwright"):
            self.assertIn(name, mcp["servers"])

    def test_no_credentials_in_report(self) -> None:
        text = str(verify())
        for token in ("password", "api_key", "authorization", "bearer "):
            self.assertNotIn(token, text.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
