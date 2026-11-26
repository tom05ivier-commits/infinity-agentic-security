# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian bridge Copilot CLI → OpenCode."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "copilot-bridge" / "bridge.py"

spec = importlib.util.spec_from_file_location("copilot_bridge", BRIDGE)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


class BridgeTests(unittest.TestCase):
    def test_extract_text_from_opencode_events(self) -> None:
        sample = (
            '{"type":"step_start","part":{"type":"step-start"}}\n'
            '{"type":"text","part":{"type":"text","text":"Halo "}}\n'
            '{"type":"text","part":{"type":"text","text":"dunia"}}\n'
        )
        self.assertEqual(bridge._extract_text(sample), "Halo dunia")

    def test_prompt_includes_system_context(self) -> None:
        prompt = bridge._prompt_from([{"role": "user", "content": "Halo"}])
        self.assertIn("Tomi vier", prompt)
        self.assertIn("Tom05ivier-commits-1.0", prompt)
        self.assertIn("[user] Halo", prompt)

    def test_metrics_shape(self) -> None:
        report = bridge._metrics_report()
        for key in ("calls", "errors", "cache_hits", "avg_latency_seconds"):
            self.assertIn(key, report)

    def test_model_constant(self) -> None:
        self.assertEqual(bridge.MODEL, "opencode/hy4-flash-free")


if __name__ == "__main__":
    unittest.main(verbosity=2)
