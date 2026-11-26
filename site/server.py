#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Server statis mandiri untuk kumpulan situs IT Agenty.

Menyajikan direktori ``site/`` tanpa dependensi eksternal. Tidak ada CDN,
tidak ada framework, dan tidak ada proses lain — sengaja dibuat seringan
mungkin agar muat di batas 512 MB / 1 CPU container Infinity.

Rute server utama (port 8769):
    /          hub yang menautkan semua situs
    /chip/     replika mandiri Sandbox Chip Merah Putih
    /agency/   landing page IT Agenty / Infinity Security System
    /mirror/   halaman penjelas mirror (aplikasi asli di port 8770)
    /mirror-info.html  halaman penjelas tersebut
    /health    health check JSON untuk supervisor

Mode ``--mirror`` (port 8770) menyajikan ``site/mirror/`` sebagai document root
supaya router React asli yang memakai path absolut (/simulator, /daftar, ...)
tetap berfungsi seperti di situs aslinya.
"""

from __future__ import annotations

import json
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "mirror"
DEFAULT_PORT = 8769
MIRROR_PORT = 8770


class SiteHandler(SimpleHTTPRequestHandler):
    """Handler statis dengan health check, fallback SPA, dan header keamanan."""

    server_version = "AgentySite/1.0"
    spa_prefix = "/mirror/"
    fallback_file = "/mirror-info.html"
    force_spa = False
    api_stub = False

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _health(self) -> None:
        self._send_json(
            {
                "status": "OK",
                "system": "IT Agenty static sites",
                "sites": ["hub", "chip", "agency", "mirror"],
            }
        )

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/health", "/health/"):
            self._health()
            return

        # Mirror asli menanyakan status login/captcha saat memuat halaman
        # masuk dan daftar. Beri jawaban JSON yang valid agar tidak terjadi
        # galat parsing; prose autentikasi tetap tidak tersedia offline.
        if self.api_stub and path.startswith("/api/"):
            self._send_json(
                {
                    "status": "ok",
                    "authenticated": False,
                    "captcha_enabled": False,
                    "github_enabled": False,
                    "google_enabled": False,
                    "message": "Mode mirror offline — backend tidak tersedia",
                }
            )
            return

        # Fallback SPA: rute klien tanpa ekstensi tidak ada sebagai berkas,
        # jadi layani shell index.html. Berkas dengan ekstensi tetap 404 agar
        # aset yang hilang tidak tersembunyi.
        leaf = path.rsplit("/", 1)[-1]
        if self.spa_prefix and path.startswith(self.spa_prefix):
            candidate = Path(self.directory) / path.lstrip("/")
            use_fallback = self.force_spa or (
                "." not in leaf
                and not candidate.exists()
                and not candidate.is_dir()
            )
            if use_fallback:
                query = self.path[len(path):]
                self.path = self.fallback_file + query
        super().do_GET()

    def end_headers(self) -> None:  # noqa: D102
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        # Saring log agar tidak mencetak informasi sensitif ke stderr.
        pass


def make_handler(
    root: Path,
    spa_prefix: str,
    fallback_file: str,
    api_stub: bool = False,
    force_spa: bool = False,
):
    """Buat handler dengan root dokumen dan aturan fallback tertentu."""

    class Handler(SiteHandler):
        pass

    Handler.spa_prefix = spa_prefix
    Handler.fallback_file = fallback_file
    Handler.api_stub = api_stub
    Handler.force_spa = force_spa
    return partial(Handler, directory=str(root))


def serve(
    port: int = DEFAULT_PORT,
    host: str | None = None,
    root: Path = ROOT,
    spa_prefix: str = "/mirror/",
    fallback_file: str = "/mirror-info.html",
    api_stub: bool = False,
    force_spa: bool = False,
) -> None:
    """Jalankan server statis pada ``host:port``."""
    bind = host or os.environ.get("AGENTY_BIND_HOST", "127.0.0.1")
    handler = make_handler(root, spa_prefix, fallback_file, api_stub, force_spa)
    ThreadingHTTPServer((bind, port), handler).serve_forever()


if __name__ == "__main__":
    mirror_mode = "--mirror" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--mirror"]
    port_arg = int(args[0]) if args else int(
        os.environ.get("SITE_PORT", MIRROR_PORT if mirror_mode else DEFAULT_PORT)
    )
    label = "mirror" if mirror_mode else "situs"
    print(f"Server {label} berjalan di http://127.0.0.1:{port_arg}/")
    if mirror_mode:
        serve(
            port_arg,
            root=MIRROR,
            spa_prefix="/",
            fallback_file="/index.html",
            api_stub=True,
        )
    else:
        serve(port_arg, force_spa=True)
