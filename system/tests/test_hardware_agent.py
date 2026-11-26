# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian agen Hardware CLI dan laporan perangkat."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.hardware_agent import AGENT_MARKDOWN, describe  # noqa: E402
from system.hardware_report import report  # noqa: E402
from system.hy4_manager import AGENTS  # noqa: E402


class HardwareAgentTests(unittest.TestCase):
    def test_agent_registered(self) -> None:
        self.assertIn("hardware.md", AGENTS)
        self.assertEqual(AGENTS["hardware.md"], AGENT_MARKDOWN)

    def test_gpu_not_claimed(self) -> None:
        info = describe()
        self.assertEqual(info["gpu_status"], "TIDAK_TEREKSPOS")
        self.assertIn("clipboard", str(info["gpu_method"]).lower())

    def test_report_shape(self) -> None:
        data = report()
        self.assertIn(data["status"], ("TERHUBUNG", "PERANGKAT_TIDAK_TERHUBUNG"))
        self.assertEqual(data["gpu_status"], "TIDAK_TEREKSPOS")
        self.assertIn("device", data)
        self.assertIn("storage_free_bytes", data)

    def test_cli_flag(self) -> None:
        out = subprocess.run(
            [str(ROOT / "tom05"), "--hardware"], capture_output=True, text=True,
            timeout=60, cwd=str(ROOT),
        ).stdout
        data = json.loads(out)
        self.assertEqual(data["agent"], "hardware")
        self.assertEqual(data["gpu_status"], "TIDAK_TEREKSPOS")

    def test_no_credentials_in_report(self) -> None:
        text = str(report()).lower()
        for token in ("password", "api_key", "authorization", "bearer "):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
