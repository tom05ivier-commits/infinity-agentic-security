# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian scorecard kualitas Tom05."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.tom05_score import CHECKS, build  # noqa: E402


class Tom05ScoreTests(unittest.TestCase):
    def test_ten_criteria(self) -> None:
        self.assertEqual(len(CHECKS), 10)

    def test_perfect(self) -> None:
        report = build()
        self.assertEqual(report["score"], 100)
        self.assertEqual(report["status"], "PERFECT")
        self.assertEqual(report["grade"], "100/100")
        self.assertEqual(report["failed"], [])
        self.assertEqual(report["total_bootstrap"], "500/500")
        self.assertTrue(all(item["points"] == 10 for item in report["checks"]))

    def test_report_written(self) -> None:
        build()
        path = ROOT / "system" / "reports" / "tom05_score.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["grade"], "100/100")
        self.assertIn("Tom05ivier-commits-1.0", data["license"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
