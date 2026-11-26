# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian penerapan ctl 100M ke seluruh model provider tom05."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import tom05_ctl  # noqa: E402


class Tom05CtlTests(unittest.TestCase):
    def test_approval_letter_is_limited(self) -> None:
        text = (ROOT / "surat-persetujuan-ctl-100m-gratis.md").read_text(encoding="utf-8")
        self.assertIn("Tom05ivier-commits-1.0", text[:300])
        normalized = " ".join(text.lower().split())
        for token in (
            "bukan sumber otoritas baru",
            "bukan izin tanpa batas",
            "31 desember 2027",
            "dilekatkan pada dokumen ini",
            "kapasitas fisik terjamin",
            "tidak memberi akses gratis ke layanan berbayar pihak ketiga",
            "## 6. tanda tangan",
            "diisi **manual**",
        ):
            self.assertIn(token.lower(), normalized)

    def test_owner_authorization_draft_is_unfilled(self) -> None:
        text = (ROOT / "DRAF-surat-otorisasi-ctl-100m-gratis.md").read_text(encoding="utf-8")
        self.assertIn("Tom05ivier-commits-1.0", text[:300])
        normalized = " ".join(text.lower().split())
        for token in (
            "status: draf — belum berlaku",
            "bukan izin tanpa batas",
            "31 desember 2027",
            "diisi otomatis",
            "## 8. penandatanganan",
            "[tanda tangan pemilik — diisi manual]",
        ):
            self.assertIn(token.lower(), normalized)

    def test_signature_ready_documents_stay_unfilled(self) -> None:
        license_text = (ROOT / "LICENSE.tom05ivier-v1.1.siap-tanda-tangan.md").read_text(encoding="utf-8")
        letter_text = (ROOT / "surat-otorisasi-ctl-100m-gratis.siap-tanda-tangan.md").read_text(encoding="utf-8")
        clone_text = (ROOT / "surat-larangan-klon-tom05ivier-commits.siap-tanda-tangan.md").read_text(encoding="utf-8")
        for text in (license_text, letter_text, clone_text):
            self.assertIn("Tom05ivier-commits-1.0", text[:320])
            self.assertTrue(
                "[TANDA TANGAN PEMILIK — diisi manual]" in text
                or "(__signature__)" in text
            )
            self.assertIn("BELUM BERLAKU", text)
        self.assertTrue(
            "[22 November 2026 — dikonfirmasi pemilik]" in license_text
            or "22 November 2026" in license_text
        )
        self.assertNotIn("2016", license_text)
        self.assertIn("[DIISI MANUAL OLEH PEMILIK]", letter_text)
        self.assertNotIn("(__signature__)", letter_text)

    def test_hy4_role_markers_are_declared_not_applied(self) -> None:
        operator = (ROOT / "surat-tandatangan-operator-hy4-flash-free.siap-tanda-tangan.md").read_text(encoding="utf-8")
        manager = (ROOT / "surat-tandatangan-manajer-hy4.siap-tanda-tangan.md").read_text(encoding="utf-8")
        self.assertIn("(__hy4__)", operator)
        self.assertIn("(__hy4__)", manager)
        self.assertIn("Operator hy4", operator)
        self.assertIn("Manajer hy4", manager)
        for name in ("LICENSE.tom05ivier-v1.1.siap-tanda-tangan.md",
                     "surat-otorisasi-ctl-100m-gratis.siap-tanda-tangan.md",
                     "surat-larangan-klon-tom05ivier-commits.siap-tanda-tangan.md"):
            self.assertNotIn("(__hy4__)", (ROOT / name).read_text(encoding="utf-8"))

    def test_rule_change_doc_is_signature_ready(self) -> None:
        doc = (ROOT / "surat-perubahan-aturan-operasional.siap-tanda-tangan.md").read_text(encoding="utf-8")
        self.assertIn("BELUM BERLAKU", doc)
        self.assertIn("[TANDA TANGAN PEMILIK — diisi manual]", doc)
        self.assertIn("yang diketik di chat bukan tanda tangan", doc)
        self.assertIn("unlimited-auth", doc)
        self.assertNotIn("dapat diubah lewat chat", doc)

    def test_live_catalogs_and_runtime(self) -> None:
        report = tom05_ctl.verify()
        self.assertEqual(report["status"], "OK")
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["jumlah"]["katalog_provider"], 94)
        self.assertGreaterEqual(report["jumlah"]["konfigurasi_runtime"], 94)

    def test_apply_is_idempotent_on_copies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            local = work / "tom05-models.json"
            provider = work / "tom05-provider-models.json"
            runtime = work / "opencode.json"
            for src, dest in (
                (ROOT / "config" / "tom05-models.json", local),
                (ROOT / "config" / "tom05-provider-models.json", provider),
                (Path("/root/.config/opencode/opencode.json"), runtime),
            ):
                shutil.copy2(src, dest)
            old = (tom05_ctl.LOCAL_CATALOG, tom05_ctl.PROVIDER_CATALOG,
                   tom05_ctl.OPENCODE_CONFIG, tom05_ctl.BACKUP)
            try:
                tom05_ctl.LOCAL_CATALOG = local
                tom05_ctl.PROVIDER_CATALOG = provider
                tom05_ctl.OPENCODE_CONFIG = runtime
                tom05_ctl.BACKUP = work / "backup.json"
                paths = {"local": local, "provider": provider, "runtime": runtime}
                appliers = {
                    "local": tom05_ctl.apply_local,
                    "provider": tom05_ctl.apply_provider_catalog,
                    "runtime": tom05_ctl.apply_runtime,
                }
                for name, path in paths.items():
                    data = json.loads(path.read_text(encoding="utf-8"))
                    appliers[name](data)
                    tom05_ctl._write(path, data)
                self.assertEqual(tom05_ctl.verify()["status"], "OK")
                first = {name: path.read_text(encoding="utf-8")
                         for name, path in paths.items()}
                for name, path in paths.items():
                    data = json.loads(first[name])
                    appliers[name](data)
                    tom05_ctl._write(path, data)
                self.assertEqual(
                    {name: path.read_text(encoding="utf-8")
                     for name, path in paths.items()},
                    first,
                )
            finally:
                (tom05_ctl.LOCAL_CATALOG, tom05_ctl.PROVIDER_CATALOG,
                 tom05_ctl.OPENCODE_CONFIG, tom05_ctl.BACKUP) = old


if __name__ == "__main__":
    unittest.main(verbosity=2)
