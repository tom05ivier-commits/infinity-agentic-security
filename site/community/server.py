#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Portal komunitas IT Agenty — server HTTP stdlib (karya baru).

Tidak memakai framework, CDN, atau dependency eksternal. Hanya modul standar
Python 3 sehingga ringan untuk batas 512 MB / 1 CPU container Infinity.

Rute:
    GET  /health                    -> JSON status untuk supervisor
    GET  /                          -> index.html
    GET  /app.js, /style.css        -> aset statis
    GET  /README.md                 -> dokumentasi (text/plain)
    GET  /api/posts                 -> {"posts": [...]}
    POST /api/posts                 -> buat posting {title, body, author}
    POST /api/posts/<id>/reply      -> balas posting {author, body}
    OPTIONS <rute apa pun>          -> preflight 204

Port tetap: 8781, bind 127.0.0.1. Boleh dioverride lewat variabel lingkungan
AGENTY_COMMUNITY_PORT (atau argumen CLI pertama) untuk keperluan uji. Sengaja
TIDAK memakai variabel bernama PORT sesuai aturan AGENTS.md.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "posts.json"

DEFAULT_PORT = 8781
BIND_HOST = "127.0.0.1"
MAX_BODY = 64 * 1024  # 64 KB per permintaan POST
MAX_POSTS = 500       # jaga jejak memori tetap kecil
MAX_REPLIES = 200     # per posting

# batas panjang karakter (minimum, maksimum)
LIMITS = {
    "title": (1, 120),
    "author": (1, 60),
    "body": (1, 5000),
    "reply_body": (1, 2000),
}

# Daftar putih berkas statis: tidak ada akses path bebas / directory traversal.
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/README.md": ("README.md", "text/plain; charset=utf-8"),
}

REPLY_PATH = re.compile(r"^/api/posts/([A-Za-z0-9_-]{1,64})/reply$")
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

_LOCK = threading.RLock()


class RequestError(Exception):
    """Galat permintaan klien yang bisa dikirim sebagai JSON."""

    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def _utc_now() -> str:
    """Cap waktu UTC dalam bentuk ISO-8601."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def init_store() -> None:
    """Buat folder dan berkas data awal bila belum ada."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        _write_store({"posts": []})


def _read_store() -> dict:
    """Baca data; kembalikan struktur kosong bila berkas rusak/hilang."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            store = json.load(handle)
        if isinstance(store, dict) and isinstance(store.get("posts"), list):
            return store
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    return {"posts": []}


def _write_store(store: dict) -> None:
    """Tulis atomik: tulis file sementara lalu os.replace."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".posts-", suffix=".tmp", dir=str(DATA_DIR))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(store, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, DATA_FILE)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _field(payload: dict, key: str, bounds: tuple[int, int]) -> str:
    """Ambil dan validasi satu field teks dari payload."""
    value = payload.get(key)
    if not isinstance(value, str):
        raise RequestError(f"Field '{key}' harus berupa teks.")
    value = value.strip()
    low, high = bounds
    if not (low <= len(value) <= high):
        raise RequestError(f"Field '{key}' harus {low}–{high} karakter.")
    return value


def create_post(payload: dict) -> dict:
    """Simpan posting baru dan kembalikan objeknya."""
    title = _field(payload, "title", LIMITS["title"])
    body = _field(payload, "body", LIMITS["body"])
    author = _field(payload, "author", LIMITS["author"])
    post = {
        "id": uuid.uuid4().hex[:12],
        "title": title,
        "body": body,
        "author": author,
        "created_at": _utc_now(),
        "replies": [],
    }
    with _LOCK:
        store = _read_store()
        store["posts"].insert(0, post)
        store["posts"] = store["posts"][:MAX_POSTS]
        _write_store(store)
    return post


def add_reply(post_id: str, payload: dict) -> dict:
    """Tambahkan balasan ke posting yang diberikan."""
    if not SAFE_ID.fullmatch(post_id):
        raise RequestError("ID posting tidak valid.", 400)
    author = _field(payload, "author", LIMITS["author"])
    body = _field(payload, "body", LIMITS["reply_body"])
    reply = {
        "id": uuid.uuid4().hex[:12],
        "author": author,
        "body": body,
        "created_at": _utc_now(),
    }
    with _LOCK:
        store = _read_store()
        target = next((p for p in store["posts"] if p.get("id") == post_id), None)
        if target is None:
            raise RequestError("Posting tidak ditemukan.", 404)
        replies = target.get("replies")
        if not isinstance(replies, list):
            replies = []
        replies.append(reply)
        target["replies"] = replies[-MAX_REPLIES:]
        _write_store(store)
    return reply


