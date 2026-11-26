# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian manajer domain lokal dan klien DDNS."""

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

from system import ddns_client, domain_manager as dm  # noqa: E402


class DomainManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="agenty-domain-")
        self.folder = Path(self.tmp.name)
        self.patches = [
            mock.patch.object(dm, "STORE", self.folder / "local_domains.json"),
            mock.patch.object(dm, "AUDIT", self.folder / "domain_actions.jsonl"),
            mock.patch.object(dm, "HOSTS", self.folder / "hosts"),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self) -> None:
        for patch in reversed(self.patches):
            patch.stop()
        self.tmp.cleanup()

    def test_suggest_is_deterministic_and_bounded(self) -> None:
        first = dm.suggest("chip", 3)
        self.assertEqual(first, dm.suggest("chip", 3))
        self.assertEqual(len(first), 3)
        self.assertTrue(all(item["available"] for item in first))
        self.assertEqual(len(dm.suggest("chip", 99)), 24)

    def test_add_list_remove_and_audit(self) -> None:
        entry = dm.add("ai-chip")
        self.assertEqual(entry["host"], "ai-chip.agenty.local")
        self.assertFalse(dm.available("ai-chip"))
        self.assertEqual(len(dm.list_domains()), 1)
        with self.assertRaises(ValueError):
            dm.add("ai-chip")
        with self.assertRaises(ValueError):
            dm.add("api", "192.0.2.1")
        self.assertTrue(dm.remove("ai-chip"))
        self.assertEqual(dm.list_domains(), [])
        audit = (self.folder / "domain_actions.jsonl").read_text()
        self.assertIn("domain-add", audit)
        self.assertIn("domain-remove", audit)

    def test_install_requires_authorize_and_writes_backup(self) -> None:
        dm.add("domain")
        with self.assertRaises(PermissionError):
            dm.install_hosts()
        hosts = self.folder / "hosts"
        hosts.write_text("127.0.0.1 localhost\n", encoding="utf-8")
        result = dm.install_hosts(authorize=True)
        self.assertEqual(result["status"], "OK")
        self.assertIn(dm.BEGIN, hosts.read_text())
        self.assertIn("domain.agenty.local", hosts.read_text())
        self.assertTrue((self.folder / "hosts.agenty-backup").exists())


class DdnsClientTests(unittest.TestCase):
    def test_status_has_no_token_values(self) -> None:
        with mock.patch.dict(os.environ, {"DUCKDNS_TOKEN": "rahasia-contoh"}):
            data = ddns_client.status()
        self.assertTrue(data["providers"]["duckdns"]["configured"])
        self.assertNotIn("rahasia-contoh", json.dumps(data, ensure_ascii=False))
        self.assertFalse(data["automatic_updates"])

    def test_update_requires_authorize(self) -> None:
        with self.assertRaises(PermissionError):
            ddns_client.update("duckdns", "contoh.duckdns.org")

    def test_update_rejects_long_ttl(self) -> None:
        with self.assertRaises(ValueError):
            ddns_client.update("duckdns", "contoh", authorize=True, ttl=301)

    def test_update_with_mock_opener(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agenty-ddns-") as folder:
            target = Path(folder) / "ddns.jsonl"
            with mock.patch.dict(os.environ, {"DUCKDNS_TOKEN": "nilai-rahasia"}), \
                 mock.patch.object(ddns_client, "AUDIT", target), \
                 mock.patch("urllib.request.urlopen") as urlopen:
                urlopen.return_value.__enter__.return_value.read.return_value = b"OK 1.2.3.4"
                report = ddns_client.update(
                    "duckdns", "contoh.duckdns.org", authorize=True, ttl=120
                )
            self.assertEqual(report["status"], "OK")
            self.assertEqual(report["ttl"], 120)
            text = target.read_text()
            self.assertIn("ddns-update", text)
            self.assertNotIn("nilai-rahasia", text)
            self.assertNotIn("nilai-rahasia", json.dumps(report))


if __name__ == "__main__":
    unittest.main(verbosity=2)
