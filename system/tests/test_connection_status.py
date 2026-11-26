# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian status koneksi OpenCode/tom05 — read-only dan tanpa kredensial."""

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

from system import connection_status  # noqa: E402


class ConnectionStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = Path(self.tmp.name) / "tom05-connections.json"
        self.config.write_text(json.dumps({
            "license": "Tom05ivier-commits-1.0",
            "endpoints": {
                "a": {"url": "http://127.0.0.1:1111", "role": "aktif"},
                "b": {"url": "http://127.0.0.1:2222", "role": "aktif"},
                "c": {"url": "http://127.0.0.1:3333", "role": "aktif"},
                "kandidat": {
                    "url": "http://127.0.0.1:4444",
                    "role": "kandidat",
                    "status": "tidak_terhubung",
                    "alasan": "protokol belum dikenal",
                },
            },
        }), encoding="utf-8")
        patcher = mock.patch.object(connection_status, "CONFIG", self.config)
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _http_aktif(url: str) -> bool:
        return any(port in url for port in ("1111", "2222", "3333"))

    def test_terhubung_bila_tiga_endpoint_hidup(self) -> None:
        with mock.patch.object(connection_status, "_http",
                               side_effect=self._http_aktif), \
             mock.patch.object(connection_status, "_tcp", return_value=True):
            hasil = connection_status.check()
        self.assertEqual(hasil["status"], "TERHUBUNG")
        self.assertEqual(hasil["terhubung"], ["a", "b", "c"])
        self.assertEqual(len(hasil["endpoint"]), 4)

    def test_sebagian_bila_kurang_dari_tiga(self) -> None:
        def http(url: str) -> bool:
            return "1111" in url

        with mock.patch.object(connection_status, "_http", side_effect=http), \
             mock.patch.object(connection_status, "_tcp", return_value=True):
            hasil = connection_status.check()
        self.assertEqual(hasil["status"], "SEBAGIAN")
        self.assertEqual(hasil["terhubung"], ["a"])

    def test_kandidat_mencantumkan_alasan(self) -> None:
        with mock.patch.object(connection_status, "_http", return_value=False), \
             mock.patch.object(connection_status, "_tcp", return_value=True):
            hasil = connection_status.check()
        kandidat = hasil["endpoint"]["kandidat"]
        self.assertFalse(kandidat["terhubung"])
        self.assertTrue(kandidat["tcp"])
        self.assertEqual(kandidat["alasan"], "protokol belum dikenal")

    def test_tidak_ada_kredensial_dalam_hasil(self) -> None:
        with mock.patch.object(connection_status, "_http",
                               side_effect=self._http_aktif), \
             mock.patch.object(connection_status, "_tcp", return_value=True):
            hasil = connection_status.check()
        teks = json.dumps(hasil).lower()
        for kata in ("token", "password", "secret", "api_key"):
            self.assertNotIn(kata, teks)
        self.assertIn("kredensial", hasil["catatan"].lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
