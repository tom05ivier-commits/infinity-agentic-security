# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian kebijakan akses lokal tunggal."""

import json
import unittest
from pathlib import Path

from system import local_access

ROOT = Path(__file__).resolve().parents[2]


class LocalAccessTests(unittest.TestCase):
    def test_konfigurasi(self) -> None:
        data = local_access.load()
        self.assertEqual(data["data_root"], str(ROOT))
        self.assertEqual(data["only_agent_port"], 8785)

    def test_aturan_izin(self) -> None:
        rules = json.loads(local_access.OPENCODE_CONFIG.read_text(encoding="utf-8"))
        pairs = {(r.get("action"), r.get("resource")): r.get("effect")
                 for r in rules.get("permissions", [])}
        self.assertEqual(pairs.get(("webfetch", "http://127.0.0.1:*")), "deny")
        self.assertEqual(pairs.get(("webfetch", "http://127.0.0.1:8785/*")), "allow")

    def test_verifikasi(self) -> None:
        self.assertEqual(local_access.verify()["status"], "OK")


if __name__ == "__main__":
    unittest.main()
