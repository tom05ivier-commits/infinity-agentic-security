# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengujian layanan HTTP generator domain."""

from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import domain_manager as dm  # noqa: E402
from system.domain_service import build_server  # noqa: E402


class DomainServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="agenty-domain-http-")
        folder = Path(cls.tmp.name)
        cls.patches = [
            mock.patch.object(dm, "STORE", folder / "local_domains.json"),
            mock.patch.object(dm, "AUDIT", folder / "domain_actions.jsonl"),
            mock.patch.object(dm, "HOSTS", folder / "hosts"),
        ]
        for patch in cls.patches:
            patch.start()
        cls.server = build_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        for patch in reversed(cls.patches):
            patch.stop()
        cls.tmp.cleanup()

    def _get(self, path: str) -> tuple[int, dict]:
        with urllib.request.urlopen(self.base + path, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def _post(self, path: str, data: dict) -> tuple[int, dict]:
        request = urllib.request.Request(
            self.base + path,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_health_and_pages(self) -> None:
        code, data = self._get("/health")
        self.assertEqual(code, 200)
        self.assertEqual(data["service"], "domain")
        for path in ("/", "/guide", "/app.js", "/styles.css"):
            with urllib.request.urlopen(self.base + path, timeout=5) as response:
                self.assertEqual(response.status, 200)
                self.assertGreater(len(response.read()), 100)

    def test_suggest_and_status(self) -> None:
        code, data = self._get("/api/suggest?seed=chip&count=3")
        self.assertEqual(code, 200)
        self.assertEqual(len(data["domains"]), 3)
        self.assertTrue(all(item["host"].endswith(".agenty.local") for item in data["domains"]))
        _, status = self._get("/api/domains")
        self.assertEqual(status["root_domain"], "agenty.local")

    def test_add_remove_and_guard(self) -> None:
        code, data = self._post("/api/domains", {"name": "uji", "target": "127.0.0.1"})
        self.assertEqual(code, 201)
        self.assertEqual(data["domain"]["host"], "uji.agenty.local")
        _, removed = self._post("/api/domains/remove", {"name": "uji"})
        self.assertTrue(removed["removed"])
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post("/api/install", {"authorize": False})
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
