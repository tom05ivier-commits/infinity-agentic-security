# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Watchdog semua server OpenCode yang berjalan di luar registry.

Proses `opencode serve --port N` yang diluncurkan OpenChamber memakai port
ephemeral: port berubah setiap sesi, sehingga pendaftaran statis di
system/services.json cepat usang. Watchdog ini mendeteksi semua server
OpenCode yang sedang berjalan (kecuali instansi `serve --service` milik sesi
dan server web OpenChamber), memastikan portnya merespons, dan menjalankan
ulang bila mati.

Watchdog TIDAK mengubah system/services.json — penambahan layanan tetap lewat
`./run_system.sh service-add` sesuai aturan proyek dan batas izin konfigurasi
otomatis. Tidak ada kredensial yang dibaca atau ditulis.
"""

from __future__ import annotations

import json
import re
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "system" / "reports" / "opencode_watch.json"
REGISTRY = ROOT / "system" / "services.json"
WRAPPER = ROOT / "scripts" / "opencode_serve.sh"
DEFAULT_INTERVAL = 10.0

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_STOP = False


def _cmdline(pid: int) -> str:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return ""
    return raw.replace(b"\0", b" ").decode("utf-8", "ignore")


def discover() -> list[dict[str, Any]]:
    """Kembalikan server OpenCode aktif yang memakai `--port`, tanpa duplikat."""
    found: dict[int, dict[str, Any]] = {}
    try:
        pids = [int(item.name) for item in Path("/proc").iterdir() if item.name.isdigit()]
    except OSError:
        return []
    for pid in pids:
        line = _cmdline(pid)
        if not line or "--service" in line or "@openchamber/web" in line:
            continue
        if " serve" not in line:
            continue
        if "opencode.exe" not in line and "bin/opencode" not in line:
            continue
        match = re.search(r"--port\s+(\d+)", line)
        if not match:
            continue
        port = int(match.group(1))
        found.setdefault(port, {"pid": pid, "port": port})
    return [found[key] for key in sorted(found)]


def registered_ports() -> set[int]:
    """Port layanan HTTP yang sudah diawasi supervisor lewat registry."""
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {
        int(item["port"])
        for item in data.get("services", [])
        if item.get("kind") == "http" and str(item.get("port", "")).isdigit()
    }


def port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def http_alive(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
            return getattr(response, "status", 200) < 500
    except urllib.error.HTTPError as exc:
        return exc.code < 500
    except Exception:
        return False


def ensure(port: int) -> bool:
    """Jalankan ulang server bila port benar-benar kosong. True bila dimulai."""
    if port_open(port) or not WRAPPER.is_file():
        return False
    try:
        subprocess.Popen(
            ["bash", str(WRAPPER), str(port)],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        return False
    return True


def snapshot() -> dict[str, Any]:
    registered = registered_ports()
    rows: list[dict[str, Any]] = []
    for item in discover():
        rows.append(
            {
                **item,
                "terdaftar": item["port"] in registered,
                "hidup": http_alive(item["port"]),
            }
        )
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "owner": "Tomi vier",
        "license": "Tom05ivier-commits-1.0",
        "status": "OK" if all(row["hidup"] for row in rows) else "PERLU_PERBAIKAN",
        "server": rows,
        "jumlah": len(rows),
        "registry_ports": sorted(registered),
        "catatan": "Instansi --service dan server web OpenChamber tidak diawasi.",
    }


def write_report(result: dict[str, Any]) -> Path:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    tmp = REPORT.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(REPORT)
    return REPORT


def loop(interval: float = DEFAULT_INTERVAL) -> None:
    def stop(_signum: int, _frame: object) -> None:
        global _STOP
        _STOP = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while not _STOP:
        result = snapshot()
        for row in result["server"]:
            if not row["hidup"]:
                ensure(int(row["port"]))
        result = snapshot()
        write_report(result)
        time.sleep(max(1.0, interval))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    mode = args[0] if args else "report"
    if mode == "loop":
        interval = float(args[1]) if len(args) > 1 else DEFAULT_INTERVAL
        loop(interval)
        return 0
    result = snapshot()
    if mode == "check":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        path = write_report(result)
        print(f"Laporan: {path}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
