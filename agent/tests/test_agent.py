# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian Agent Computer."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.brain import AgentBrain  # noqa: E402
from agent.runtime import STATE_PATH, AgentRuntime  # noqa: E402
from agent.tasks import TASKS  # noqa: E402


class AgentBrainTests(unittest.TestCase):
    def test_all_tasks_registered(self) -> None:
        self.assertEqual(
            set(TASKS),
            {
                "status",
                "verify",
                "protect",
                "integrity",
                "dashboard",
                "capability",
                "perfect",
                "campaign",
                "drill",
            },
        )

    def test_plan_protection_goal(self) -> None:
        steps = AgentBrain().plan("lindungi hardware dengan antivirus")
        names = [step.task for step in steps]
        self.assertEqual(names[0], "status")
        self.assertIn("protect", names)

    def test_plan_drill_requires_authorization(self) -> None:
        brain = AgentBrain()
        unauthorized = brain.plan("lakukan serangan malware", authorize=False)
        step = next(s for s in unauthorized if s.task == "drill")
        self.assertFalse(step.params["authorize"])
        authorized = brain.plan("lakukan serangan malware", authorize=True)
        step2 = next(s for s in authorized if s.task == "drill")
        self.assertTrue(step2.params["authorize"])

    def test_plan_perfect_goal(self) -> None:
        steps = AgentBrain().plan("sempurnakan sistem")
        names = [step.task for step in steps]
        self.assertEqual(names, ["status", "perfect"])
        self.assertEqual(len(set(names)), len(names))

    def test_plan_campaign_goal(self) -> None:
        steps = AgentBrain().plan("jalankan kampanye keamanan")
        names = [step.task for step in steps]
        self.assertIn("campaign", names)
        self.assertEqual(len(names), len(set(names)))

    def test_unknown_goal_falls_back_to_verify(self) -> None:
        steps = AgentBrain().plan("hal yang tidak dikenal")
        self.assertIn("verify", [step.task for step in steps])


class AgentRuntimeTests(unittest.TestCase):
    def test_run_records_trace(self) -> None:
        result = AgentRuntime().run("status sistem")
        self.assertEqual(result["status"], "SUCCESS")
        self.assertGreaterEqual(len(result["trace"]), 2)
        self.assertTrue(STATE_PATH.exists())
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["runs"]), 1)

    def test_drill_skipped_without_authorization(self) -> None:
        result = AgentRuntime().run("serang lab dengan malware", authorize=False)
        self.assertEqual(result["status"], "PARTIAL")
        drill = next(t for t in result["trace"] if t["task"] == "drill")
        self.assertTrue(drill["result"]["skipped"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
