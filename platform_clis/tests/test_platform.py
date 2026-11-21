# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian scorecard CLI platform engineering."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from platform_clis.cli import context_markdown  # noqa: E402
from platform_clis.clis import CRITERIA, TOP10, inventory, score  # noqa: E402


class PlatformTests(unittest.TestCase):
    def test_top10_complete(self) -> None:
        self.assertEqual(len(TOP10), 10)
        self.assertEqual([i["rank"] for i in TOP10], list(range(1, 11)))
        self.assertEqual(len(CRITERIA), 8)

    def test_inventory_detects_local_tools(self) -> None:
        data = inventory()
        by_name = {item["name"]: item for item in data}
        self.assertTrue(by_name["OpenCode / Kilo CLI"]["installed"])
        self.assertTrue(by_name["Claude Code"]["installed"])
        self.assertTrue(by_name["kubectl"]["installed"])
        self.assertTrue(by_name["GitHub CLI"]["installed"])
        self.assertTrue(by_name["Terraform / OpenTofu"]["installed"])

    def test_score_bounded(self) -> None:
        for item in inventory():
            result = score(item)
            self.assertGreaterEqual(result["score"], 70)
            self.assertLessEqual(result["score"], 100)

    def test_context_for_hy4(self) -> None:
        text = context_markdown()
        for token in ("hy4-flash-free", "kubectl", "StackGen", "structured_output"):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
