# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengujian watchdog akselerator AI tom05."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip import chip_watch  # noqa: E402


class ChipWatchTests(unittest.TestCase):
    def test_cycle_writes_atomic_report(self) -> None:
        state = {"cycles": 0}
        with tempfile.TemporaryDirectory(prefix="ai-chip-watch-") as tmp:
            target = Path(tmp) / "ai_chip_watch.json"
            with mock.patch.object(chip_watch, "REPORT", target):
                report = chip_watch.cycle(state)
            self.assertTrue(target.exists())
            self.assertFalse(Path(str(target) + ".tmp").exists())
            data = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(data, report)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["cycles"], 1)
        self.assertEqual(report["fabrication"], "NOT_READY")
        self.assertEqual(report["results"]["score"]["score"], 100)
        self.assertEqual(report["bukti"], {"sintesis": "PASS", "browser": "PASS"})

    def test_commands_are_read_only(self) -> None:
        names = [command[0] for _, command in chip_watch.COMMANDS]
        self.assertEqual(names, ["verify", "iverilog", "score"])
        for _, command in chip_watch.COMMANDS:
            self.assertIn(command[0], ("verify", "iverilog", "score"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
