# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian katalog model terpisah dan provider tom05 yang melayani semuanya."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CATALOG = ROOT / "config" / "tom05-provider-models.json"
LETTER = ROOT / "surat-persetujuan-tom05-model.md"
TEST_PORT = "8791"


class Tom05ProviderModelTests(unittest.TestCase):
    def test_catalog_separated_and_attributed(self) -> None:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(data["license"], "Tom05ivier-commits-1.0")
        self.assertEqual(data["total"], len(data["models"]))
        self.assertGreaterEqual(data["total"], 90)
        for item in data["models"]:
            self.assertTrue(item["id"])
            self.assertTrue(item["proxied"])
            self.assertEqual(item["source"], "opencode")
            self.assertTrue(item["owned_by"])
            self.assertEqual(item["ctl"], 100_000_000)
            self.assertTrue(item["declared_only"])
        self.assertIn("bukan model baru", data["note"].lower())

    def test_entries_and_routing(self) -> None:
        from system.tom05_provider import (
            MODEL_ID, PROXIED, model_entries, resolve_upstream,
        )

        entries = model_entries()
        external = [m for m in PROXIED if not str(m.get("id", "")).startswith("tom05/")]
        self.assertEqual(len(entries), len(external) + 1)
        alias = entries[0]
        self.assertEqual(alias["id"], MODEL_ID)
        self.assertEqual(alias["owned_by"], "tom05")
        self.assertEqual(alias["context_length"], 100_000_000)
        self.assertTrue(alias["declared_only"])
        ids = [entry["id"] for entry in entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse(any(i.startswith("tom05/") for i in ids[1:]))
        self.assertTrue(all(entry.get("proxied") for entry in entries[1:]))
        # Semua model yang dilayani provider menyatakan ctl 100M.
        self.assertTrue(all(e.get("context_length") == 100_000_000 for e in entries))
        self.assertTrue(all(e.get("declared_only") for e in entries))

        self.assertEqual(resolve_upstream("tom05-flash-free"), "hy4-flash-free")
        self.assertEqual(resolve_upstream("tom05/tom05-flash-free"), "hy4-flash-free")
        self.assertEqual(resolve_upstream("tom05/foo"), "foo")
        self.assertEqual(resolve_upstream("opencode-go/hy3"), "opencode-go/hy3")

    def test_http_endpoint_serves_all_models(self) -> None:
        env = dict(os.environ, TOM05_PROVIDER_PORT=TEST_PORT)
        proc = subprocess.Popen(
            [sys.executable, str(ROOT / "system" / "tom05_provider.py")],
            cwd=str(ROOT), env=env, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            payload: dict = {}
            for _ in range(40):
                try:
                    with urllib.request.urlopen(
                        f"http://127.0.0.1:{TEST_PORT}/health", timeout=2
                    ) as response:
                        payload = json.loads(response.read())
                    break
                except Exception:  # noqa: BLE001
                    time.sleep(0.15)
            self.assertEqual(payload.get("status"), "ok")
            self.assertGreaterEqual(payload.get("proxied_models", 0), 90)

            with urllib.request.urlopen(
                f"http://127.0.0.1:{TEST_PORT}/v1/models", timeout=5
            ) as response:
                models = json.loads(response.read())
            ids = [item["id"] for item in models["data"]]
            self.assertEqual(models["total"], len(ids))
            self.assertGreaterEqual(len(ids), 90)
            self.assertIn("tom05-flash-free", ids)
            self.assertIn("opencode-go/hy3", ids)
            alias = next(m for m in models["data"] if m["id"] == "tom05-flash-free")
            self.assertEqual(alias["context_length"], 100_000_000)
            self.assertTrue(alias["declared_only"])
            self.assertTrue(all(
                m.get("context_length") == 100_000_000 for m in models["data"]
            ))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    def test_approval_letter_is_limited(self) -> None:
        text = LETTER.read_text(encoding="utf-8")
        self.assertIn("Tom05ivier-commits-1.0", text[:300])
        normalized = " ".join(text.lower().split())
        for token in (
            "bukan sumber otoritas baru",
            "bukan izin tanpa batas",
            "31 Desember 2027",
            "tidak menggantikan tanda tangan pemilik",
            "Model pihak ketiga",
            "## 6. tanda tangan",
            "diisi **manual**",
            "dilekatkan pada dokumen ini oleh agen",
        ):
            self.assertIn(token.lower(), normalized)


if __name__ == "__main__":
    unittest.main(verbosity=2)
