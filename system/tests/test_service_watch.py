# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian watchdog layanan turunan PyUptimeKit (MIT)."""

from __future__ import annotations

import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import service_watch as sw  # noqa: E402


class ProbeTests(unittest.TestCase):
    def test_tcp_up_mengukur_latensi(self) -> None:
        sock = mock.MagicMock()
        sock.connect_ex.return_value = 0
        with mock.patch.object(sw.socket, "socket", return_value=sock):
            result = sw.tcp_probe("127.0.0.1", 8782)
        self.assertEqual(result["status"], "UP")
        self.assertIsInstance(result["latency_ms"], float)
        sock.close.assert_called_once()

    def test_tcp_down_tanpa_latensi(self) -> None:
        sock = mock.MagicMock()
        sock.connect_ex.return_value = 111
        with mock.patch.object(sw.socket, "socket", return_value=sock):
            result = sw.tcp_probe("127.0.0.1", 1)
        self.assertEqual(result["status"], "DOWN")
        self.assertIsNone(result["latency_ms"])

    def test_tcp_timeout_ditangani(self) -> None:
        sock = mock.MagicMock()
        sock.connect_ex.side_effect = socket.timeout("timeout")
        with mock.patch.object(sw.socket, "socket", return_value=sock):
            result = sw.tcp_probe("127.0.0.1", 8782)
        self.assertEqual(result["status"], "DOWN")
        self.assertIn("timeout", result["message"].lower())

    def test_http_up(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.status = 200
        with mock.patch.object(sw.urllib.request, "urlopen", return_value=response):
            result = sw.http_probe(8765, "/api/health")
        self.assertEqual(result["status"], "UP")
        self.assertEqual(result["http_status"], 200)

    def test_http_down(self) -> None:
        with mock.patch.object(sw.urllib.request, "urlopen",
                               side_effect=OSError("refused")):
            result = sw.http_probe(1)
        self.assertEqual(result["status"], "DOWN")
        self.assertIsNone(result["http_status"])


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.registry = self.base / "services.json"
        self.heartbeat = self.base / "heartbeat.json"
        self.report = self.base / "service_watch.json"
        self.registry.write_text(json.dumps({"services": [
            {"name": "web", "kind": "http", "port": 8765, "health": "/api/health"},
            {"name": "port-9999", "kind": "monitor", "port": 9999},
            {"name": "worker", "kind": "process", "command": ["true"]},
        ]}), encoding="utf-8")
        self.heartbeat.write_text(json.dumps({"services": {
            "worker": {"alive": True},
        }}), encoding="utf-8")

    def test_check_services_memakai_kind_yang_tepat(self) -> None:
        with mock.patch.object(sw, "http_probe", return_value={"status": "UP"}), \
             mock.patch.object(sw, "tcp_probe", return_value={"status": "DOWN"}):
            report = sw.check_services(self.registry, self.heartbeat)
        statuses = {item["name"]: item["status"] for item in report["results"]}
        self.assertEqual(statuses, {
            "web": "UP", "port-9999": "DOWN", "worker": "UP",
        })
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["up"], 2)
        self.assertEqual(report["down"], 1)

    def test_write_report_dan_run_once(self) -> None:
        with mock.patch.object(sw, "REGISTRY", self.registry), \
             mock.patch.object(sw, "HEARTBEAT", self.heartbeat), \
             mock.patch.object(sw, "REPORT", self.report), \
             mock.patch.object(sw, "http_probe", return_value={"status": "UP"}), \
             mock.patch.object(sw, "tcp_probe", return_value={"status": "UP"}):
            report = sw.run_once()
        self.assertTrue(self.report.exists())
        self.assertEqual(json.loads(self.report.read_text(encoding="utf-8")), report)
        self.assertEqual(report["source"], "service-watch")

    def test_registry_rusak_tetap_menghasilkan_laporan(self) -> None:
        self.registry.write_text("bukan json", encoding="utf-8")
        report = sw.check_services(self.registry, self.heartbeat)
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["results"], [])

    def test_render_html_escape(self) -> None:
        report = {"checked_at": "x", "up": 0, "total": 1, "results": [
            {"name": "<script>", "kind": "http", "status": "DOWN",
             "message": "&"},
        ]}
        rendered = sw._render(report)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&amp;", rendered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
