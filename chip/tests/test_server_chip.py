# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian chip verifikasi untuk setiap server localhost (jalur terpisah)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip.server_chip_gen import servers  # noqa: E402
from chip.server_chip_reference import verify_all  # noqa: E402


class ServerChipTests(unittest.TestCase):
    def test_all_servers_have_chip(self) -> None:
        report = verify_all()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["servers"], len(servers()))
        self.assertEqual(report["vectors"], report["servers"] * 8)
        self.assertEqual(report["fabrication"], "NOT_READY")

    def test_rtl_license_and_gate(self) -> None:
        from chip.server_chip_reference import gate

        self.assertEqual(gate(1, 1, 1), {"ready": 1, "degraded": 0, "blocked": 0})
        self.assertEqual(gate(1, 0, 1), {"ready": 0, "degraded": 1, "blocked": 0})
        self.assertEqual(gate(0, 1, 1), {"ready": 0, "degraded": 0, "blocked": 1})
        for s in servers():
            path = ROOT / "chip" / "rtl" / f"srv_{s['sig']}.v"
            self.assertTrue(path.exists(), path)
            head = path.read_text(encoding="utf-8")[:300]
            self.assertIn("SPDX-License-Identifier: Tom05ivier-commits-1.0", head)
            self.assertIn("Copyright (c) 2026 Tomi vier", head)

    def test_main_modules_untouched(self) -> None:
        from chip.reference import MODULES

        self.assertEqual(len(MODULES), 11)
        for name in MODULES:
            self.assertFalse(name.startswith("srv_"))

    def test_registry_is_source_of_truth(self) -> None:
        names = {s["name"] for s in servers()}
        registry = json.loads((ROOT / "system" / "services.json").read_text())
        self.assertEqual(names, {s["name"] for s in registry["services"]})


if __name__ == "__main__":
    unittest.main()
