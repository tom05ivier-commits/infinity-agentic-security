# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian drill firewall hardware + software."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.firewall_drill import _criteria, run_cycle  # noqa: E402


class FirewallDrillTests(unittest.TestCase):
    def test_criteria_accepts_daemon_quarantine(self) -> None:
        criteria = _criteria(
            protection={"integrity": {"changed": True}},
            response={
                "quarantined": [],
                "integrity": {"changed": True},
            },
            privacy={"publik_aman": 0},
            remaining_infected=0,
        )
        self.assertTrue(criteria["software_dikarantina"])
        self.assertTrue(all(criteria.values()))

    def test_run_cycle_produces_debug(self) -> None:
        result = run_cycle("light")
        self.assertIn("criteria", result)
        self.assertIn("debug", result)
        self.assertIn("remaining_infected", result["debug"])
        self.assertIsInstance(result["success"], bool)


if __name__ == "__main__":
    unittest.main(verbosity=2)
