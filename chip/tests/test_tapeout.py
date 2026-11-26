# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian paket serah-terima chip."""

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

from chip.tapeout import build_tapeout as tapeout  # noqa: E402
from chip.tapeout.build_tapeout import build  # noqa: E402


class TapeoutTests(unittest.TestCase):
    def test_build_package(self) -> None:
        result = build()
        self.assertEqual(result["status"], "OK")
        self.assertGreaterEqual(result["files"], 30)
        archive = Path(result["archive"])
        self.assertTrue(archive.exists())

    def test_manifest_marks_not_ready(self) -> None:
        result = build()
        manifest = Path(result["package"]) / "MANIFEST.json"
        data = json.loads(manifest.read_text())
        self.assertEqual(data["fabrication_status"], "NOT_READY")
        self.assertEqual(data["license"], "Tom05ivier-commits-1.0")

    def test_hapus_pohon_retry_saat_sibuk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "package"
            target.mkdir()
            with mock.patch.object(
                tapeout.shutil, "rmtree",
                side_effect=[OSError("directory not empty"), None],
            ) as removed:
                tapeout._remove_tree(target)
        self.assertEqual(removed.call_count, 2)

    def test_tidak_menyisakan_staging(self) -> None:
        build()
        leftovers = list(tapeout.TAPEOUT.glob("package-*"))
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
