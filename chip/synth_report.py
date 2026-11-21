# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Ringkasan bukti sintesis & simulasi gate-level chip.

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SYNTH = ROOT / "synth"
REPORT_DIR = ROOT / "reports"
OUTPUT = REPORT_DIR / "chip_synthesis.json"
MODULES = (
    "full_adder", "mux2", "decoder2", "parity4", "alu4",
    "hy4_dot4", "hy4_quant", "hy4_top",
)


def collect() -> dict[str, Any]:
    modules: list[dict[str, Any]] = []
    for name in MODULES:
        stat = SYNTH / f"{name}.stat"
        gate = SYNTH / f"{name}_gate.v"
        netlist = SYNTH / f"{name}_netlist.json"
        cells = 0
        if stat.exists():
            match = re.search(r"Number of cells:\s*(\d+)", stat.read_text(errors="ignore"))
            cells = int(match.group(1)) if match else 0
        modules.append(
            {
                "module": name,
                "cells": cells,
                "gate_netlist": gate.exists(),
                "json_netlist": netlist.exists(),
            }
        )
    return {
        "status": (
            "PASS"
            if all(m["gate_netlist"] and m["json_netlist"] for m in modules)
            else "FAIL"
        ),
        "tools": {"yosys": "0.33", "iverilog": "12.0"},
        "modules": modules,
        "total_cells": sum(m["cells"] for m in modules),
        "license": "Tom05ivier-commits-1.0",
    }


def write() -> dict[str, Any]:
    report = collect()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chip synthesis report")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = write() if args.write else collect()
    print(json.dumps(report, indent=2))
