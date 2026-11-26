# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian agen R.A.M. — laporan memori virtual tanpa perubahan nyata."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.hy4_manager import AGENTS  # noqa: E402
from system.ram_agent import AGENT_MARKDOWN, describe  # noqa: E402
from system.ram_manager import dispatch, plan, status  # noqa: E402


class RamManagerTests(unittest.TestCase):
    def test_agent_registered(self) -> None:
        self.assertIn("ram.md", AGENTS)
        self.assertEqual(AGENTS["ram.md"], AGENT_MARKDOWN)

    def test_no_physical_claim(self) -> None:
        info = describe()
        self.assertFalse(info["physical_ram_change"])
        self.assertEqual(info["agent"], "ram")

    def test_status_shape(self) -> None:
        data = status()
        self.assertEqual(data["status"], "OK")
        self.assertGreater(data["fisik_kb"], 0)
        self.assertGreaterEqual(data["rasio"], 0)
        self.assertEqual(data["target_rasio"], 2)

    def test_plan_is_dry_run(self) -> None:
        data = plan()
        self.assertIn(data["status"], ("TIDAK_PERLU", "RENCANA"))
        self.assertEqual(data["perubahan_diperlukan"], data["status"] == "RENCANA")

    def test_authorization_required(self) -> None:
        for action in ("enable", "disable"):
            data = dispatch(action, False)
            self.assertEqual(data["status"], "DITOLAK")
            self.assertIn("authorize", data["alasan"])

    def test_unknown_action(self) -> None:
        self.assertEqual(dispatch("hapus")["status"], "DITOLAK")


if __name__ == "__main__":
    unittest.main(verbosity=2)
