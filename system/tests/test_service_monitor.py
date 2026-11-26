# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian layanan monitor (TCP-only) dan determinisme gate pembaruan."""

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

from system import cli, supervisor, update_all  # noqa: E402


class ServiceAddMonitorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.registry = base / "system" / "services.json"
        self.registry.parent.mkdir(parents=True)
        self.registry.write_text(
            json.dumps({"services": [{"name": "lama", "kind": "process",
                                      "command": ["true"]}]}),
            encoding="utf-8",
        )
        patcher = mock.patch.object(cli, "ROOT", base)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _entries(self) -> dict[str, dict]:
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        return {item["name"]: item for item in data["services"]}

    def test_monitor_diterima_tanpa_cmd(self) -> None:
        code = cli.main([
            "service-add", "--name", "port-9999", "--kind", "monitor",
            "--port", "9999",
        ])
        self.assertEqual(code, 0)
        entry = self._entries()["port-9999"]
        self.assertEqual(entry["kind"], "monitor")
        self.assertEqual(entry["command"], ["true"])
        self.assertEqual(entry["port"], 9999)
        self.assertNotIn("health", entry)

    def test_monitor_mengganti_nama_sama(self) -> None:
        cli.main(["service-add", "--name", "port-9999", "--kind", "monitor",
                  "--port", "9999"])
        cli.main(["service-add", "--name", "port-9999", "--kind", "monitor",
                  "--port", "10000"])
        names = list(self._entries())
        self.assertEqual(names.count("port-9999"), 1)
        self.assertEqual(self._entries()["port-9999"]["port"], 10000)

    def test_proses_tetap_wajib_cmd(self) -> None:
        code = cli.main(["service-add", "--name", "x", "--kind", "process"])
        self.assertEqual(code, 1)
        self.assertNotIn("x", self._entries())

    def test_nama_tetap_wajib(self) -> None:
        code = cli.main(["service-add", "--kind", "monitor", "--port", "1"])
        self.assertEqual(code, 1)


class SupervisorMonitorTests(unittest.TestCase):
    def _supervisor(self, services: list[dict]) -> supervisor.Supervisor:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        registry = Path(tmp.name) / "services.json"
        registry.write_text(json.dumps({"services": services}), encoding="utf-8")
        patcher = mock.patch.object(supervisor, "REGISTRY", registry)
        patcher.start()
        self.addCleanup(patcher.stop)
        return supervisor.Supervisor()

    def test_is_alive_memakai_port(self) -> None:
        svc = self._supervisor([
            {"name": "m", "kind": "monitor", "port": 12345,
             "command": ["true"]},
        ])
        with mock.patch.object(supervisor, "port_open", return_value=True) as probe:
            self.assertTrue(svc.is_alive("m"))
        probe.assert_called_once_with(12345)

    def test_kind_tcp_juga_dipantau(self) -> None:
        svc = self._supervisor([
            {"name": "t", "kind": "tcp", "port": 23456,
             "command": ["true"]},
        ])
        with mock.patch.object(supervisor, "port_open", return_value=False) as probe:
            self.assertFalse(svc.is_alive("t"))
        probe.assert_called_once_with(23456)

    def test_start_tidak_menjalankan_proses(self) -> None:
        svc = self._supervisor([
            {"name": "m", "kind": "monitor", "port": 12345,
             "command": ["true"]},
        ])
        with mock.patch.object(supervisor.subprocess, "Popen") as popen:
            svc.start("m")
        popen.assert_not_called()
        self.assertNotIn("m", svc.processes)
        self.assertNotIn("m", svc.restarts)


class StalePrepareErrorTests(unittest.TestCase):
    def test_bersihkan_error_lama(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        manifest = Path(tmp.name) / "data_manifest.json"
        stale = [manifest.parent / n for n in (
            "prepare_github_error.txt", "prepare_hy4_error.txt",
        )]
        for path in stale:
            path.write_text("gagal lama", encoding="utf-8")
        with mock.patch.object(update_all, "MANIFEST", manifest):
            update_all._clean_stale_prepare_errors()
        self.assertTrue(all(not path.exists() for path in stale))

    def test_aman_bila_tidak_ada(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        with mock.patch.object(update_all, "MANIFEST", Path(tmp.name) / "m.json"):
            update_all._clean_stale_prepare_errors()


if __name__ == "__main__":
    unittest.main(verbosity=2)
