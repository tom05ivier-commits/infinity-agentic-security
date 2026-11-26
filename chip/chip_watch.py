# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Watchdog ringan untuk akselerator AI tom05 (TAI-1).

Layanan `process` ini dijalankan supervisor. Tiap siklus ia menjalankan
verifikasi model, Icarus Verilog, dan scorecard chip, lalu menulis ringkasan
ke `system/reports/ai_chip_watch.json` secara atomik. Tidak membuka port,
tidak membaca kredensial, dan tidak melakukan aksi jaringan.
"""

from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
REPORT = ROOT / "system" / "reports" / "ai_chip_watch.json"
COMMANDS = (
    ("model", ("verify",)),
    ("iverilog", ("iverilog",)),
    ("score", ("score",)),
)
REPORTS = {
    "sintesis": ROOT / "chip" / "reports" / "chip_synthesis.json",
    "browser": ROOT / "chip" / "reports" / "browser_presets.json",
}


def _report_status(path: Path) -> str:
    """Baca status laporan yang dihasilkan jalur verifikasi lain."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "FAIL"
    return str(data.get("status", "FAIL"))


def _run(command: tuple[str, ...]) -> dict[str, Any]:
    done = subprocess.run(
        [sys.executable, str(ROOT / "chip" / "chip_cli.py"), *command],
        capture_output=True, text=True, timeout=180, cwd=str(ROOT),
    )
    try:
        data = json.loads(done.stdout)
    except ValueError:
        data = {}
    return {
        "returncode": done.returncode,
        "status": data.get("status"),
        "score": data.get("score"),
        "vectors": data.get("vectors"),
        "checks": data.get("checks"),
        "errors": data.get("errors"),
    }


def cycle(state: dict[str, Any]) -> dict[str, Any]:
    """Jalankan satu siklus verifikasi dan tulis laporan atomik."""
    results: dict[str, Any] = {}
    for key, command in COMMANDS:
        try:
            results[key] = _run(command)
        except (OSError, subprocess.SubprocessError) as exc:
            results[key] = {"returncode": -1, "status": "FAIL", "error": type(exc).__name__}

    bukti = {key: _report_status(path) for key, path in REPORTS.items()}
    ok = (
        results.get("model", {}).get("status") == "PASS"
        and results.get("iverilog", {}).get("status") == "PASS"
        and results.get("score", {}).get("score") == 100
        and all(value == "PASS" for value in bukti.values())
    )
    state["cycles"] = int(state.get("cycles", 0)) + 1
    report = {
        "license": LICENSE,
        "owner": OWNER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "ai-chip-watch",
        "cycles": state["cycles"],
        "status": "PASS" if ok else "FAIL",
        "results": results,
        "bukti": bukti,
        "fabrication": "NOT_READY",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    tmp = REPORT.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(REPORT)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Watchdog chip AI tom05")
    parser.add_argument("--interval", type=float, default=60.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)

    stop = False

    def handle(_signum: int, _frame: Any) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, handle)
    signal.signal(signal.SIGINT, handle)

    state: dict[str, Any] = {"cycles": 0}
    interval = max(5.0, args.interval)
    while not stop:
        report = cycle(state)
        if args.once:
            return 0 if report["status"] == "PASS" else 1
        # Tidur bertahap agar SIGTERM dapat menghentikan proses dengan cepat.
        deadline = time.monotonic() + interval
        while not stop and time.monotonic() < deadline:
            time.sleep(min(1.0, deadline - time.monotonic()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
