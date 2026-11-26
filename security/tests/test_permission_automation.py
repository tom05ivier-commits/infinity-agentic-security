# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengujian otomatisasi izin tertulis dan pemeriksa kedaluwarsanya."""

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

from security import permission_automation as pa  # noqa: E402


class PermissionAutomationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="agenty-izin-")
        self.folder = Path(self.tmp.name)
        self.patches = [
            mock.patch.object(pa, "ROOT", self.folder),
            mock.patch.object(pa, "LETTERS", self.folder / "letters"),
            mock.patch.object(pa, "INDEX", self.folder / "index.jsonl"),
            mock.patch.object(pa, "EXPIRY_REPORT", self.folder / "expiry.json"),
            mock.patch.object(pa, "META_LETTER", ROOT / "surat-persetujuan-otomatis.md"),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self) -> None:
        for patch in reversed(self.patches):
            patch.stop()
        self.tmp.cleanup()

    def test_issue_allowed_letter(self) -> None:
        result = pa.issue("verify", ttl=120, reason="uji rutin")
        self.assertEqual(result["status"], "OK")
        letter = self.folder / result["letter"]["letter"]
        self.assertTrue(letter.exists())
        text = letter.read_text(encoding="utf-8")
        self.assertIn("(__signature__)", text)
        self.assertIn("Bukan izin tanpa batas", text)
        self.assertIn("120 detik", text)
        self.assertEqual(len(pa.letters()), 1)

    def test_rejects_denied_unknown_and_long_ttl(self) -> None:
        for task in ("unlimited-auth", "external-network-action", "tidak-ada"):
            result = pa.issue(task)
            self.assertEqual(result["status"], "DITOLAK")
        self.assertEqual(pa.issue("verify", ttl=301)["status"], "DITOLAK")
        self.assertEqual(pa.letters(), [])

    def test_check_read_only_shape(self) -> None:
        report = pa.check()
        self.assertIn(report["status"], ("AMAN", "PERINGATAN"))
        self.assertEqual(report["valid_until"], "2027-12-31")
        self.assertLessEqual(report["max_ttl"] if "max_ttl" in report else 300, 300)
        self.assertIn("verify", report["allowed_categories"])
        self.assertIn("unlimited-auth", report["denied_categories"])
        self.assertNotIn("password", json.dumps(report, ensure_ascii=False).lower())

    def test_check_flags_draft_and_expiring(self) -> None:
        (self.folder / "DRAF-izin-contoh.md").write_text(
            "SPDX-License-Identifier: Tom05ivier-commits-1.0\nDRAF\n", encoding="utf-8"
        )
        (self.folder / "surat-izin-contoh.md").write_text(
            "SPDX-License-Identifier: Tom05ivier-commits-1.0\n"
            "Berlaku sampai 31 Desember 2027\n(__signature__)\n",
            encoding="utf-8",
        )
        report = pa.check()
        states = {item["file"]: item["status"] for item in report["static_letters"]}
        self.assertEqual(states["DRAF-izin-contoh.md"], "DRAF")
        self.assertIn(states["surat-izin-contoh.md"],
                      ("AKTIF", "SEGERA_KEDALUWARSA"))
        written = pa.write_report(report)
        self.assertTrue(written.exists())
        self.assertEqual(json.loads(written.read_text())["status"], report["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
