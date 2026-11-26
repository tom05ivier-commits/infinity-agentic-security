# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian katalog mandiri tom05, alias model, dan alias CLI hy4."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
import urllib.request
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
        self.assertEqual(data["default"], "tom05/tom05-flash-free")
        self.assertEqual(len(data["models"]), 11)
        for item in data["models"]:
            self.assertTrue(item["id"].startswith("opencode/"))
            self.assertTrue(item["name"])
            self.assertIsInstance(item["variants"], list)
            self.assertEqual(item["ctl"], 100_000_000)
            self.assertTrue(item["declared_only"])

    def test_default_model_is_tom05_alias(self) -> None:
        out = subprocess.run(
            [str(CLI), "--version"], capture_output=True, text=True,
            timeout=30, cwd=str(ROOT),
        ).stdout
        self.assertIn("model tom05/tom05-flash-free", out)

    def test_alias_points_to_real_model(self) -> None:
        clone = json.loads(CATALOG.read_text(encoding="utf-8"))
        alias = next(a for a in clone["aliases"] if a["id"] == "tom05-flash-free")
        self.assertEqual(alias["name"], "Tom05 flash Free")
        self.assertEqual(alias["target"], "tom05/tom05-flash-free")
        self.assertTrue(alias["verified"])

    def test_cli_lists_alias(self) -> None:
        out = subprocess.run(
            [str(CLI), "--list-models"], capture_output=True, text=True,
            timeout=30, cwd=str(ROOT),
        ).stdout
        self.assertIn("tom05-flash-free", out)
        self.assertIn("Tom05 flash Free", out)
        self.assertIn("tom05/tom05-flash-free", out)

    def test_cli_resolves_alias_to_real_model(self) -> None:
        out = subprocess.run(
            [str(CLI), "--model", "tom05-flash-free", "--version"],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT),
        ).stdout
        self.assertIn("model tom05/tom05-flash-free", out)

    def test_cli_rejects_unknown_model(self) -> None:
        done = subprocess.run(
            [str(CLI), "--model", "opencode/tidak-ada", "--version"],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT),
        )
        self.assertEqual(done.returncode, 2)

    def test_provider_model_registered(self) -> None:
        out = subprocess.run(
            ["opencode", "models"], capture_output=True, text=True,
            timeout=60, cwd=str(ROOT),
        ).stdout
        self.assertIn("tom05/tom05-flash-free", out)

    def test_declared_context_limit(self) -> None:
        cfg = json.loads(Path("/root/.config/opencode/opencode.json").read_text(encoding="utf-8"))
        limit = cfg["providers"]["tom05"]["models"]["tom05-flash-free"]["limit"]
        self.assertEqual(limit["context"], 100_000_000)
        self.assertEqual(limit["input"], 100_000_000)
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        alias = next(a for a in catalog["aliases"] if a["id"] == "tom05-flash-free")
        self.assertTrue(alias["declared_only"])
        self.assertEqual(alias["ctl"], 100_000_000)

    def test_all_provider_models_declare_ctl(self) -> None:
        cfg = json.loads(Path("/root/.config/opencode/opencode.json").read_text(encoding="utf-8"))
        models = cfg["providers"]["tom05"]["models"]
        self.assertGreaterEqual(len(models), 94)
        for model_id, entry in models.items():
            with self.subTest(model=model_id):
                self.assertEqual(entry["limit"]["context"], 100_000_000)
                self.assertEqual(entry["limit"]["input"], 100_000_000)

    def test_provider_health(self) -> None:
        with urllib.request.urlopen(
            "http://127.0.0.1:8772/health", timeout=5
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["model"], "tom05-flash-free")

    def test_cli_ctl_flag(self) -> None:
        out = subprocess.run(
            [str(CLI), "--ctl"], capture_output=True, text=True,
            timeout=30, cwd=str(ROOT),
        ).stdout.strip()
        self.assertEqual(out, "100000000")

    def test_provider_advertises_ctl(self) -> None:
        with urllib.request.urlopen(
            "http://127.0.0.1:8772/v1/models", timeout=5
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
        model = next(m for m in data["data"] if m["id"] == "tom05-flash-free")
        self.assertEqual(model["context_length"], 100_000_000)
        self.assertTrue(model["declared_only"])

    def test_hy4_alias_active(self) -> None:
        # hy4 diaktifkan kembali 26-11-2026; semula dinonaktifkan 22-11-2026.
        active = ROOT / "hy4"
        self.assertTrue(active.exists())
        self.assertFalse((ROOT / "hy4.nonaktif-20261122").exists())
        self.assertIn("alias ini menjaga kompatibilitas", active.read_text(encoding="utf-8"))
        publish = (ROOT / "prepare_github.sh").read_text(encoding="utf-8")
        self.assertNotIn("run_copilot.sh tom05 hy4 \\", publish)
        self.assertIn("Penonaktifan hy4 flash free", (ROOT / "docs" / "HY4-DEAKTIVASI.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
