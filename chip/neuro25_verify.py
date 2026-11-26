# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Jalur verifikasi lengkap chip simulasi NEURO-25.

Tiga bukti: model referensi vs RTL, Icarus Verilog (lint + kompilasi + vvp
dengan waveform), dan sintesis Yosys. Semua berjalan lokal, tanpa jaringan,
tanpa kredensial, dan tanpa data subjek manusia. Status fabrikasi tetap
NOT_READY serta validasi klinis NOT_VALIDATED.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from chip.neuro25_reference import (  # noqa: E402
    MODULE, PROFILE_AGE_REFERENCE_YEARS, verify as verify_model,
)

REPORTS = ROOT / "reports"
SYNTH = ROOT / "synth"
RTL = ROOT / "rtl" / f"{MODULE}.v"
TB = ROOT / "tb" / "tb_neuro25.v"
GATE = SYNTH / f"{MODULE}_gate.v"
NETLIST = SYNTH / f"{MODULE}_netlist.json"
STAT = SYNTH / f"{MODULE}.stat"
VCD = REPORTS / f"tb_{MODULE}.vcd"
IVERILOG_REPORT = REPORTS / "neuro25_iverilog.json"
SYNTH_REPORT = REPORTS / "neuro25_synthesis.json"
REPORT = REPORTS / "neuro25.json"
PASS_MARKER = "PASS: semua vektor sintetis benar."
VECTOR_RE = re.compile(r"^VECTOR\s+(\S+)\s+(\d+)\s+(\d+)$", re.MULTILINE)
TOTAL_RE = re.compile(r"^TOTAL\s+(\d+)\s+(\d+)$", re.MULTILINE)


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def _warning_count(stderr: str) -> int:
    return sum(1 for line in stderr.splitlines() if "warning" in line.lower())


