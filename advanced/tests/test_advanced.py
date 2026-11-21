# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian Infinity Advanced Computer."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from advanced.engine import AdvancedComputer  # noqa: E402
from advanced.knowledge import KnowledgeBase  # noqa: E402


class KnowledgeTests(unittest.TestCase):
    def test_indexes_our_data(self) -> None:
        kb = KnowledgeBase()
        stats = kb.stats()
        self.assertGreaterEqual(stats["documents"], 10)
        self.assertIn("LICENSE", stats["sources"])
        self.assertIn("surat-izin-keamanan.md", stats["sources"])

    def test_search_finds_license(self) -> None:
        results = KnowledgeBase().search("Tom05 kommits")
        self.assertTrue(results)
        self.assertTrue(any("LICENSE" in item["source"] for item in results))


class ComputerTests(unittest.TestCase):
    def test_run_cycle(self) -> None:
        result = AdvancedComputer().run("status sistem")
        self.assertTrue(result["tasks"])
        self.assertIn("reflection", result)
        self.assertEqual(result["reflection"]["status"], "SUCCESS")

    def test_until_stops_when_target_reached(self) -> None:
        os.environ["AGENTY_MAX_ITERATIONS"] = "3"
        self.addCleanup(os.environ.pop, "AGENTY_MAX_ITERATIONS", None)
        result = AdvancedComputer().run_until("status sistem")
        self.assertLessEqual(result["iterations"], 3)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["limit"], 3)

    def test_offensive_goal_is_skipped_safely(self) -> None:
        os.environ["AGENTY_MAX_ITERATIONS"] = "2"
        self.addCleanup(os.environ.pop, "AGENTY_MAX_ITERATIONS", None)
        result = AdvancedComputer().run_until("serang lab dengan malware")
        self.assertLessEqual(result["iterations"], 2)
        self.assertEqual(result["status"], "PARTIAL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
