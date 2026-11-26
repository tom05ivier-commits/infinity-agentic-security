# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian status peresmian lisensi (read-only)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.license_formalization import status  # noqa: E402


class LicenseFormalizationTests(unittest.TestCase):
    def test_waiting_for_signature(self) -> None:
        report = status()
        self.assertIn(
            report["status"],
            ("MENUNGGU_TANDA_TANGAN", "PERLU_PERBAIKAN",
             "PERLU_VERIFIKASI_MANUAL"),
        )
        self.assertEqual(report["akses"], "read-only")
        if report["status"] == "MENUNGGU_TANDA_TANGAN":
            self.assertTrue(
                all(report["checks"].values())
                or (
                    report["checks"]["tanda_tangan_bersih"]
                    and report["checks"]["surat_larangan_bersih"]
                )
            )
        elif report["status"] == "PERLU_VERIFIKASI_MANUAL":
            self.assertNotIn("Versi 1.0", (ROOT / "LICENSE").read_text())
        else:
            # PERLU_PERBAIKAN terjadi bila salah satu isian tanda tangan masih
            # memuat artefak otomatis. Surat larangan klon sudah ditandatangani
            # pemilik, jadi yang wajib bersih adalah draf amandemen; tidak boleh
            # memaksa surat yang sah menjadi "tidak bersih" agar tes lulus.
            self.assertFalse(all(report["checks"].values()))
            self.assertFalse(
                report["checks"]["tanda_tangan_bersih"]
                and report["checks"]["surat_larangan_bersih"]
            )

    def test_active_license_unchanged(self) -> None:
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue("Versi 1.1" in text or "Versi 1.0" in text)

    def test_drafts_exist_and_marked(self) -> None:
        for name in ("LICENSE.tom05ivier-v1.1.draf",
                     "DRAF-surat-larangan-klon-tom05ivier-commits.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("BELUM BERLAKU", text)

    def test_no_credentials_in_report(self) -> None:
        text = str(status()).lower()
        for token in ("password", "api_key", "authorization", "bearer "):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
