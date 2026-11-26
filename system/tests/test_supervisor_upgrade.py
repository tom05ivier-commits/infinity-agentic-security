# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.1 — lihat file LICENSE di root proyek.
"""Pengujian peningkatan supervisor: validasi, adopsi PID, dan backoff."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import supervisor as sup  # noqa: E402


class ValidationTests(unittest.TestCase):
    def test_registry_valid_lulus(self) -> None:
        services = [
            {"name": "a", "kind": "process", "command": ["true"]},
            {"name": "b", "kind": "http", "port": 8765, "health": "/"},
            {"name": "m", "kind": "monitor", "port": 14713},
        ]
        self.assertEqual(sup.validate_services(services), [])

    def test_duplikat_dan_command_kosong_ditolak(self) -> None:
        services = [
            {"name": "a", "kind": "process", "command": ["true"]},
            {"name": "a", "kind": "process", "command": []},
            {"name": "b", "kind": "http"},
        ]
        issues = sup.validate_services(services)
        self.assertTrue(any("duplikat" in item for item in issues))
        self.assertTrue(any("command" in item for item in issues))
        self.assertTrue(any("port" in item for item in issues))


class AdoptionTests(unittest.TestCase):
    def test_pid_file_diabadikan_ketika_proses_hidup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "services.json"
            registry.write_text(json.dumps({"services": [
                {"name": "adopt", "kind": "process", "command": ["true"]},
            ]}), encoding="utf-8")
            pid_dir = base / "pids"
            pid_dir.mkdir()
            (pid_dir / "adopt.pid").write_text(
                json.dumps({"pid": os.getpid(), "name": "adopt"}), encoding="utf-8"
            )
            with mock.patch.object(sup, "REGISTRY", registry), \
                 mock.patch.object(sup, "PID_DIR", pid_dir), \
                 mock.patch.object(sup, "HEARTBEAT", base / "heartbeat.json"), \
                 mock.patch.object(sup, "command_matches", return_value=True):
                svc = sup.Supervisor()
                self.assertEqual(svc.adopted.get("adopt"), os.getpid())
                self.assertTrue(svc.is_alive("adopt"))


class BackoffTests(unittest.TestCase):
    def test_restart_bertahap_saat_gagal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "services.json"
            registry.write_text(json.dumps({"services": [
                {"name": "flap", "kind": "process", "command": ["false"]},
            ]}), encoding="utf-8")
            with mock.patch.object(sup, "REGISTRY", registry), \
                 mock.patch.object(sup, "PID_DIR", base / "pids"), \
                 mock.patch.object(sup, "HEARTBEAT", base / "heartbeat.json"), \
                 mock.patch.object(sup.subprocess, "Popen") as popen:
                popen.return_value.pid = 4242
                popen.return_value.poll.return_value = 1
                svc = sup.Supervisor()
                svc.start("flap")
                first = svc.next_start["flap"]
                svc.start("flap")  # masih dalam jendela backoff
                self.assertEqual(popen.call_count, 1)
                self.assertEqual(svc.next_start["flap"], first)
                self.assertGreater(first, 0)


class StatusTests(unittest.TestCase):
    def test_status_melaporkan_masalah_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "services.json"
            registry.write_text(json.dumps({"services": [
                {"name": "x", "kind": "process", "command": []},
            ]}), encoding="utf-8")
            with mock.patch.object(sup, "REGISTRY", registry), \
                 mock.patch.object(sup, "PID_DIR", base / "pids"), \
                 mock.patch.object(sup, "HEARTBEAT", base / "heartbeat.json"):
                report = sup.Supervisor().status()
                self.assertEqual(report[sup.STATUS_KEY], "PERLU_PERBAIKAN")
                self.assertTrue(report["masalah"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
