# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Diadaptasi dari PyUptimeKit (MIT, © 2026 PyUptimeKit Contributors):
#   https://github.com/HarikrishnanK9/PyUptimeKit @ 79e3a3e
# Bagian yang dipakai: pola probe TCP (connect_ex + perf_counter) dari
# src/pyuptimekit/monitors/tcp.py. Lisensi MIT asli dipertahankan penuh di
# docs/SERVICE-WATCH.md. Kode IT Agenty tetap tunduk pada Tom05ivier-commits-1.0.
"""Watchdog ringan untuk semua layanan yang terdaftar di supervisor.

Membaca system/services.json, memeriksa tiap layanan (TCP/HTTP/process),
menulis laporan JSON, dan menyajikan status lewat HTTP lokal. Berjalan
sebagai layanan supervisor; tidak membuka port selain yang didaftarkan.
"""

from __future__ import annotations

import argparse
import html
import json
import socket
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REGISTRY = ROOT / "system" / "services.json"
HEARTBEAT = ROOT / "system" / "reports" / "heartbeat.json"
REPORT = ROOT / "system" / "reports" / "service_watch.json"
DEFAULT_PORT = 8782
INTERVAL = 10.0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def tcp_probe(host: str, port: int, timeout: float = 1.0) -> dict[str, Any]:
    """Probe TCP + latensi; diadaptasi dari PyUptimeKit TcpMonitor."""
    sock: socket.socket | None = None
    started = time.perf_counter()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        code = sock.connect_ex((host, port))
        latency = (time.perf_counter() - started) * 1000
        if code == 0:
            return {
                "status": "UP",
                "latency_ms": round(latency, 3),
                "message": f"TCP {host}:{port} reachable",
            }
        return {
            "status": "DOWN",
            "latency_ms": None,
            "message": f"TCP {host}:{port} connect_ex={code}",
        }
    except (socket.timeout, OSError) as exc:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "message": f"TCP {host}:{port} error: {type(exc).__name__}",
        }
    finally:
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass


def http_probe(port: int, path: str = "/", timeout: float = 2.0) -> dict[str, Any]:
    """Probe HTTP health endpoint pada localhost."""
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}{path}", timeout=timeout
        ) as response:
            code = getattr(response, "status", 200)
        latency = (time.perf_counter() - started) * 1000
        return {
            "status": "UP" if code == 200 else "DEGRADED",
            "http_status": code,
            "latency_ms": round(latency, 3),
            "message": f"HTTP 127.0.0.1:{port}{path} -> {code}",
        }
    except Exception as exc:  # urllib memunculkan banyak tipe error
        return {
            "status": "DOWN",
            "http_status": None,
            "latency_ms": None,
            "message": f"HTTP 127.0.0.1:{port}{path} error: {type(exc).__name__}",
        }


def _heartbeat_state(heartbeat_path: Path) -> dict[str, bool]:
    try:
        data = json.loads(heartbeat_path.read_text(encoding="utf-8"))
        services = data.get("services", {})
        return {
            name: bool(item.get("alive"))
            for name, item in services.items()
            if isinstance(item, dict)
        }
    except (OSError, ValueError, TypeError):
        return {}


def check_services(
    registry_path: Path | None = None, heartbeat_path: Path | None = None
) -> dict[str, Any]:
    """Periksa semua entri registry dan kembalikan laporan lengkap."""
    registry_path = registry_path if registry_path is not None else REGISTRY
    heartbeat_path = heartbeat_path if heartbeat_path is not None else HEARTBEAT
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        definitions = registry.get("services", [])
    except (OSError, ValueError, TypeError):
        definitions = []

    states = _heartbeat_state(heartbeat_path)
    results: list[dict[str, Any]] = []
    for item in definitions:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "?"))
        kind = item.get("kind", "process")
        port = item.get("port")
        if kind == "http" and port is not None:
            probe = http_probe(int(port), str(item.get("health", "/")))
        elif kind in ("tcp", "monitor") and port is not None:
            probe = tcp_probe("127.0.0.1", int(port))
        else:
            alive = states.get(name)
            probe = {
                "status": "UP" if alive else ("DOWN" if alive is False else "UNKNOWN"),
                "latency_ms": None,
                "message": f"process '{name}' from supervisor heartbeat",
            }
        results.append({"name": name, "kind": kind, **probe})

    up = sum(1 for item in results if item["status"] == "UP")
    return {
        "checked_at": _now(),
        "source": "service-watch",
        "upstream": "PyUptimeKit (MIT) — pola probe TCP",
        "total": len(results),
        "up": up,
        "down": sum(1 for item in results if item["status"] == "DOWN"),
        "degraded": sum(1 for item in results if item["status"] == "DEGRADED"),
        "unknown": sum(1 for item in results if item["status"] == "UNKNOWN"),
        "results": results,
    }


def write_report(report: dict[str, Any], path: Path | None = None) -> Path:
    path = path if path is not None else REPORT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return path


def run_once() -> dict[str, Any]:
    report = check_services()
    write_report(report, REPORT)
    return report


def _render(report: dict[str, Any]) -> str:
    rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(item["name"])),
            html.escape(str(item["kind"])),
            html.escape(str(item["status"])),
            html.escape(str(item.get("message", ""))),
        )
        for item in report.get("results", [])
    )
    return (
        "<!doctype html><html lang='id'><meta charset='utf-8'>"
        "<title>Service Watch</title>"
        f"<h1>Service Watch</h1><p>{html.escape(str(report.get('checked_at','')))}"
        f" — UP {report.get('up',0)}/{report.get('total',0)}</p>"
        "<table border='1'><tr><th>Nama</th><th>Jenis</th><th>Status</th>"
        f"<th>Keterangan</th></tr>{rows}</table></html>"
    )


def make_handler(report_holder: dict[str, Any]) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: bytes, content_type: str, code: int = 200) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/health":
                self._send(b'{"status":"ok","service":"service-watch"}',
                           "application/json")
            elif path == "/status":
                body = json.dumps(report_holder["data"], ensure_ascii=False).encode()
                self._send(body, "application/json")
            elif path in ("/", "/index.html"):
                self._send(_render(report_holder["data"]).encode(),
                           "text/html; charset=utf-8")
            else:
                self._send(b'{"error":"not found"}', "application/json", 404)

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    return Handler


def serve(port: int = DEFAULT_PORT, interval: float = INTERVAL) -> None:
    holder: dict[str, Any] = {"data": run_once()}

    def loop() -> None:
        while True:
            time.sleep(interval)
            try:
                holder["data"] = run_once()
            except Exception:
                pass

    threading.Thread(target=loop, name="service-watch-refresh", daemon=True).start()
    server = HTTPServer(("127.0.0.1", port), make_handler(holder))
    print(f"Service Watch di http://127.0.0.1:{port}/", flush=True)
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="service_watch.py")
    parser.add_argument("command", choices=("once", "serve"), nargs="?", default="once")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--interval", type=float, default=INTERVAL)
    args = parser.parse_args(argv)
    if args.command == "serve":
        serve(args.port, max(1.0, args.interval))
    else:
        report = run_once()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
