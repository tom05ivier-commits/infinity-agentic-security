# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian jalur kelola read-only NEURO-25 + 23 chip agen kustom."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip.neuro25_fleet import report  # noqa: E402


class Neuro25FleetTests(unittest.TestCase):
    def test_gabungan_pass(self) -> None:
        data = report()
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["agents"]["count"], 23)
        self.assertTrue(
            any(item["agent"] == "hy4" for item in data["agents"]["items"])
        )
        self.assertTrue(data["neuro25"]["safety_gate"])

    def test_status_tidak_diubah(self) -> None:
        neuro = report()["neuro25"]
        self.assertEqual(neuro["fabrication"], "NOT_READY")
        self.assertEqual(neuro["clinical_validation"], "NOT_VALIDATED")
        self.assertFalse(neuro["medical_device"])

    def test_akses_dibatasi(self) -> None:
        data = report()
        self.assertEqual(data["allowed"], ["verify", "status", "report"])
        self.assertIn("change_fabrication", data["denied"])
        self.assertIn("subject_data", data["denied"])

    def test_cli_fleet(self) -> None:
        done = subprocess.run(
            [sys.executable, str(ROOT / "chip" / "chip_cli.py"), "fleet"],
            capture_output=True, text=True, timeout=60, cwd=str(ROOT),
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn('"status": "PASS"', done.stdout)


if __name__ == "__main__":
    unittest.main()
