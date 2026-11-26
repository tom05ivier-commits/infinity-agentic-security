# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengujian chip simulasi NEURO-25 dan agen khususnya."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip import neuro25_reference as ref  # noqa: E402
from chip.neuro25_agent import (  # noqa: E402
    AGENT_FILE, AGENT_MARKDOWN, AGENT_MODEL, describe,
)


class Neuro25Tests(unittest.TestCase):
    def test_rtl_present_with_license(self) -> None:
        path = ROOT / "chip" / "rtl" / "tom05_neuro25.v"
        self.assertTrue(path.exists())
        head = path.read_text(encoding="utf-8")[:800]
        self.assertIn("SPDX-License-Identifier: Tom05ivier-commits-1.0", head)
        self.assertIn("Copyright (c) 2026 Tomi vier", head)
        self.assertIn("module tom05_neuro25", path.read_text(encoding="utf-8"))

    def test_model_known_values(self) -> None:
        zero = ref.neuro25(0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(zero, {
            "decision": 0, "stage": 0, "act": 0,
            "blocked": 0, "irq": 0, "ready": 1,
        })
        denied = ref.neuro25(3, 3, 3, 3, 3, 3, 0)
        self.assertEqual(denied["decision"], 10)
        self.assertEqual(denied["stage"], 3)
        self.assertEqual(denied["act"], 0)
        self.assertEqual(denied["blocked"], 1)
        self.assertEqual(denied["irq"], 1)
        granted = ref.neuro25(3, 3, 3, 3, 3, 3, 1)
        self.assertEqual(granted["act"], 1)
        self.assertEqual(granted["blocked"], 0)
        self.assertEqual(granted["irq"], 0)
        early = ref.neuro25(3, 3, 3, 3, 3, 0, 1)
        self.assertEqual(early["act"], 0)

    def test_exhaustive_model_verification(self) -> None:
        report = ref.verify()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["vectors"], 8192)
        self.assertEqual(report["mismatches"], 0)
        self.assertFalse(report["subject_data"])
        self.assertEqual(report["profile"]["age_reference_years"], 25)

    def test_iverilog_evidence(self) -> None:
        path = ROOT / "chip" / "reports" / "neuro25_iverilog.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "PASS", data.get("reasons"))
        self.assertEqual(data["vectors"], 8192)
        self.assertEqual(data["checks"], 49152)
        self.assertEqual(data["errors"], 0)
        self.assertEqual(data["lint_warnings"], 0)
        self.assertEqual(data["compile_warnings"], 0)
        self.assertTrue((ROOT / data["vcd"]).exists())

    def test_synthesis_evidence(self) -> None:
        path = ROOT / "chip" / "reports" / "neuro25_synthesis.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "PASS")
        self.assertGreater(data["cells"], 0)
        for name in ("tom05_neuro25_gate.v", "tom05_neuro25_netlist.json",
                     "tom05_neuro25.stat"):
            self.assertTrue((ROOT / "chip" / "synth" / name).exists(), name)

    def test_final_report_and_safety_declaration(self) -> None:
        path = ROOT / "chip" / "reports" / "neuro25.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["cognitive_stages"],
                         ["indra", "memori", "perencanaan", "aksi"])
        self.assertEqual(data["fabrication"], "NOT_READY")
        self.assertEqual(data["clinical_validation"], "NOT_VALIDATED")
        self.assertFalse(data["medical_device"])
        self.assertFalse(data["safety"]["neural_interface"])
        self.assertFalse(data["safety"]["implantable"])
        self.assertFalse(data["safety"]["stimulation"])
        self.assertFalse(data["safety"]["subject_data"])
        self.assertFalse(data["safety"]["network_transmission"])
        self.assertTrue(data["safety"]["consent_gate"])

    def test_chip_cli_agent(self) -> None:
        done = subprocess.run(
            [sys.executable, str(ROOT / "chip" / "chip_cli.py"), "neuro25-agent"],
            capture_output=True, text=True, timeout=60, cwd=str(ROOT),
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["agent"], "neuro25")
        self.assertEqual(data["file"], AGENT_FILE)
        self.assertEqual(data["model"], AGENT_MODEL)
        self.assertFalse(data["medical_device"])
        self.assertIn("definition", data)

    def test_tom05_agent_flag(self) -> None:
        done = subprocess.run(
            [str(ROOT / "tom05"), "--neuro25-agent"],
            capture_output=True, text=True, timeout=60, cwd=str(ROOT),
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["agent"], "neuro25")
        self.assertEqual(data["source"], "chip/neuro25_agent.py")

    def test_agent_registered_in_supervisor(self) -> None:
        from system.hy4_manager import AGENTS

        self.assertEqual(AGENTS.get("neuro25.md"), AGENT_MARKDOWN)
        self.assertEqual(describe()["tom05_flag"], "tom05 --neuro25-agent")

    def test_agent_body_has_hard_boundaries(self) -> None:
        text = AGENT_MARKDOWN.lower()
        for phrase in ("bukan alat medis", "bukan bci", "not_ready",
                       "not_validated", "tidak membaca", "tidak terhubung",
                       "tidak memberikan stimulasi"):
            self.assertIn(phrase, text)

    def test_documentation_exists(self) -> None:
        path = ROOT / "docs" / "NEURO25-CHIP.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for token in ("NEURO-25", "tom05_neuro25", "NOT_READY",
                      "NOT_VALIDATED", "bukan alat medis", "consent"):
            self.assertIn(token, text.lower() if token.islower() else text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
