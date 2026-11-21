# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Kompilasi, lint, dan eksekusi testbench RTL dengan Icarus Verilog.

Alur lengkap: iverilog -tnull (lint) → iverilog -o (compilasi) → vvp
(simulasi + VCD). Laporan ditulis ke chip/reports/iverilog.json.
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

from chip.reference import MODULES  # noqa: E402

REPORT = ROOT / "reports" / "iverilog.json"
VCD = ROOT / "reports" / "tb_chip.vcd"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
PASS_MARKER = "PASS: semua vektor benar."
EXPECTED_VECTORS: dict[str, int] = {
    "full_adder": 8,
    "mux2": 8,
    "decoder2": 4,
    "parity4": 16,
    "alu4": 1024,
    "hy4_dot4": 256,
    "hy4_top": 256,
    "hy4_quant": 16,
}
VECTOR_RE = re.compile(r"^VECTOR\s+(\S+)\s+(\d+)\s+(\d+)$", re.MULTILINE)
TOTAL_RE = re.compile(r"^TOTAL\s+(\d+)\s+(\d+)$", re.MULTILINE)


def _compiler() -> str:
    try:
        out = subprocess.run(
            ["iverilog", "-V"], capture_output=True, text=True, timeout=30
        )
        first = next((ln.strip() for ln in out.stdout.splitlines() if ln.strip()), "")
        return first or "Icarus Verilog"
    except (OSError, subprocess.SubprocessError):
        return "Icarus Verilog"


def _warning_count(stderr: str) -> int:
    return sum(1 for line in stderr.splitlines() if "warning" in line.lower())


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(PARENT))
    except ValueError:
        return str(path)


def run(write: bool = True) -> dict[str, Any]:
    """Lint, kompilasi, dan jalankan testbench.

    STATUS SKIP bila iverilog/vvp tidak tersedia; STATUS FAIL bila ada
    warning, error simulasi, modul hilang, atau ketidaksesuaian vektor.
    """
    started = time.monotonic()
    rtl = sorted((ROOT / "rtl").glob("*.v"))
    tb = ROOT / "tb" / "tb_chip.v"
    result: dict[str, Any] = {
        "license": LICENSE,
        "owner": OWNER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "compiler": _compiler() if shutil.which("iverilog") else "tidak tersedia",
        "command": "iverilog -g2012 -Wall -tnull ... && iverilog -g2012 -Wall -o tb_chip ... && vvp +vcd=... tb_chip",
        "rtl_files": [_relative(p) for p in rtl],
        "testbench": _relative(tb),
        "lint_warnings": 0,
        "lint_stderr": "",
        "compile_warnings": 0,
        "compile_stderr": "",
        "simulation_output": "",
        "modules": [],
        "vectors": 0,
        "checks": 0,
        "errors": 0,
        "vcd": None,
        "duration_ms": 0,
        "reasons": [],
        "status": "SKIP",
    }

    if not shutil.which("iverilog") or not shutil.which("vvp"):
        result["reasons"].append("iverilog/vvp tidak ditemukan di PATH")
        result["compile_stderr"] = result["reasons"][0]
        if write:
            _write(result)
        return result

    reasons: list[str] = result["reasons"]
    sources = [str(p) for p in rtl] + [str(tb)]
    tmp_root = Path("/tmp/opencode")
    kwargs: dict[str, Any] = {"prefix": "hy4-iverilog-"}
    if tmp_root.is_dir():
        kwargs["dir"] = tmp_root
    tmp = Path(tempfile.mkdtemp(**kwargs))

    try:
        # 1. Lint: deteksi warning tanpa menghasilkan binary.
        lint = subprocess.run(
            ["iverilog", "-g2012", "-Wall", "-tnull", "-s", "tb_chip", *sources],
            capture_output=True, text=True, timeout=120,
        )
        result["lint_stderr"] = lint.stderr.strip()
        result["lint_warnings"] = _warning_count(lint.stderr)
        if lint.returncode != 0:
            reasons.append("lint gagal")

        # 2. Kompilasi ke vvp.
        out = tmp / "tb_chip.vvp"
        compiled = subprocess.run(
            ["iverilog", "-g2012", "-Wall", "-o", str(out), "-s", "tb_chip", *sources],
            capture_output=True, text=True, timeout=120,
        )
        result["compile_stderr"] = compiled.stderr.strip()
        result["compile_warnings"] = _warning_count(compiled.stderr)
        if compiled.returncode != 0:
            reasons.append("kompilasi gagal")

        # 3. Simulasi + waveform VCD.
        if compiled.returncode == 0:
            if VCD.exists():
                VCD.unlink()
            simulated = subprocess.run(
                ["vvp", str(out), "+vcd=" + str(VCD)],
                capture_output=True, text=True, timeout=120,
            )
            output = (simulated.stdout + simulated.stderr).strip()
            result["simulation_output"] = output
            if simulated.returncode != 0:
                reasons.append("vvp keluar dengan kode nonzero")
            if PASS_MARKER not in output:
                reasons.append("penanda PASS tidak ditemukan")
            if "FAIL:" in output:
                reasons.append("testbench melaporkan FAIL")

            parsed: dict[str, dict[str, int]] = {}
            for name, vectors, errors in VECTOR_RE.findall(output):
                parsed[name] = {"vectors": int(vectors), "errors": int(errors)}
            result["modules"] = [
                {
                    "name": name,
                    "vectors": parsed.get(name, {}).get("vectors", 0),
                    "errors": parsed.get(name, {}).get("errors", -1),
                    "expected_vectors": EXPECTED_VECTORS.get(name, 0),
                    "status": "PASS" if parsed.get(name, {}).get("errors") == 0
                    and parsed.get(name, {}).get("vectors")
                    == EXPECTED_VECTORS.get(name) else "FAIL",
                }
                for name in sorted(MODULES)
            ]
            total = TOTAL_RE.search(output)
            if total:
                result["checks"] = int(total.group(1))
                result["errors"] = int(total.group(2))
            else:
                reasons.append("ringkasan TOTAL tidak ditemukan")
            result["vectors"] = sum(m["vectors"] for m in result["modules"])
            for module in result["modules"]:
                if module["status"] == "FAIL":
                    reasons.append(f"modul {module['name']} tidak lolos")
            if result["checks"] < sum(EXPECTED_VECTORS.values()):
                reasons.append("jumlah pengecekan lebih kecil dari expected")
            if VCD.is_file():
                result["vcd"] = {
                    "path": _relative(VCD),
                    "bytes": VCD.stat().st_size,
                }
            else:
                reasons.append("VCD tidak dihasilkan")
        else:
            result["simulation_output"] = compiled.stderr.strip()

        if result["lint_warnings"]:
            reasons.append(f"{result['lint_warnings']} warning lint")
        if result["compile_warnings"]:
            reasons.append(f"{result['compile_warnings']} warning kompilasi")
        result["status"] = "FAIL" if reasons else "PASS"
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        reasons.append(f"error toolchain: {type(exc).__name__}")
        result["status"] = "FAIL"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        result["duration_ms"] = int((time.monotonic() - started) * 1000)

    if write:
        _write(result)
    return result


def _write(result: dict[str, Any]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    payload = run()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    sys.exit(0 if payload["status"] in ("PASS", "SKIP") else 1)