class CommunityHandler(BaseHTTPRequestHandler):
    """Handler HTTP untuk portal komunitas."""

    server_version = "AgentyCommunity/1.0"
    protocol_version = "HTTP/1.1"
    timeout = 15

    # ---- pembantu respons -------------------------------------------------
    @staticmethod
    def _health_payload() -> dict:
        with _LOCK:
            count = len(_read_store()["posts"])
        return {
            "status": "OK",
            "system": "IT Agenty Community",
            "version": "1.0",
            "posts": count,
            "license": "Tom05ivier-commits-1.0",
        }

    def _send_json(self, payload: object, status: int = 200, head: bool = False) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def _send_static(self, path: str, head: bool = False) -> None:
        entry = STATIC.get(path)
        if entry is None:
            self._send_json({"error": "Halaman tidak ditemukan."}, 404, head=head)
            return
        name, content_type = entry
        try:
            body = (ROOT / name).read_bytes()
        except OSError:
            self._send_json({"error": "Berkas tidak tersedia."}, 500, head=head)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def end_headers(self) -> None:  # noqa: D102
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        # Saring log agar tidak mencetak data pengguna ke stderr.
        pass

    # ---- pembacaan body ---------------------------------------------------
    def _read_json_body(self) -> dict:
        if "chunked" in self.headers.get("Transfer-Encoding", "").lower():
            raise RequestError("Transfer-Encoding chunked tidak didukung.")
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise RequestError("Content-Length tidak valid.")
        if length <= 0:
            raise RequestError("Body permintaan kosong.")
        if length > MAX_BODY:
            raise RequestError(
                f"Body terlalu besar (maksimal {MAX_BODY} byte).", 413
            )
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise RequestError("Body permintaan tidak lengkap.")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RequestError("Body harus berupa JSON yang valid.")
        if not isinstance(payload, dict):
            raise RequestError("Body harus berupa objek JSON.")
        return payload

    # ---- rute -------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        try:
            if path in ("/health", "/health/"):
                self._send_json(self._health_payload())
                return
            if path == "/api/posts":
                with _LOCK:
                    store = _read_store()
                self._send_json({"posts": store["posts"]})
                return
            if path.startswith("/api/"):
                self._send_json({"error": "Endpoint tidak ditemukan."}, 404)
                return
            self._send_static(path)
        except BrokenPipeError:
            pass
        except Exception:  # pragma: no cover - jangan bocorkan traceback
            try:
                self._send_json({"error": "Galat internal server."}, 500)
            except BrokenPipeError:
                pass

    def do_HEAD(self) -> None:  # noqa: N802
        """Header saja, tanpa body — untuk probe monitoring ringan."""
        path = self.path.split("?", 1)[0]
        try:
            if path in ("/health", "/health/"):
                self._send_json(self._health_payload(), head=True)
            elif path == "/api/posts":
                with _LOCK:
                    store = _read_store()
                self._send_json({"posts": store["posts"]}, head=True)
            elif path.startswith("/api/"):
                self._send_json({"error": "Endpoint tidak ditemukan."}, 404, head=True)
            else:
                self._send_static(path, head=True)
        except BrokenPipeError:
            pass
        except Exception:  # pragma: no cover
            try:
                self._send_json({"error": "Galat internal server."}, 500, head=True)
            except BrokenPipeError:
                pass

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        try:
            if path == "/api/posts":
                post = create_post(self._read_json_body())
                self._send_json(post, 201)
                return
            match = REPLY_PATH.fullmatch(path)
            if match:
                reply = add_reply(match.group(1), self._read_json_body())
                self._send_json(reply, 201)
                return
            self._send_json({"error": "Endpoint tidak ditemukan."}, 404)
        except RequestError as exc:
            # Body yang ditolak mungkin belum terbaca; tutup koneksi agar sisa
            # byte tidak disalahartikan sebagai permintaan berikutnya.
            self.close_connection = True
            try:
                self._send_json({"error": exc.message}, exc.status)
            except BrokenPipeError:
                pass
        except BrokenPipeError:
            pass
        except Exception:  # pragma: no cover
            try:
                self._send_json({"error": "Galat internal server."}, 500)
            except BrokenPipeError:
                pass

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Allow", "GET, POST, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()


def serve(port: int = DEFAULT_PORT, host: str = BIND_HOST) -> None:
    """Inisialisasi data lalu jalankan server sampai dihentikan."""
    init_store()
    httpd = ThreadingHTTPServer((host, port), CommunityHandler)
    httpd.daemon_threads = True
    print(f"Portal komunitas berjalan di http://{host}:{port}/", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


def main() -> None:
    port = DEFAULT_PORT
    raw = os.environ.get("AGENTY_COMMUNITY_PORT")
    if len(sys.argv) > 1:
        raw = sys.argv[1]
    if raw:
        try:
            candidate = int(raw)
            if 1 <= candidate <= 65535:
                port = candidate
            else:
                print(f"Port {raw} di luar rentang; memakai {DEFAULT_PORT}.", flush=True)
        except ValueError:
            print(f"Port '{raw}' tidak valid; memakai {DEFAULT_PORT}.", flush=True)
    serve(port)


if __name__ == "__main__":
    main()
