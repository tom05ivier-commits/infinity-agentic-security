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

from system.hy4_manager import (  # noqa: E402
    AGENTS, CLI_REGISTRY, COMMANDS, LEGACY_MODEL, MODEL,
)


class Hy4ManagerTests(unittest.TestCase):
    def test_model_constant(self) -> None:
        self.assertEqual(MODEL, "opencode/hy4-flash-free")
        self.assertEqual(LEGACY_MODEL, "opencode/glm-5.3-flash")

    def test_agents_and_commands_registered(self) -> None:
        self.assertEqual(len(AGENTS), 18)
        self.assertEqual(len(COMMANDS), 10)
        for name in ("security.md", "platform.md", "professor.md",
                     "doctor.md", "engineer.md", "auditor.md", "architect.md",
                     "analyst.md", "firewall.md", "asisten-manajer.md",
                     "chip.md", "neuro25.md", "hardware.md", "ram.md", "dataset.md",
                     "owner-ceo.md", "agent-manager.md", "hy4.md"):
            self.assertIn(name, AGENTS)
        self.assertIn("hy4.md", AGENTS)
        self.assertIn("model: opencode/tidepool-alpha-free", AGENTS["owner-ceo.md"])
        self.assertIn("bukan jabatan otorisasi", AGENTS["owner-ceo.md"])
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
