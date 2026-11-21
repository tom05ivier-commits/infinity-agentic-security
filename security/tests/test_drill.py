# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian integrasi alur cyber range lengkap."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import tempfile  # noqa: E402
import time  # noqa: E402

from security.blue.defense_agent import DefenseAgent  # noqa: E402
from security.blue.monitor import FileMonitor  # noqa: E402
from security.common.authorization import issue_token  # noqa: E402
from security.common.config import EICAR_SIGNATURE  # noqa: E402
from security.red.attack_agent import AttackAgent  # noqa: E402
from security.verify import ComplianceVerifier  # noqa: E402


class DrillIntegrationTests(unittest.TestCase):
    def test_full_cycle_protect_attack_respond(self) -> None:
        """Pertahanan harus mendeteksi artefak yang disebarkan serangan."""
        defense = DefenseAgent()
        protection = defense.protect_hardware()
        self.assertIn("hardware", protection)
        self.assertIn("report", protection)

        token = issue_token(
            token_id="integration-drill",
            issued_by="unittest",
            allowed_targets=("lab", "127.0.0.1"),
            duration_seconds=120,
        )
        attack = AttackAgent(token)
        results = attack.full_drill()
        self.assertEqual(len(results), 4)

        response = defense.respond_to_attack(results)

        # Daemon always-on dapat mengkarantina artefak lebih dulu; itu juga
        # dianggap berhasil selama tidak ada berkas terinfeksi yang tersisa.
        from security.blue.antivirus_agent import AntivirusAgent
        from security.common.config import LAB_ROOT

        remaining = [
            scan
            for scan in AntivirusAgent().scan_directory(LAB_ROOT)
            if scan.infected
        ]
        self.assertTrue(
            len(response["quarantined"]) >= 1 or not remaining,
            "Tidak ada artefak yang dikarantina dan masih ada berkas terinfeksi",
        )
        self.assertGreater(response["risk_score"], 0)
        self.assertIn("DROP", response["firewall_block"]["command"])
        self.assertTrue(Path(response["report"]).exists())

    def test_realtime_monitor_quarantines_dropped_malware(self) -> None:
        """Antivirus real-time harus menangkap malware yang muncul saat aktif."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            monitor = FileMonitor(root, auto_quarantine=True, interval=0.05)
            thread = monitor.start(seconds=2)
            time.sleep(0.1)
            (root / "dropped.bin").write_bytes(EICAR_SIGNATURE)
            time.sleep(0.6)
            monitor.stop()
            thread.join(timeout=2)
            monitor.poll_once()
            report = monitor.report()
            self.assertGreaterEqual(report["detections"], 1)
            self.assertTrue(report["events"][0]["quarantined"])

    def test_compliance_verifier_is_compliant(self) -> None:
        """Seluruh pemeriksaan kepatuhan harus lulus."""
        report = ComplianceVerifier().run()
        self.assertEqual(report["status"], "COMPLIANT")
        self.assertEqual(report["summary"]["fail"], 0)
        self.assertGreaterEqual(len(report["checks"]), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
