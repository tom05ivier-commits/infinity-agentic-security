# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengujian layanan HTTP status chip AI tom05."""

from __future__ import annotations

import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.ai_chip_service import build_server, status  # noqa: E402


class AiChipServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = build_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def _get(self, path: str) -> tuple[int, dict]:
        with urllib.request.urlopen(self.base + path, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_status_reads_real_evidence(self) -> None:
        data = status()
        self.assertEqual(data["service"], "ai-chip")
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["fabrication"], "NOT_READY")
        self.assertTrue(all(data["checks"].values()))
        self.assertEqual(data["module"]["name"], "tom05_ai_accel")
        self.assertEqual(data["license"], "Tom05ivier-commits-1.0")

    def test_health_endpoint(self) -> None:
        code, data = self._get("/health")
        self.assertEqual(code, 200)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["fabrication"], "NOT_READY")

    def test_status_endpoint(self) -> None:
        code, data = self._get("/status")
        self.assertEqual(code, 200)
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["bukti"]["score"]["score"], 100)

    def test_capabilities_endpoint(self) -> None:
        code, data = self._get("/capabilities")
        self.assertEqual(code, 200)
        self.assertEqual(data["module"], "tom05_ai_accel")
        self.assertIn("tom05 --ai-chip", data["cli"])
        self.assertEqual(data["supervisor"], ["ai-chip", "ai-chip-watch"])
        self.assertEqual(data["fabrication"], "NOT_READY")

    def test_unknown_path(self) -> None:
        try:
            self._get("/tidak-ada")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)
        else:
            self.fail("path tidak dikenal harus 404")


if __name__ == "__main__":
    unittest.main(verbosity=2)
