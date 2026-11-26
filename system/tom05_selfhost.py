# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Server inferensi mandiri tom05 (self-hosted), tanpa pihak ketiga.

Server ini sengaja TIDAK meneruskan permintaan ke model opencode maupun pihak
ketiga lainnya. Ia hanya:

* mengiklankan identitas ``tom05-flash-free``;
* menjawab dari model pengetahuan retrieval (bukan neural terlatih) bila belum
  ada endpoint milik pemilik;
* meneruskan ke endpoint lokal itu bila sudah diset — itu pun hanya loopback.

Tidak ada kredensial yang dibaca, disimpan, atau dicetak. Prompt tidak masuk log.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:  # Model pengetahuan retrieval dari data workspace (bukan neural terlatih).
    from system.tom05_knowledge import get_model  # noqa: E402
except Exception:  # pragma: no cover
    get_model = None  # type: ignore[assignment]

PORT = int(os.environ.get("TOM05_SELFHOST_PORT", "8773"))
ENDPOINT = os.environ.get("TOM05_SELFHOST_ENDPOINT", "").strip().rstrip("/")
MODEL_ID = "tom05-flash-free"
CTL = int(os.environ.get("TOM05_SELFHOST_CTL", "100000000"))
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"


def loopback_ok(url: str) -> bool:
    """Terima hanya endpoint loopback; tolak jaringan eksternal."""
    if not url:
        return False
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}


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
        return  # senyap: prompt/data tidak ditulis ke log

    def _send_stream(self, payload: dict[str, Any]) -> None:
        """Kirim jawaban sebagai SSE OpenAI-compatible dengan finish_reason."""
        choice = (payload.get("choices") or [{}])[0]
        content = choice.get("message", {}).get("content", "")
        model = payload.get("model", MODEL_ID)
        chunk = {
            "id": payload.get("id", "chatcmpl-stream"),
            "object": "chat.completion.chunk",
            "model": model,
            "choices": [{"index": 0, "delta": {"role": "assistant", "content": content},
                         "finish_reason": None}],
        }
        final = {
            "id": chunk["id"],
            "object": "chat.completion.chunk",
            "model": model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        body = "".join(
            f"data: {json.dumps(part, ensure_ascii=False)}\n\n" for part in (chunk, final)
        ) + "data: [DONE]\n\n"
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.rstrip("/")
        if path in ("/health", "/v1/health"):
            _send(self, 200, {
                "status": "ok",
                "provider": "tom05-selfhost",
                "model": MODEL_ID,
                "backend": "self-hosted",
                "endpoint_terhubung": loopback_ok(ENDPOINT),
                "model_mode": "forward" if loopback_ok(ENDPOINT) else "retrieval",
                "pihak_ketiga": False,
                "license": LICENSE,
                "owner": OWNER,
            })
        elif path in ("/v1/models", "/models"):
            _send(self, 200, {
                "object": "list", "total": 1,
                "data": [{
                    "id": MODEL_ID, "object": "model", "owned_by": "tom05",
                    "name": "Tom05 flash Free", "context_length": CTL,
                    "declared_only": True, "license": LICENSE,
                }],
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
        wants_stream = bool(body.get("stream"))
        if not loopback_ok(ENDPOINT):
            if get_model is None:
                _send(self, 503, {
                    "error": "model pengetahuan tidak tersedia",
                    "catatan": "Modul system/tom05_knowledge.py tidak dapat dimuat.",
                    "license": LICENSE,
                })
                return
            user_text = ""
            messages = body.get("messages") or []
            if isinstance(messages, list):
                for msg in messages:
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        user_text = str(msg.get("content", ""))
                        break
            answer = get_model().answer(user_text or "status")
            if wants_stream:
                self._send_stream(answer)
            else:
                _send(self, 200, answer)
            return
        request = urllib.request.Request(
            f"{ENDPOINT}/v1/chat/completions",
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type", "application/json")
        except Exception as exc:  # noqa: BLE001
            _send(self, 502, {"error": "endpoint lokal gagal", "jenis": type(exc).__name__})
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[tom05-selfhost] aktif di http://127.0.0.1:{PORT}/v1", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
