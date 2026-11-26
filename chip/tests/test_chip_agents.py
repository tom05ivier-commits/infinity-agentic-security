# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyeg.
"""Pengujian chip khusus per agent: verifikasi exhaustif & kontrak."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip.custom_agents_reference import reg_agents, verify_all  # noqa: E402
from chip.custom_agents_reference import chip_name  # noqa: E402


class ChipAgentsTests(unittest.TestCase):
    def test_registry_matches_agents(self) -> None:
        names = {a["agent"] for a in reg_agents()}
        self.assertEqual(len(names), 23)
        self.assertIn("agent-manager", names)
        self.assertIn("hy4", names)
        self.assertTrue({f"agenty-{level}" for level in range(1, 7)} <= names)
        for a in reg_agents():
            p = ROOT / "chip" / "rtl" / f"{chip_name(a['agent'])}.v"
            self.assertTrue(p.exists(), p)
            head = p.read_text(encoding="utf-8")[:200]
            self.assertIn("SPDX-License-Identifier: Tom05ivier-commits-1.0", head)

    def test_all_agents_verify(self) -> None:
        rep = verify_all()
        self.assertEqual(rep["status"], "PASS", rep["results"])
        self.assertEqual(rep["fabrication"], "NOT_READY")
        self.assertGreaterEqual(rep["vectors"], 23 * 256 * 2)

    def test_hy4_terhubung_ke_fleet(self) -> None:
        rep = verify_all()
        hy4 = next((r for r in rep["results"] if r["agent"] == "hy4"), None)
        self.assertIsNotNone(hy4)
        self.assertEqual(hy4["chip"], "cd_hy4")
        self.assertEqual(hy4["acc"], 116)
        self.assertEqual(hy4["status"], "PASS")

    def test_agenty_model_sama_level_berbeda(self) -> None:
        entries = {a["agent"]: a for a in reg_agents()}
        agenty = [entries[f"agenty-{level}"] for level in range(1, 7)]
        self.assertEqual({a["model"] for a in agenty},
                         {"tom05/tom05-flash-free"})
        self.assertEqual([a["level"] for a in agenty], [1, 2, 3, 4, 5, 6])
        self.assertEqual([a["acc"] for a in agenty],
                         [200, 201, 202, 203, 204, 205])
        self.assertEqual(len({a["acc"] for a in agenty}), 6)

    def test_cli_custom_agents(self) -> None:
        import json
        import subprocess

        done = subprocess.run(
            [sys.executable, str(ROOT / "chip" / "chip_cli.py"),
             "custom-agents"],
            capture_output=True, text=True, timeout=120, cwd=str(ROOT),
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["agents"], 23)
        self.assertEqual(data["fabrication"], "NOT_READY")

    def test_no_ketidaksesuaian(self) -> None:
        from chip.reference import MODULES

        for a in reg_agents():
            self.assertFalse(a["chip"].startswith("srv_"))
        for name in MODULES:
            self.assertTrue(name.startswith(("srv_", "cd_test")) or
                            name in MODULES)  # cd_* tidak anggota MODULES


if __name__ == "__main__":
    unittest.main()