def run_iverilog(write: bool = True) -> dict[str, Any]:
    """Lint, kompilasi, dan jalankan testbench 8192 vektor."""
    started = time.monotonic()
    result: dict[str, Any] = {
        "module": MODULE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "compiler": "",
        "lint_warnings": 0,
        "compile_warnings": 0,
        "errors": 0,
        "vectors": 0,
        "checks": 0,
        "status": "SKIP",
        "reasons": [],
        "vcd": f"chip/reports/{VCD.name}",
        "duration_ms": 0,
    }
    if not shutil.which("iverilog") or not shutil.which("vvp"):
        result["reasons"].append("iverilog/vvp tidak tersedia di PATH")
        if write:
            _write(IVERILOG_REPORT, result)
        return result
    try:
        version = subprocess.run(["iverilog", "-V"], capture_output=True,
                                 text=True, timeout=30, cwd=str(ROOT))
        result["compiler"] = next(
            (line.strip() for line in version.stdout.splitlines() if line.strip()),
            "Icarus Verilog",
        )
    except (OSError, subprocess.SubprocessError):
        result["compiler"] = "Icarus Verilog"

    tmp_root = Path("/tmp/opencode")
    kwargs: dict[str, Any] = {"prefix": "neuro25-iverilog-"}
    if tmp_root.is_dir():
        kwargs["dir"] = str(tmp_root)
    tmp = Path(tempfile.mkdtemp(**kwargs))
    binary = tmp / "tb_neuro25"
    lint = compile_proc = sim = None
    try:
        sources = [str(RTL), str(TB)]
        lint = subprocess.run(["iverilog", "-g2012", "-Wall", "-tnull", *sources],
                              capture_output=True, text=True, timeout=120, cwd=str(ROOT))
        result["lint_warnings"] = _warning_count(lint.stderr)
        if result["lint_warnings"] or lint.returncode != 0:
            result["reasons"].append("lint gagal")
        compile_proc = subprocess.run(
            ["iverilog", "-g2012", "-Wall", "-o", str(binary), *sources],
            capture_output=True, text=True, timeout=120, cwd=str(ROOT),
        )
        result["compile_warnings"] = _warning_count(compile_proc.stderr)
        if result["compile_warnings"] or compile_proc.returncode != 0:
            result["reasons"].append("kompilasi gagal")
        if not result["reasons"]:
            # Plusarg harus dikirim SETELAH nama biner; bila sebelum, vvp
            # mengira `+vcd=...` sebagai berkas input dan gagal membukanya.
            # Path absolut dipakai karena $dumpfile tidak membuka direktori relatif
            # dengan stabil ketika vvp dijalankan dari workdir lain.
            sim = subprocess.run(
                [str(binary), f"+vcd={VCD}"],
                capture_output=True, text=True, timeout=180, cwd=str(ROOT),
            )
            output = sim.stdout
            vector = VECTOR_RE.search(output)
            total = TOTAL_RE.search(output)
            if vector:
                result["vectors"] = int(vector.group(2))
                if vector.group(1) != MODULE or int(vector.group(3)):
                    result["errors"] += int(vector.group(3))
                    result["reasons"].append("vektor melanggar model")
            else:
                result["reasons"].append("marker VECTOR tidak ditemukan")
            if total:
                result["checks"] = int(total.group(1))
                result["errors"] += int(total.group(2))
            else:
                result["reasons"].append("marker TOTAL tidak ditemukan")
            if PASS_MARKER not in output:
                result["reasons"].append("testbench tidak melaporkan PASS")
            result["simulation_output"] = output[-1200:]
    except (OSError, subprocess.SubprocessError) as exc:
        result["reasons"].append(f"toolchain gagal: {type(exc).__name__}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    result["duration_ms"] = int((time.monotonic() - started) * 1000)
    result["status"] = "PASS" if not result["reasons"] else "FAIL"
    if write:
        _write(IVERILOG_REPORT, result)
    return result


def run_synthesis(write: bool = True) -> dict[str, Any]:
    """Sintesis gate-level memakai Yosys (lokal, tanpa jaringan)."""
    result: dict[str, Any] = {
        "module": MODULE, "tool": "yosys", "status": "SKIP",
        "cells": 0, "gate_netlist": False, "json_netlist": False,
        "reasons": [],
    }
    if not shutil.which("yosys"):
        result["reasons"].append("yosys tidak tersedia di PATH")
        if write:
            _write(SYNTH_REPORT, result)
        return result
    SYNTH.mkdir(parents=True, exist_ok=True)
    script = (
        f"read_verilog {RTL}; hierarchy -check -top {MODULE}; proc; opt; "
        f"write_verilog -noattr {GATE}; stat; write_json {NETLIST}"
    )
    try:
        done = subprocess.run(["yosys", "-p", script], capture_output=True,
                              text=True, timeout=180, cwd=str(ROOT))
        STAT.write_text(done.stdout, encoding="utf-8")
        match = re.search(r"Number of cells:\s*(\d+)", done.stdout)
        result["cells"] = int(match.group(1)) if match else 0
        result["gate_netlist"] = GATE.exists()
        result["json_netlist"] = NETLIST.exists()
        if done.returncode != 0 or not result["cells"] or not (
            result["gate_netlist"] and result["json_netlist"]
        ):
            result["reasons"].append("sintesis tidak menghasilkan netlist lengkap")
    except (OSError, subprocess.SubprocessError) as exc:
        result["reasons"].append(f"yosys gagal: {type(exc).__name__}")
    result["status"] = "PASS" if not result["reasons"] else "FAIL"
    if write:
        _write(SYNTH_REPORT, result)
    return result


def build(write: bool = True) -> dict[str, Any]:
    """Jalankan ketiga bukti lalu tulis satu laporan deklaratif."""
    model = verify_model()
    sim = run_iverilog(write=write)
    synth = run_synthesis(write=write)
    ok = all(item["status"] == "PASS" for item in (model, sim, synth))
    report: dict[str, Any] = {
        "schema": "tom05-neuro25-chip/1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if ok else "FAIL",
        "name": "NEURO-25",
        "module": MODULE,
        "target": "cognitive-signal-simulation",
        "cognitive_stages": ["indra", "memori", "perencanaan", "aksi"],
        "profile": {
            "age_reference_years": PROFILE_AGE_REFERENCE_YEARS,
            "kind": "synthetic-adult-reference",
            "gain": 2,
            "note": (
                "Usia hanya penanda konfigurasi simulasi. Bukan data biologis, "
                "bukan pengukuran otak, dan tidak mewakili subjek sungguhan."
            ),
        },
        "evidence": {
            "model": {"status": model["status"], "vectors": model["vectors"],
                      "mismatches": model["mismatches"]},
            "iverilog": {"status": sim["status"], "vectors": sim["vectors"],
                         "checks": sim["checks"], "errors": sim["errors"],
                         "lint_warnings": sim["lint_warnings"],
                         "compile_warnings": sim["compile_warnings"]},
            "synthesis": {"status": synth["status"], "cells": synth["cells"]},
        },
        "safety": {
            "consent_gate": True,
            "action_blocked_without_gate": True,
            "neural_interface": False,
            "implantable": False,
            "stimulation": False,
            "subject_data": False,
            "network_transmission": False,
            "offline_verification": True,
        },
        "fabrication": "NOT_READY",
        "clinical_validation": "NOT_VALIDATED",
        "medical_device": False,
        "disclaimer": (
            "Desain RTL untuk simulasi dan pembelajaran. Bukan alat medis, "
            "bukan BCI, tidak terhubung ke otak manusia hidup, tidak membaca "
            "atau mengirim data neural, dan tidak memberikan stimulasi."
        ),
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }
    if write:
        _write(REPORT, report)
    return report


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, ensure_ascii=False))
