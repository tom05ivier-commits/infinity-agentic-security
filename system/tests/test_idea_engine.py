# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian mesin ide supervisor (10 ide)."""

import json
import unittest
from pathlib import Path

from system import idea_engine

ROOT = Path(__file__).resolve().parents[2]


class IdeaEngineTests(unittest.TestCase):
    def test_sepuluh_ide_unik(self) -> None:
        ids = [idea["id"] for idea in idea_engine.IDEAS]
        self.assertEqual(len(ids), 10)
        self.assertEqual(len(set(ids)), 10)

    def test_laporan_kerja(self) -> None:
        report = json.loads(idea_engine.REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["dibuat"], 10)
        self.assertEqual(report["selesai"], 10)
        self.assertEqual(report["status"], "OK")

    def test_cli_terdaftar(self) -> None:
        text = (ROOT / "system" / "cli.py").read_text(encoding="utf-8")
        self.assertIn('"ideas"', text)


if __name__ == "__main__":
    unittest.main()
