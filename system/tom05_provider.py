# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Provider OpenAI-compatible lokal untuk identitas Tom05.

Mendengar di 127.0.0.1:8772 dan meneruskan permintaan ke bridge yang sudah
ada (127.0.0.1:8766). Model yang diekspos:

* ``tom05-flash-free`` — alias identitas Tom05 (diteruskan ke model upstream).
* Seluruh model pihak ketiga dari ``opencode models`` — sebagai **alias
  proxied**, dimuat dari ``config/tom05-provider-models.json``.

Model pihak ketiga tidak diubah, diambil alih, atau diklaim sebagai model
baru tom05; provider hanya meneruskan permintaan ke runtime yang tersedia.
Tidak ada kredensial yang dibaca, disimpan, atau dicetak oleh server ini.
"""

from __future__ import annotations

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("TOM05_PROVIDER_PORT", "8772"))
UPSTREAM = os.environ.get(
    "TOM05_UPSTREAM", "http://127.0.0.1:8766/v1/chat/completions"
).rstrip("/")
UPSTREAM_MODEL = os.environ.get("TOM05_UPSTREAM_MODEL", "hy4-flash-free")
MODEL_ID = "tom05-flash-free"
CTL = int(os.environ.get("TOM05_CTL", "100000000"))
CATALOG = Path(
    os.environ.get(
        "TOM05_MODEL_CATALOG",
        str(ROOT / "config" / "tom05-provider-models.json"),
    )
)


def load_proxied_models() -> list[dict[str, Any]]:
    """Baca katalog model pihak ketiga; kosong bila berkas tidak ada."""
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [item for item in data.get("models", []) if isinstance(item, dict)]


PROXIED = load_proxied_models()


def model_entries() -> list[dict[str, Any]]:
    """Daftar model yang diiklankan: alias Tom05 + model proxied."""
    entries: list[dict[str, Any]] = [{
        "id": MODEL_ID,
        "object": "model",
        "owned_by": "tom05",
        "name": "Tom05 flash Free",
        "context_length": CTL,
        "declared_only": True,
        "aliases": ["tom05/tom05-flash-free"],
    }]
    for item in PROXIED:
        model_id = str(item.get("id", ""))
        if not model_id or model_id.startswith("tom05/"):
            continue  # identitas Tom05 sudah diwakili entri alias di atas
        try:
            ctl = int(item.get("ctl", CTL))
        except (TypeError, ValueError):
            ctl = CTL
        entries.append({
            "id": model_id,
            "object": "model",
            "owned_by": item.get("owned_by", "third-party"),
            "proxied": True,
            "source": "opencode",
            "context_length": ctl,
            "declared_only": True,
            "note": "Model pihak ketiga; diteruskan ke runtime, bukan model baru tom05.",
        })
    return entries


def resolve_upstream(requested: str) -> str:
    """Terjemahkan ID model yang diminta menjadi ID model upstream."""
    value = (requested or "").strip()
    if value in ("", MODEL_ID, "tom05/tom05-flash-free"):
        return UPSTREAM_MODEL
    if value.startswith("tom05/"):
        return value[len("tom05/"):]
    return value  # ID pihak ketiga diteruskan apa adanya


def _send(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        return  # senyap: tidak menulis prompt atau data ke log

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") in ("/health", "/v1/health"):
            _send(self, 200, {
                "status": "ok",
                "provider": "tom05",
                "model": MODEL_ID,
                "proxied_models": len(PROXIED),
            })
        elif self.path.rstrip("/") in ("/v1/models", "/models"):
            entries = model_entries()
            _send(self, 200, {
                "object": "list",
                "total": len(entries),
                "data": entries,
            })
        else:
            _send(self, 404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") not in ("/v1/chat/completions", "/chat/completions"):
            _send(self, 404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            _send(self, 400, {"error": "invalid JSON"})
            return
        if not isinstance(body, dict):
            _send(self, 400, {"error": "invalid body"})
            return
        body["model"] = resolve_upstream(str(body.get("model", "")))
        request = urllib.request.Request(
            UPSTREAM,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type", "application/json")
        except Exception as exc:  # noqa: BLE001
            _send(self, 502, {"error": "upstream gagal", "jenis": type(exc).__name__})
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[tom05] provider aktif di http://127.0.0.1:{PORT}/v1", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
