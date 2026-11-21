# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian manajer model hy4."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.hy4_manager import AGENTS, CLI_REGISTRY, COMMANDS, MODEL  # noqa: E402


class Hy4ManagerTests(unittest.TestCase):
    def test_model_constant(self) -> None:
        self.assertEqual(MODEL, "opencode/hy4-flash-free")

    def test_agents_and_commands_registered(self) -> None:
        self.assertEqual(len(AGENTS), 10)
        self.assertEqual(len(COMMANDS), 10)
        for name in ("hy4.md", "security.md", "platform.md", "professor.md",
                     "doctor.md", "engineer.md", "auditor.md", "architect.md",
                     "analyst.md", "firewall.md"):
            self.assertIn(name, AGENTS)
        self.assertIn("verify.md", COMMANDS)
        self.assertIn("chip.md", COMMANDS)

    def test_cli_registry(self) -> None:
        for name in ("gh", "kubectl", "terraform", "tofu", "doctor"):
            self.assertIn(name, CLI_REGISTRY)
        self.assertEqual(CLI_REGISTRY["doctor"]["kind"], "npm")
        self.assertIn("doctor.md", COMMANDS)
        self.assertIn("cli-troubleshoot.md", COMMANDS)
        self.assertIn("audit.md", COMMANDS)
        self.assertIn("architecture.md", COMMANDS)
        self.assertIn("analyze.md", COMMANDS)
        self.assertIn("firewall-drill.md", COMMANDS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
