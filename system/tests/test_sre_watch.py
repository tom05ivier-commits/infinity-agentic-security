# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian eksekusi otomatis skill sre-engineer di supervisor."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import sre_watch as sw  # noqa: E402


class AssessTests(unittest.TestCase):
    def test_layanan_sehat(self) -> None:
        watch = {"total": 4, "up": 4, "results": [
            {"name": "a", "kind": "http", "status": "UP"},
        ]}
        report = sw.assess(watch, [])
        self.assertEqual(report["status"], "SEHAT")
        self.assertEqual(report["availability"], 1.0)
        self.assertEqual(report["signal"], "BELUM_CUKUP_DATA")
        self.assertEqual(report["owner_ranking"], [])

    def test_error_budget_terlampaui(self) -> None:
        watch = {"total": 4, "up": 3, "results": [
            {"name": "port-x", "kind": "tcp", "status": "DOWN"},
        ]}
        report = sw.assess(watch, [], target=0.99)
        self.assertEqual(report["status"], "WASPADA")
        self.assertGreater(report["error_budget"]["fraction"], 1)
        self.assertEqual(report["owner_ranking"][0]["area"], "network/port")
        self.assertIn("Error budget", report["recommendation"])

    def test_monitor_tidak_masuk_slo(self) -> None:
        watch = {"total": 15, "up": 14, "results": [
            {"name": "web", "kind": "http", "status": "UP"},
            {"name": "port-14713", "kind": "monitor", "status": "DOWN"},
        ]}
        report = sw.assess(watch, [], target=0.99)
        self.assertEqual(report["availability"], 1.0)
        self.assertEqual(report["status"], "SEHAT")
        self.assertEqual(report["informational"][0]["name"], "port-14713")

    def test_regresi_dibedakan_dari_noise(self) -> None:
        watch = {"total": 100, "up": 85, "results": []}
        history = [{"availability": v} for v in (0.99, 0.991, 0.989, 0.99)]
        report = sw.assess(watch, history, target=0.95)
        self.assertEqual(report["signal"], "REGRESI")
        self.assertEqual(report["status"], "WASPADA")

    def test_tanpa_data_tidak_mengklaim_regresi(self) -> None:
        report = sw.assess({"total": 10, "up": 9, "results": []}, [])
        self.assertEqual(report["signal"], "BELUM_CUKUP_DATA")
        self.assertIn("belum dibuktikan", report["residual_risk"])


class RunOnceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.watch = base / "service_watch.json"
        self.report = base / "sre_watch.json"
        self.history = base / "sre_history.jsonl"
        self.watch.write_text(json.dumps({
            "total": 2, "up": 2, "results": [],
        }), encoding="utf-8")

    def test_tulis_laporan_dan_riwayat(self) -> None:
        report = sw.run_once(self.watch, self.report, self.history)
        self.assertTrue(self.report.exists())
        self.assertTrue(self.history.exists())
        self.assertEqual(json.loads(self.report.read_text(encoding="utf-8")), report)
        self.assertEqual(len(sw.read_history(self.history)), 1)

    def test_registry_rusak_tetap_aman(self) -> None:
        self.watch.write_text("bukan json", encoding="utf-8")
        report = sw.run_once(self.watch, self.report, self.history)
        self.assertEqual(report["availability"], 0.0)
        self.assertIn("skill", report)

    def test_riwayat_dibatasi(self) -> None:
        for i in range(sw.MAX_HISTORY + 10):
            sw.append_history({"availability": i / 100}, self.history)
        self.assertEqual(len(sw.read_history(self.history)), sw.MAX_HISTORY)


if __name__ == "__main__":
    unittest.main(verbosity=2)
