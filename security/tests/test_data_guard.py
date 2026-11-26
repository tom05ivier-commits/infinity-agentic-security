# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian Data Guard — preflight pemblokiran ekspor data ilegal."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.data_guard import AUDIT, check  # noqa: E402

CLEAN = "Halo, ini dokumen teknis kecil bersinggungan publik."
GHP = "Ganti ini: ghp_" + "A" * 36
PASSWORD_S = "password: ini-adalah-password-saya-12345"
EMAIL_S = "E-mail saya: example@site.com. Isi: diskusi umum."


class DataGuardTests(unittest.TestCase):
    def test_clean_is_ok(self) -> None:
        self.assertEqual(check(CLEAN)["status"], "OK")

    def test_block_on_github_token(self) -> None:
        out = check(GHP)
        self.assertEqual(out["status"], "BLOCK")
        self.assertIn("github_token", out["laporan"]["blocked_labels"])

    def test_block_on_password(self) -> None:
        out = check(PASSWORD_S)
        self.assertEqual(out["status"], "BLOCK")
        self.assertIn("katasandi", out["laporan"]["blocked_labels"])

    def test_warn_on_email(self) -> None:
        out = check(EMAIL_S)
        self.assertEqual(out["status"], "WARN")
        self.assertIn("email", out["laporan"]["warn_labels"])

    def test_audit_written_on_block(self) -> None:
        n_before = len(AUDIT.read_text().splitlines()) if AUDIT.exists() else 0
        check(GHP)
        n_after = len(AUDIT.read_text().splitlines())
        self.assertGreaterEqual(n_after, n_before + 1)

    def test_never_crashes(self) -> None:
        # check() selalu mengembalikan dict berisi kunci "status" (lihat tes lain).
        self.assertIn(check("")["status"], ["OK", "WARN", "BLOCK"])
        self.assertIn(
            check("ada tanda tangan (__signature__)")["status"],
            ["OK", "WARN", "BLOCK"],
        )


if __name__ == "__main__":
    unittest.main()
