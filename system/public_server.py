# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Server publik dengan Basic Auth untuk akses online melalui tunnel.

from __future__ import annotations

import base64
import binascii
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

DEFAULT_PORT = 8768

USER = os.environ.get("AGENTY_AUTH_USER") or os.environ.get("OPENCODE_SERVER_USERNAME", "")
PASSWORD = os.environ.get("AGENTY_AUTH_PASS") or os.environ.get("OPENCODE_SERVER_PASSWORD", "")


def _authorized(header: str | None) -> bool:
    if not USER or not PASSWORD:
        return False
    if not header or not header.startswith("Basic "):
        return False
    try:
        raw = base64.b64decode(header.split(None, 1)[1]).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, IndexError):
        return False
    user, _, password = raw.partition(":")
    return hmac.compare_digest(user, USER) and hmac.compare_digest(password, PASSWORD)


class Handler(BaseHTTPRequestHandler):
    server_version = "InfinityPublic/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if status == 401:
            self.send_header("WWW-Authenticate", 'Basic realm="Infinity Security"')
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200) -> None:
        self._send(
            status,
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json",
        )

    def do_GET(self) -> None:  # noqa: N802
        if not _authorized(self.headers.get("Authorization")):
            self._json({"error": "authentication required"}, status=401)
            return
        path = self.path.split("?", 1)[0]
        if path == "/api/health":
            self._json({"status": "OK", "mode": "public", "authenticated": True})
        elif path in ("/", "/status"):
            body = """<!DOCTYPE html><html lang="id"><head><meta charset="UTF-8">
<title>Infinity Public Status</title></head><body>
<h1>IT Agenty - Infinity</h1>
<p>Akses online aktif. Sistem dan proteksi berjalan.</p>
<p><a href="/api/health">/api/health</a></p>
</body></html>"""
            self._send(200, body.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self._json({"error": "not found"}, status=404)

    def log_message(self, fmt: str, *args: object) -> None:
        pass


def serve(port: int = DEFAULT_PORT) -> None:
    if not USER or not PASSWORD:
        raise SystemExit("Kredensial publik belum tersedia (AGENTY_AUTH_USER/PASS).")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT)
