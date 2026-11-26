# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian pengalihan model otomatis yang terbatas & diaudit."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.model_fallback import (  # noqa: E402
    ALLOWED_SCOPES, CATALOG, MAX_ATTEMPTS, apply, candidates, choose, history, status,
)


class ModelFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _catalog(self) -> Path:
        path = self.dir / "catalog.json"
        path.write_text(json.dumps({"models": [
            {"id": "opencode/a-free", "status": "active"},
            {"id": "opencode/b-free", "status": "active"},
            {"id": "opencode/c-free", "status": "inactive"},
        ]}), encoding="utf-8")
        return path

    def test_candidates_hanya_aktif(self) -> None:
        pool = candidates(catalog=self._catalog())
        self.assertEqual(pool, ["opencode/a-free", "opencode/b-free"])
        self.assertEqual(candidates(exclude=("opencode/a-free",), catalog=self._catalog()),
                         ["opencode/b-free"])

    def test_choose_memilih_kandidat_pertama(self) -> None:
        audit = self.dir / "audit.jsonl"
        result = choose("opencode/lama", catalog=self._catalog(), audit=audit)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["selected"], "opencode/a-free")
        self.assertNotEqual(result["selected"], "opencode/lama")
        self.assertEqual(result["scope"], "model")
        self.assertTrue(audit.exists())
        self.assertEqual(len(history(audit=audit)), 1)

    def test_choose_menolak_scope_invalid(self) -> None:
        audit = self.dir / "audit.jsonl"
        result = choose("opencode/lama", scope="data-theft", catalog=self._catalog(), audit=audit)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertNotIn("selected", result)

    def test_choose_membatasi_percobaan(self) -> None:
        audit = self.dir / "audit.jsonl"
        result = choose("opencode/lama", attempts=MAX_ATTEMPTS,
                        catalog=self._catalog(), audit=audit)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertIn("Batas percobaan", result["reason"])

    def test_choose_gagal_tanpa_kandidat(self) -> None:
        empty = self.dir / "empty.json"
        empty.write_text('{"models": []}', encoding="utf-8")
        result = choose("opencode/lama", catalog=empty, audit=self.dir / "audit.jsonl")
        self.assertEqual(result["status"], "GAGAL")

    def test_riwayat_tidak_menyimpan_nilai_sensitif(self) -> None:
        audit = self.dir / "audit.jsonl"
        choose("opencode/lama", catalog=self._catalog(), audit=audit)
        text = audit.read_text(encoding="utf-8")
        for token in ("password", "token", "api_key", "secret"):
            self.assertNotIn(token, text.lower())

    def test_apply_dry_run_tidak_menulis(self) -> None:
        config = self.dir / "opencode.json"
        config.write_text('{"model": "opencode/lama"}', encoding="utf-8")
        result = apply("opencode/lama", config=config, catalog=self._catalog(),
                       audit=self.dir / "audit.jsonl", dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["applied"])
        self.assertEqual(json.loads(config.read_text())["model"], "opencode/lama")

    def test_apply_menulis_kandidat_dan_backup(self) -> None:
        config = self.dir / "opencode.json"
        config.write_text('{"model": "opencode/lama"}', encoding="utf-8")
        result = apply("opencode/lama", config=config, catalog=self._catalog(),
                       audit=self.dir / "audit.jsonl")
        self.assertTrue(result["applied"])
        self.assertEqual(json.loads(config.read_text())["model"], "opencode/a-free")
        self.assertTrue(Path(result["backup"]).exists())
        self.assertEqual(result["previous"], "opencode/lama")

    def test_status_ringkas(self) -> None:
        data = status(catalog=CATALOG, audit=self.dir / "audit.jsonl")
        self.assertEqual(data["maks_percobaan"], MAX_ATTEMPTS)
        self.assertEqual(data["scopes"], list(ALLOWED_SCOPES))
        self.assertGreater(data["model_aktif"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
