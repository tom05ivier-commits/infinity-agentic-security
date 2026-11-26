# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian peta koneksi supervisor <-> semua model opencode/tom05."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.model_connectivity import NAMED, check, collect_models  # noqa: E402


class ModelConnectivityTests(unittest.TestCase):
    def test_named_models_are_mapped(self) -> None:
        models = collect_models()
        for model_id in NAMED:
            self.assertIn(model_id, models)

    def test_glm_alias_not_invented(self) -> None:
        models = collect_models()
        self.assertIn("opencode/glm-5.3-flash", models)
        self.assertNotIn("opencode/glm-5.3-flash-free", models)

    def test_all_catalog_models_collected(self) -> None:
        self.assertGreaterEqual(len(collect_models()), 94)

    def test_report_shape(self) -> None:
        data = check()
        self.assertIn(data["status"], ("TERHUBUNG", "SEBAGIAN"))
        self.assertEqual(len(data["dinamai"]), 5)
        self.assertIn("supervisor", data)
        self.assertIn("endpoint", data)
        for item in data["dinamai"]:
            self.assertIn("status", item)
            self.assertTrue(set(item["rincian"]).issubset(set(data["endpoint"])))
        self.assertIn("bukan model terlatih baru", data["catatan"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
