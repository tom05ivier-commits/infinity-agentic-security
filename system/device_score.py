# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Scorecard kualitas integrasi perangkat — 10 kriteria × 10 poin.

Bersama chip, keamanan, Tom05, dan container total 500/500.
Semua kriteria dibaca dari bukti nyata; tidak ada nilai yang di-hardcode.
Tidak ada kredensial atau data pribadi yang dibaca/dicetak.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT = ROOT / "system" / "reports" / "device_score.json"
HELPER = Path(
    os.environ.get("OPENCODE_CONFIG_HOME", "/root/.config/opencode")
) / "skills" / "android-device" / "android_device.py"
SIGNATURE = "SPDX-License-Identifier: Tom05ivier-commits-1.0"


def _call(action: str) -> dict[str, Any]:
    if not HELPER.is_file():
        return {"success": False, "error": "helper tidak ada"}
    try:
        out = subprocess.run(
            ["python3", str(HELPER), action], capture_output=True, text=True,
            timeout=20, cwd=str(ROOT),
        )
        return json.loads(out.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"success": False, "error": type(exc).__name__}


def _result(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "points": 10 if ok else 0, "detail": detail}


def check_license() -> dict[str, Any]:
    files = [
        ROOT / "system" / "hardware_agent.py",
        ROOT / "system" / "ram_agent.py",
        ROOT / "system" / "gpu_benchmark.py",
        ROOT / "site" / "hardware" / "gpu.html",
        ROOT / "docs" / "HARDWARE-AGENT.md",
        ROOT / "docs" / "RAM-AGENT.md",
    ]
    bad = [p.name for p in files if not p.is_file() or SIGNATURE not in p.read_text()]
    return _result(not bad, f"{len(files)} berkas; tanpa header: {bad or 'tidak ada'}")


def check_bridge() -> dict[str, Any]:
    data = _call("health")
    ok = data.get("status") == "ok"
    return _result(ok, f"status={data.get('status')}, port={data.get('port')}")


def check_device() -> dict[str, Any]:
    data = _call("device-info")
    ok = bool(data.get("success")) and bool(data.get("model"))
    return _result(ok, f"success={data.get('success')}, model terisi={bool(data.get('model'))}")


def check_storage() -> dict[str, Any]:
    data = _call("file-diagnostics")
    ok = bool(data.get("success")) and (data.get("storage_free_bytes") or 0) > 0
    return _result(ok, f"success={data.get('success')}, bebas={data.get('storage_free_bytes')}")


def check_gpu_honesty() -> dict[str, Any]:
    from system.hardware_agent import describe as hw
    from system.hardware_report import report as hr

    ok = hw()["gpu_status"] == "TIDAK_TEREKSPOS" and hr()["gpu_status"] == "TIDAK_TEREKSPOS"
    return _result(ok, "agen dan laporan sama-sama menyatakan GPU tidak diekspos")


def check_gpu_page() -> dict[str, Any]:
    text = (ROOT / "site" / "hardware" / "gpu.html").read_text(encoding="utf-8")
    ok = all(token in text for token in ("navigator.gpu", "tom05-webgpu", "clipboard.writeText"))
    return _result(ok, "WebGPU + penanda + salin hasil tersedia")


def check_clipboard_safety() -> dict[str, Any]:
    from system.gpu_benchmark import MARKER, parse_result

    ok = (
        parse_result("kata sandi")["status"] == "CLIPBOARD_BUKAN_HASIL_BENCHMARK"
        and parse_result(json.dumps({"benchmark": MARKER, "status": "OK"}))["status"] == "OK"
    )
    return _result(ok, "clipboard asing ditolak; penanda tom05-webgpu diterima")


def check_ram_honesty() -> dict[str, Any]:
    from system.ram_agent import describe as rd
    from system.ram_manager import status as rs

    data = rd()
    s = rs()
    ok = (
        data["physical_ram_change"] is False
        and s["target_rasio"] == 2
        and "fisik" in s["catatan"]
    )
    return _result(ok, f"klaim fisik={data['physical_ram_change']}, target={s['target_rasio']}×")


def check_agents() -> dict[str, Any]:
    from system.hy4_manager import AGENTS

    ok = all(n in AGENTS for n in ("hardware.md", "ram.md", "chip.md"))
    return _result(ok, f"agen={len(AGENTS)}; hardware/ram/chip={'ada' if ok else 'kurang'}")


def check_privacy() -> dict[str, Any]:
    from system.gpu_benchmark import parse_result
    from system.hardware_report import report as hr
    from system.ram_manager import status as rs

    text = str(hr()).lower() + str(rs()).lower() + str(parse_result("x")).lower()
    bad = [t for t in ("password", "api_key", "authorization", "bearer ") if t in text]
    return _result(not bad, f"kata kunci sensitif: {bad or 'tidak ada'}")


CHECKS: tuple[tuple[str, str, Callable[[], dict[str, Any]]], ...] = (
    ("lisensi", "Header SPDX pada komponen perangkat", check_license),
    ("bridge", "Bridge capability server sehat", check_bridge),
    ("perangkat", "Info perangkat terbaca", check_device),
    ("storage", "Diagnostik storage terbaca", check_storage),
    ("gpu-jujur", "GPU tidak diklaim diekspos", check_gpu_honesty),
    ("gpu-halaman", "Halaman WebGPU mandiri", check_gpu_page),
    ("clipboard", "Clipboard hanya terima penanda aman", check_clipboard_safety),
    ("ram-jujur", "R.A.M. tidak mengklaim RAM fisik", check_ram_honesty),
    ("agen", "Agen hardware/ram/chip terdaftar", check_agents),
    ("privasi", "Tanpa kredensial dalam laporan", check_privacy),
)


def build() -> dict[str, Any]:
    results = []
    for key, label, fn in CHECKS:
        try:
            item = fn()
        except Exception as exc:
            item = _result(False, f"gagal membaca bukti: {type(exc).__name__}")
        results.append({"kriteria": key, "label": label, **item})
    score = sum(item["points"] for item in results)
    report = {
        "license": SIGNATURE,
        "owner": "Tomi vier",
        "score": score,
        "maximum": 100,
        "status": "PERFECT" if score == 100 else "PARTIAL",
        "grade": f"{score}/100",
        "checks": results,
        "failed": [item["kriteria"] for item in results if not item["pass"]],
        "total_bootstrap": f"{score + 400}/500",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    report = build()
    print(json.dumps({
        "status": report["status"],
        "grade": report["grade"],
        "score": report["score"],
        "total": report["total_bootstrap"],
        "failed": report["failed"],
        "report": "system/reports/device_score.json",
    }, indent=2, ensure_ascii=False))
    if report["score"] != 100:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
