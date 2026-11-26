# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Layanan HTTP read-only untuk status akselerator AI tom05 (TAI-1).

Berjalan di localhost, tanpa kredensial, tanpa aksi ofensif, dan tanpa
menjalankan verifikasi berat saat permintaan masuk — laporan dibaca dari
artefak yang dihasilkan jalur verifikasi chip.
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
SERVICE = "ai-chip"

REPORTS = {
    "verification": ROOT / "chip" / "reports" / "chip_verification.json",
    "synthesis": ROOT / "chip" / "reports" / "chip_synthesis.json",
    "iverilog": ROOT / "chip" / "reports" / "iverilog.json",
    "browser": ROOT / "chip" / "reports" / "browser_presets.json",
    "score": ROOT / "chip" / "reports" / "chip_score.json",
    "watch": ROOT / "system" / "reports" / "ai_chip_watch.json",
}


def _load(path: Path) -> dict[str, Any]:
    """Baca laporan JSON; kembalikan dict kosong bila belum tersedia."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def status() -> dict[str, Any]:
    """Ringkasan status chip dari bukti nyata, tanpa nilai sensitif."""
    meta = _load(ROOT / "chip" / "hy4_chip.json")
    module = next(
        (m for m in meta.get("modules", []) if m.get("name") == "tom05_ai_accel"),
        {},
    )
    verification = _load(REPORTS["verification"])
    synthesis = _load(REPORTS["synthesis"])
    iverilog = _load(REPORTS["iverilog"])
    browser = _load(REPORTS["browser"])
    score = _load(REPORTS["score"])
    watch = _load(REPORTS["watch"])

    checks = {
        "model": verification.get("status") == "PASS",
        "sintesis": synthesis.get("status") == "PASS",
        "iverilog": iverilog.get("status") in ("PASS", "SKIP")
        and iverilog.get("errors", 1) == 0,
        "browser": browser.get("status") == "PASS",
        "score": score.get("score") == 100,
    }
    return {
        "service": SERVICE,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "module": {
            "name": module.get("name", "tom05_ai_accel"),
            "target": module.get("target"),
            "rtl": module.get("rtl"),
            "function": module.get("function"),
            "description": module.get("description"),
        },
        "fabrication": module.get("fabrication", "NOT_READY"),
        "checks": checks,
        "bukti": {
            "model": {
                "status": verification.get("status"),
                "modules": verification.get("modules"),
                "vectors": verification.get("vectors"),
            },
            "sintesis": {
                "status": synthesis.get("status"),
                "total_cells": synthesis.get("total_cells"),
            },
            "iverilog": {
                "status": iverilog.get("status"),
                "vectors": iverilog.get("vectors"),
                "checks": iverilog.get("checks"),
                "errors": iverilog.get("errors"),
            },
            "browser": {
                "status": browser.get("status"),
                "presets": len(browser.get("presets", [])),
            },
            "score": {
                "grade": score.get("grade"),
                "score": score.get("score"),
            },
            "watch": {
                "cycles": watch.get("cycles"),
                "last_status": watch.get("status"),
            },
        },
        "license": LICENSE,
        "owner": OWNER,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "Tom05AiChip/1.0"

    def _send(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/health":
            self._send(200, {
                "status": "ok",
                "service": SERVICE,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "license": LICENSE,
                "owner": OWNER,
                "fabrication": "NOT_READY",
            })
        elif path == "/capabilities":
            self._send(200, {
                "service": SERVICE,
                "module": "tom05_ai_accel",
                "cli": [
                    "python3 chip/chip_cli.py ai-chip",
                    "python3 chip/chip_cli.py verify",
                    "python3 chip/chip_cli.py iverilog",
                    "python3 chip/chip_cli.py synth",
                    "python3 chip/chip_cli.py score",
                    "tom05 --ai-chip",
                ],
                "endpoints": ["/health", "/", "/status", "/module", "/capabilities"],
                "supervisor": ["ai-chip", "ai-chip-watch"],
                "fabrication": "NOT_READY",
                "license": LICENSE,
                "owner": OWNER,
            })
        elif path in ("/", "/status", "/module"):
            self._send(200, status())
        else:
            self._send(404, {"error": "tidak ditemukan", "path": path})

    def log_message(self, fmt: str, *args: Any) -> None:
        # Jangan menulis permintaan ke log publik; layanan ini read-only.
        return


def build_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Layanan status chip AI tom05")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8783)
    args = parser.parse_args(argv)

    server = build_server(args.host, args.port)

    def stop(_signum: int, _frame: Any) -> None:
        # Menjawab SIGTERM sebagai KeyboardInterrupt agar serve_forever
        # dihentikan dan server_close() tetap dijalankan.
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
