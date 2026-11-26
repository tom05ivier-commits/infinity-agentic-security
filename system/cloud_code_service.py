# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Layanan HTTP read-only untuk status Cloud Code di supervisor IT Agenty.

Tidak membuka koneksi keluar, tidak membaca kredensial, dan tidak menjalankan
perintah cloud. Semua data berasal dari deteksi biner di PATH.
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

from system.cloud_code import capabilities, detect, status  # noqa: E402

LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
SERVICE = "cloud-code"


class Handler(BaseHTTPRequestHandler):
    server_version = "AgentyCloudCode/1.0"

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
            })
        elif path == "/capabilities":
            self._send(200, capabilities())
        elif path == "/tools":
            self._send(200, {"alat": detect(), "license": LICENSE, "owner": OWNER})
        elif path in ("/", "/status"):
            self._send(200, status())
        else:
            self._send(404, {"error": "tidak ditemukan", "path": path})

    def log_message(self, fmt: str, *args: Any) -> None:
        # Jangan menulis permintaan ke log publik; layanan ini read-only.
        return


def build_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Layanan status Cloud Code IT Agenty")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8785)
    args = parser.parse_args(argv)

    server = build_server(args.host, args.port)

    def stop(_signum: int, _frame: Any) -> None:
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
