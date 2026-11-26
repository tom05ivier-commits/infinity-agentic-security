# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Layanan HTTP situs & API generator domain gratis IT Agenty.

Berjalan di localhost. Menyajikan halaman generator, domain lokal
`*.agenty.local`, panduan penyedia gratis, dan status DDNS (tanpa token).
Tidak ada permintaan jaringan keluar dari layanan ini.
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import domain_manager as dm  # noqa: E402
from system.ddns_client import status as ddns_status  # noqa: E402

SITE = ROOT / "site" / "domain"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
SERVICE = "domain"


def _json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "AgentyDomain/1.0"

    def _send(self, code: int, payload: dict[str, Any]) -> None:
        body = _json(payload)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _static(self, name: str) -> None:
        path = SITE / name
        if not path.is_file():
            self._send(404, {"error": "tidak ditemukan", "path": name})
            return
        body = path.read_bytes()
        ctype = "text/html; charset=utf-8" if name.endswith(".html") else (
            "text/javascript; charset=utf-8" if name.endswith(".js")
            else "text/css; charset=utf-8"
        )
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if not length:
            return {}
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except (ValueError, UnicodeDecodeError):
            return {}

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        if path == "/health":
            self._send(200, {
                "status": "ok", "service": SERVICE,
                "license": LICENSE, "owner": OWNER,
            })
        elif path in ("/", "/index.html"):
            self._static("index.html")
        elif path == "/guide":
            self._static("guide.html")
        elif path == "/app.js":
            self._static("app.js")
        elif path == "/styles.css":
            self._static("styles.css")
        elif path == "/api/suggest":
            seed = query.get("seed", ["agenty"])[0]
            try:
                count = int(query.get("count", ["8"])[0])
            except ValueError:
                count = 8
            self._send(200, {"domains": dm.suggest(seed, count)})
        elif path == "/api/domains":
            self._send(200, dm.status())
        elif path == "/api/ddns/status":
            self._send(200, ddns_status())
        elif path == "/api/guide":
            self._send(200, {"providers": dm.guide()})
        elif path == "/capabilities":
            self._send(200, {
                "service": SERVICE,
                "root_domain": dm.ROOT_DOMAIN,
                "endpoints": [
                    "/health", "/", "/guide", "/api/suggest", "/api/domains",
                    "/api/ddns/status", "/api/guide", "/capabilities",
                ],
                "mutations": ["POST /api/domains", "POST /api/install"],
                "license": LICENSE, "owner": OWNER,
            })
        else:
            self._send(404, {"error": "tidak ditemukan", "path": path})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        body = self._body()
        try:
            if path == "/api/domains":
                entry = dm.add(str(body.get("name", "")), str(body.get("target", "127.0.0.1")))
                self._send(201, {"status": "OK", "domain": entry})
            elif path == "/api/domains/remove":
                removed = dm.remove(str(body.get("name", "")))
                self._send(200, {"status": "OK", "removed": removed})
            elif path == "/api/install":
                result = dm.install_hosts(authorize=bool(body.get("authorize")))
                self._send(200, result)
            else:
                self._send(404, {"error": "tidak ditemukan", "path": path})
        except (ValueError, PermissionError, OSError) as exc:
            self._send(400, {"status": "GAGAL", "error": str(exc)})

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def build_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Situs generator domain IT Agenty")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8784)
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
