# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian katalog mandiri tom05, alias model, dan alias CLI hy4."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CATALOG = ROOT / "config" / "tom05-models.json"
CLI = ROOT / "tom05"


class Tom05ModelTests(unittest.TestCase):
    def test_catalog_is_self_contained(self) -> None:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(data["source"], "katalog model lokal tom05 (mandiri)")
        self.assertEqual(data["default"], "tom05-flash-free")
        self.assertEqual(len(data["models"]), 11)
        for item in data["models"]:
            self.assertTrue(item["id"].startswith("opencode/"))
            self.assertTrue(item["name"])
            self.assertIsInstance(item["variants"], list)

    def test_default_model_is_tom05_alias(self) -> None:
        out = subprocess.run(
            [str(CLI), "--version"], capture_output=True, text=True,
            timeout=30, cwd=str(ROOT),
        ).stdout
        self.assertIn("model opencode/hy4-flash-free", out)

    def test_alias_points_to_real_model(self) -> None:
        clone = json.loads(CATALOG.read_text(encoding="utf-8"))
        alias = next(a for a in clone["aliases"] if a["id"] == "tom05-flash-free")
        self.assertEqual(alias["name"], "Tom05 flash Free")
        self.assertEqual(alias["target"], "opencode/hy4-flash-free")
        self.assertTrue(alias["verified"])

    def test_cli_lists_alias(self) -> None:
        out = subprocess.run(
            [str(CLI), "--list-models"], capture_output=True, text=True,
            timeout=30, cwd=str(ROOT),
        ).stdout
        self.assertIn("tom05-flash-free", out)
        self.assertIn("Tom05 flash Free", out)
        self.assertIn("opencode/hy4-flash-free", out)

    def test_cli_resolves_alias_to_real_model(self) -> None:
        out = subprocess.run(
            [str(CLI), "--model", "tom05-flash-free", "--version"],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT),
        ).stdout
        self.assertIn("model opencode/hy4-flash-free", out)

    def test_cli_rejects_unknown_model(self) -> None:
        done = subprocess.run(
            [str(CLI), "--model", "opencode/tidak-ada", "--version"],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT),
        )
        self.assertEqual(done.returncode, 2)

    def test_hy4_alias_delegates_to_tom05(self) -> None:
        alias = ROOT / "hy4"
        self.assertTrue(alias.exists())
        out = subprocess.run(
            [str(alias), "--version"], capture_output=True, text=True,
            timeout=30, cwd=str(ROOT),
        ).stdout
        self.assertIn("tom05 CLI", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
