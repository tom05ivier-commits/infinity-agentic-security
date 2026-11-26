# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian sinkronisasi hy4 → Copilot CLI."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.copilot_sync import (  # noqa: E402
    _expected,
    agent_profile,
    skill_file,
    sync,
    verify,
)
from system.hy4_manager import AGENTS, COMMANDS  # noqa: E402


class CopilotSyncTests(unittest.TestCase):
    def test_agent_profile_conversion(self) -> None:
        text = agent_profile("professor.md", AGENTS["professor.md"])
        self.assertIn("name: professor", text)
        self.assertIn("description:", text)
        self.assertIn("model: opencode-hy4/hy4-flash-free", text)

    def test_skill_conversion(self) -> None:
        text = skill_file("verify.md", COMMANDS["verify.md"])
        self.assertIn("name: verify", text)
        self.assertIn("license: Tom05ivier-commits-1.0", text)
        self.assertIn("security_cli.py verify", text)

    def test_dry_run_counts(self) -> None:
        result = sync(dry_run=True)
        self.assertEqual(result["status"], "SIMULASI")
        self.assertEqual(result["agents"], len(AGENTS))
        self.assertEqual(result["commands"], len(COMMANDS))
        self.assertEqual(result["files"], 2 * (len(AGENTS) + len(COMMANDS)))

    def test_expected_files_follow_definitions(self) -> None:
        expected = _expected()
        self.assertEqual(len(expected), 2 * (len(AGENTS) + len(COMMANDS)))
        self.assertEqual(len(AGENTS), 17)
        self.assertEqual(len(COMMANDS), 10)
        self.assertIn("dataset.md", AGENTS)
        self.assertIn("neuro25.md", AGENTS)

    def test_verify_after_sync(self) -> None:
        sync()
        result = verify()
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["agents"], len(AGENTS))
        self.assertEqual(result["commands"], len(COMMANDS))
        self.assertEqual(result["expected_files"], result["present_files"])
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["content_mismatch"], [])
        self.assertEqual(result["stale"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
