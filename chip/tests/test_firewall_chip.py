# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian chip firewall (jalur terpisah dari 10 modul utama)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip import firewall_reference as fw  # noqa: E402
from chip.firewall_drill import MUTATIONS, run  # noqa: E402


class FirewallChipTests(unittest.TestCase):
    def test_rtl_files_have_license(self) -> None:
        for name in fw.SPECS:
            path = ROOT / "chip" / "rtl" / f"{name}.v"
            self.assertTrue(path.exists(), path)
            head = path.read_text(encoding="utf-8")[:300]
            self.assertIn("SPDX-License-Identifier: Tom05ivier-commits-1.0", head)
            self.assertIn("Copyright (c) 2026 Tomi vier", head)

    def test_all_vectors_pass(self) -> None:
        for name in fw.SPECS:
            result = fw.verify(name)
            self.assertEqual(result["status"], "PASS", result["details"])
            self.assertGreater(result["vectors"], 0)

    def test_reference_deny_priority(self) -> None:
        # Allow cocok tapi deny juga cocok → decision = 0 (deny menang).
        self.assertEqual(fw.firewall_decide(1, 2, 3, 4, 1, 2, 3, 4, 1,
                                             1, 2, 3, 4, 1), {"decision": 0})
        # Allow cocok, deny tidak aktif → decision = 1.
        self.assertEqual(fw.firewall_decide(1, 2, 3, 4, 9, 9, 9, 9, 0,
                                             1, 2, 3, 4, 1), {"decision": 1})

    def test_mutations_are_caught(self) -> None:
        self.assertEqual(len(MUTATIONS), 4)
        for name, old, new in MUTATIONS:
            text = fw.load_rtl(name)
            self.assertIn(old, text)
            self.assertNotEqual(fw.verify(name, rtl_text=text.replace(old, new, 1))["status"],
                                "PASS")

    def test_drill_report(self) -> None:
        report = run()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["mutation_testing"]["terdeteksi"], 4)
        self.assertGreaterEqual(report["verifikasi"]["vektor"], 16000)
        path = ROOT / "chip" / "reports" / "firewall_chip.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["license"], "Tom05ivier-commits-1.0")

    def test_iverilog_testbench(self) -> None:
        from chip.firewall_iverilog import EXPECTED, run as sim

        self.assertEqual(sum(EXPECTED.values()), 16896)
        result = sim(write=False)
        self.assertIn(result["status"], ("PASS", "SKIP"))
        if result["status"] == "PASS":
            self.assertEqual(result["vectors"], 16896)
            self.assertEqual(result["errors"], 0)
            self.assertEqual(result["lint_warnings"], 0)
            self.assertEqual(result["compile_warnings"], 0)

    def test_cli_firewall_command(self) -> None:
        import subprocess

        done = subprocess.run(
            [sys.executable, str(ROOT / "chip" / "chip_cli.py"), "firewall"],
            capture_output=True, text=True, timeout=180, cwd=str(ROOT),
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["drill"]["vectors"], 16896)
        self.assertIn(data["iverilog"]["status"], ("PASS", "SKIP"))

    def test_main_modules_untouched(self) -> None:
        from chip.reference import MODULES

        # 11 modul utama: 9 modul awal + index_match4 + tom05_ai_accel.
        self.assertEqual(len(MODULES), 11)
        self.assertIn("index_match4", MODULES)
        self.assertNotIn("firewall_match", MODULES)
        self.assertNotIn("firewall_decide", MODULES)


if __name__ == "__main__":
    unittest.main()
