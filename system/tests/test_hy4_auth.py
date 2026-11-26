# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian pemeriksa otorisasi publik."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.hy4_auth import guide, local_status, scan_public  # noqa: E402


class Hy4AuthTests(unittest.TestCase):
    def test_guide_exists(self) -> None:
        guide_data = guide()
        self.assertIn("token tidak dibagikan", guide_data["prinsip"].lower())
        self.assertIn("opencode auth login", guide_data["langkah"])

    def test_local_status_has_no_secret_values(self) -> None:
        status = local_status()
        for key in ("opencode_auth", "copilot_auth", "bridge_provider_key", "env_api_key"):
            self.assertIsInstance(status[key], bool)
        self.assertNotIn("token", " ".join(str(v) for v in status.values()).lower())

    def test_public_scan_is_safe(self) -> None:
        result = scan_public()
        self.assertIn(result["status"], ("AMAN", "BOCOR"))
        self.assertIsInstance(result["findings"], list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
