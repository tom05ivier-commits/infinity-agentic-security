# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian RTL, model referensi, dan preset simulator chip."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip.reference import MODULES, verify_all, verify_module  # noqa: E402


class ChipTests(unittest.TestCase):
    def test_rtl_files_present_with_license(self) -> None:
        for name in MODULES:
            path = ROOT / "chip" / "rtl" / f"{name}.v"
            self.assertTrue(path.exists(), path)
            self.assertIn("Tom05ivier-commits-1.0", path.read_text()[:300])

    def test_all_modules_verify(self) -> None:
        for name in MODULES:
            result = verify_module(name)
            self.assertEqual(result["status"], "PASS", result["details"])

    def test_verify_all_report(self) -> None:
        report = verify_all()
        self.assertEqual(report["status"], "PASS")
        self.assertGreaterEqual(report["vectors"], 1000)
        path = ROOT / "chip" / "reports" / "chip_verification.json"
        self.assertTrue(path.exists())

    def test_simulator_presets_exposed(self) -> None:
        script = (ROOT / "site" / "chip" / "simulator.js").read_text()
        page = (ROOT / "site" / "chip" / "simulator.html").read_text()
        for name in MODULES:
            self.assertIn(f"{name}:", script)
            self.assertIn(f'value="{name}"', page)

    def test_synthesis_artifacts_present(self) -> None:
        report = ROOT / "chip" / "reports" / "chip_synthesis.json"
        self.assertTrue(report.exists())
        import json

        data = json.loads(report.read_text())
        self.assertEqual(data["status"], "PASS")
        self.assertGreaterEqual(data["total_cells"], 1)
        for name in MODULES:
            gate = ROOT / "chip" / "synth" / f"{name}_gate.v"
            netlist = ROOT / "chip" / "synth" / f"{name}_netlist.json"
            self.assertTrue(gate.exists(), gate)
            self.assertTrue(netlist.exists(), netlist)

    def test_testbench_present(self) -> None:
        tb = ROOT / "chip" / "tb" / "tb_chip.v"
        self.assertTrue(tb.exists())
        text = tb.read_text()
        for token in ("full_adder", "mux2", "decoder2", "parity4", "alu4",
                      "hy4_dot4", "hy4_quant", "hy4_top"):
            self.assertIn(token, text)
        for token in ("VECTOR", "TOTAL", "$value$plusargs", "$dumpfile", "$dumpvars"):
            self.assertIn(token, text)

    def test_iverilog_check(self) -> None:
        import json

        path = ROOT / "chip" / "reports" / "iverilog.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["lint_warnings"], 0)
        self.assertEqual(data["compile_warnings"], 0)
        self.assertEqual(data["vectors"], 1588)
        self.assertEqual(data["checks"], 1608)
        self.assertEqual(data["errors"], 0)
        self.assertEqual(len(data["modules"]), len(MODULES))
        self.assertTrue(all(m["status"] == "PASS" for m in data["modules"]))
        self.assertTrue((ROOT / data["vcd"]["path"]).exists())
        from chip.iverilog_check import run

        result = run(write=False)
        self.assertIn(result["status"], ("PASS", "SKIP"))
        if result["status"] == "PASS":
            self.assertEqual(result["lint_warnings"], 0)
            self.assertEqual(result["compile_warnings"], 0)
            self.assertEqual(result["vectors"], 1588)

    def test_iverilog_skip_without_toolchain(self) -> None:
        from unittest import mock

        from chip.iverilog_check import run

        with mock.patch("chip.iverilog_check.shutil.which", return_value=None):
            result = run(write=False)
        self.assertEqual(result["status"], "SKIP")
        self.assertTrue(result["reasons"])

    def test_iverilog_fail_on_toolchain_error(self) -> None:
        import subprocess
        from unittest import mock

        from chip.iverilog_check import run

        failed = subprocess.CompletedProcess(["iverilog"], 1, "", "error")
        with mock.patch("chip.iverilog_check.shutil.which", return_value="/usr/bin/x"), \
             mock.patch("chip.iverilog_check.subprocess.run", return_value=failed):
            result = run(write=False)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("lint gagal", result["reasons"])
        self.assertIn("kompilasi gagal", result["reasons"])

    def test_browser_preset_report(self) -> None:
        import json

        path = ROOT / "chip" / "reports" / "browser_presets.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(len(data["presets"]), 3)
        self.assertTrue(all(p["pass"] and p["mismatches"] == 0 for p in data["presets"]))
        self.assertEqual(data["scopedErrors"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
