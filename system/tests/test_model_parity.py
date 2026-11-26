# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian kesetaraan tom05-flash-free dan hy4-flash-free."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.model_parity import (  # noqa: E402
    DEFAULT_DECLARED_MODEL,
    check,
    check_declared,
    check_declared_all,
)


class ModelParityTests(unittest.TestCase):
    def test_same_upstream(self) -> None:
        data = check()
        self.assertEqual(data["status"], "SAMA")
        self.assertEqual(data["upstream"], "opencode/hy4-flash-free")
        self.assertEqual(data["resolved"], "hy4-flash-free")

    def test_same_variants_and_free(self) -> None:
        data = check()
        self.assertEqual(data["variants"], ["none", "high"])
        self.assertTrue(data["gratis"])

    def test_no_fake_model_claim(self) -> None:
        self.assertIn("bukan model terlatih baru", check()["catatan"])

    def test_deepseek_declared_parity(self) -> None:
        data = check_declared(DEFAULT_DECLARED_MODEL)
        self.assertEqual(data["status"], "SAMA")
        self.assertEqual(data["nama"], "DeepSeek V4.1 Flash Free")
        self.assertEqual(data["variants"], ["low", "high", "max"])
        self.assertTrue(all(data["checks"].values()))
        self.assertIn("bukan model terlatih baru", data["catatan"])

    def test_all_declared_models(self) -> None:
        data = check_declared_all()
        self.assertEqual(data["status"], "SAMA")
        self.assertEqual(data["jumlah"], 11)

    def test_unknown_model(self) -> None:
        data = check_declared("opencode/model-tidak-ada")
        self.assertEqual(data["status"], "BEDA")
        self.assertEqual(data["alasan"], "TIDAK_DITEMUKAN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
