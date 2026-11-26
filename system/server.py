# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Server HTTP lokal untuk menyajikan dashboard dan snapshot sistem.

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .core import WORKSPACE, ComputerSystem
from .dashboard import OUTPUT, generate

DASHBOARD = generate()


class SystemHandler(BaseHTTPRequestHandler):
    """Handler untuk endpoint sistem."""

    server_version = "InfinitySystem/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/", "/dashboard"):
            content = OUTPUT.read_bytes()
            self._send(200, content, "text/html; charset=utf-8")
        elif path == "/api/snapshot":
            self._json(ComputerSystem().snapshot())
        elif path == "/api/health":
            self._json({"status": "OK", "system": "Infinity Computer System"})
        elif path == "/api/license":
            self._json(ComputerSystem().license())
        elif path == "/api/identity":
            self._json(ComputerSystem().identity())
        else:
            self._json({"error": "Not found", "path": path}, status=404)

    def log_message(self, fmt: str, *args: object) -> None:
        # Saring log agar tidak mencetak informasi sensitif ke stderr.
        pass


def serve(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    """Jalankan server HTTP lokal."""
    server = ThreadingHTTPServer((host, port), SystemHandler)
    return server
