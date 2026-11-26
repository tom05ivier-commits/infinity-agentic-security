# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian alur pengukuran GPU ponsel yang aman."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.gpu_benchmark import MARKER, parse_result  # noqa: E402


class GpuBenchmarkTests(unittest.TestCase):
    def test_valid_result(self) -> None:
        payload = json.dumps({
            "benchmark": MARKER,
            "status": "OK",
            "adapter": {"vendor": "qualcomm"},
            "elapsed_ms": 12.5,
        })
        data = parse_result(payload)
        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["elapsed_ms"], 12.5)

    def test_foreign_clipboard_rejected(self) -> None:
        self.assertEqual(
            parse_result("kata sandi rahasia")["status"],
            "CLIPBOARD_BUKAN_HASIL_BENCHMARK",
        )

    def test_wrong_marker_rejected(self) -> None:
        self.assertEqual(
            parse_result(json.dumps({"benchmark": "lain", "status": "OK"}))["status"],
            "CLIPBOARD_BUKAN_HASIL_BENCHMARK",
        )

    def test_parse_result_keeps_display_profile(self) -> None:
        payload = json.dumps({
            "benchmark": MARKER,
            "status": "OK",
            "orientation": "lanskap",
            "gpu_backends": ["panfrost", "mali"],
            "gpu_mode": "deklarasi-manual",
        })
        data = parse_result(payload)
        self.assertEqual(data["orientation"], "lanskap")
        self.assertEqual(data["gpu_backends"], ["panfrost", "mali"])
        self.assertEqual(data["gpu_mode"], "deklarasi-manual")

    def test_page_exists(self) -> None:
        self.assertTrue((ROOT / "site" / "hardware" / "gpu.html").is_file())

    def test_page_declares_display_profile(self) -> None:
        page = (ROOT / "site" / "hardware" / "gpu.html").read_text(encoding="utf-8")
        for token in ("Profil tampilan Tom05", "lanskap", "panfrost", "mali"):
            self.assertIn(token, page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
