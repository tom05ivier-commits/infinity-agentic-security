# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengujian scorecard kualitas chip."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip.scorecard import CHECKS, build  # noqa: E402


class ScorecardTests(unittest.TestCase):
    def test_ten_criteria(self) -> None:
        self.assertEqual(len(CHECKS), 10)

    def test_build_is_perfect(self) -> None:
        report = build()
        self.assertEqual(report["score"], 100)
        self.assertEqual(report["maximum"], 100)
        self.assertEqual(report["grade"], "100/100")
        self.assertEqual(report["status"], "PERFECT")
        self.assertEqual(report["failed"], [])
        self.assertTrue(all(item["points"] == 10 for item in report["checks"]))

    def test_report_written(self) -> None:
        build()
        path = ROOT / "chip" / "reports" / "chip_score.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["grade"], "100/100")
        self.assertIn("Tom05ivier-commits-1.0", data["license"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
