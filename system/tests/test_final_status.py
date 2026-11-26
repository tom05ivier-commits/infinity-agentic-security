# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian agregat status final."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.final_status import final  # noqa: E402


class FinalStatusTests(unittest.TestCase):
    def test_final_state(self) -> None:
        data = final()
        self.assertEqual(data["status"], "SEMPURNA")
        self.assertEqual(data["skor_total"], "500/500")
        self.assertEqual(data["koneksi"], "TERHUBUNG")
        self.assertEqual(data["data_bersama"], "TERHUBUNG")
        self.assertEqual(data["konektivitas_infinity"], "TERHUBUNG")

    def test_all_five_scores_present(self) -> None:
        data = final()
        self.assertEqual(len(data["skor"]), 5)
        self.assertTrue(all(v["nilai"] == 100 for v in data["skor"].values()))

    def test_no_credentials(self) -> None:
        text = str(final()).lower()
        for token in ("password", "api_key", "authorization", "bearer "):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
