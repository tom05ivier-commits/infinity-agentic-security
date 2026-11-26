# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Lint, kompilasi, dan simulasi Icarus untuk testbench firewall.

Terpisah dari ``chip/iverilog_check.py`` agar 9 modul utama (2612 vektor,
5704 check) tidak berubah. Laporan: chip/reports/firewall_iverilog.json.
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
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

REPORT = ROOT / "reports" / "firewall_iverilog.json"
VCD = ROOT / "reports" / "tb_firewall.vcd"
RTL = [ROOT / "rtl" / "firewall_match.v", ROOT / "rtl" / "firewall_decide.v"]
TB = ROOT / "tb" / "tb_firewall.v"
EXPECTED = {"firewall_match": 512, "firewall_decide": 16384}
VECTOR_RE = re.compile(r"^VECTOR\s+(\S+)\s+(\d+)\s+(\d+)$", re.MULTILINE)
TOTAL_RE = re.compile(r"^TOTAL\s+(\d+)\s+(\d+)$", re.MULTILINE)
PASS_MARKER = "PASS: semua vektor benar."
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"


def _warn(stderr: str) -> int:
    return sum(1 for ln in stderr.splitlines() if "warning" in ln.lower())


def run(write: bool = True) -> dict[str, Any]:
    started = time.monotonic()
    result: dict[str, Any] = {
        "license": LICENSE, "owner": OWNER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "compiler": "Icarus Verilog" if shutil.which("iverilog") else "tidak tersedia",
        "lint_warnings": 0, "compile_warnings": 0,
        "vectors": 0, "checks": 0, "errors": 0,
        "modules": [], "reasons": [], "status": "SKIP",
    }
    if not all(shutil.which(t) for t in ("iverilog", "vvp")):
        result["reasons"].append("toolchain tidak tersedia")
        return result

    try:
        lint = subprocess.run(
            ["iverilog", "-g2012", "-Wall", "-tnull", *map(str, RTL)],
            capture_output=True, text=True, timeout=60,
        )
        result["lint_warnings"] = _warn(lint.stderr)
        if lint.returncode != 0 or result["lint_warnings"]:
            result["reasons"].append("lint gagal")

        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as tmp:
            exe = Path(tmp) / "tb_firewall"
            comp = subprocess.run(
                ["iverilog", "-g2012", "-Wall", "-o", str(exe),
                 *map(str, RTL), str(TB)],
                capture_output=True, text=True, timeout=60,
            )
            result["compile_warnings"] = _warn(comp.stderr)
            if comp.returncode != 0 or result["compile_warnings"]:
                result["reasons"].append("kompilasi gagal")

            sim = subprocess.run(
                ["vvp", str(exe), f"+vcd={VCD}"],  # plusargs setelah executable
                capture_output=True, text=True, timeout=120,
            )
            if sim.returncode != 0:
                result["reasons"].append("simulasi gagal")
            vectors = {m: (int(n), int(e)) for m, n, e in
                       VECTOR_RE.findall(sim.stdout)}
            total = TOTAL_RE.search(sim.stdout)
            for name, expected in EXPECTED.items():
                n, errs = vectors.get(name, (0, 0))
                result["modules"].append({"name": name, "vectors": n,
                                          "errors": errs, "status": "PASS" if n == expected and errs == 0 else "FAIL"})
                if n != expected:
                    result["reasons"].append(f"{name}: {n} != {expected}")
            result["vectors"] = sum(n for n, _ in vectors.values())
            result["checks"] = result["vectors"]
            result["errors"] = int(total.group(2)) if total else sum(e for _, e in vectors.values())
            if PASS_MARKER not in sim.stdout:
                result["reasons"].append("penanda PASS tidak ditemukan")
    except (OSError, subprocess.SubprocessError) as exc:
        result["reasons"].append(f"{type(exc).__name__}: {exc}")

    result["status"] = "PASS" if not result["reasons"] and result["errors"] == 0 else (
        "SKIP" if not shutil.which("iverilog") else "FAIL"
    )
    result["duration_ms"] = int((time.monotonic() - started) * 1000)
    if write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main() -> int:
    r = run()
    print(json.dumps({
        "status": r["status"], "compiler": r["compiler"],
        "lint_warnings": r["lint_warnings"], "compile_warnings": r["compile_warnings"],
        "modules": len(r["modules"]), "vectors": r["vectors"],
        "checks": r["checks"], "errors": r["errors"],
        "reasons": r["reasons"], "report": "chip/reports/firewall_iverilog.json",
    }, indent=2, ensure_ascii=False))
    return 0 if r["status"] in ("PASS", "SKIP") else 1


if __name__ == "__main__":
    raise SystemExit(main())
