# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Bridge OpenAI-compatible untuk Copilot CLI → OpenCode hy4-flash-free (v2).

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODEL = os.environ.get("COPILOT_BRIDGE_MODEL", "opencode/hy4-flash-free")
VARIANT = os.environ.get("COPILOT_BRIDGE_VARIANT", "")
MODEL_ID = os.environ.get("COPILOT_BRIDGE_MODEL_ID", "hy4-flash-free")
PORT = int(os.environ.get("COPILOT_BRIDGE_PORT", "8766"))
TIMEOUT = int(os.environ.get("COPILOT_BRIDGE_TIMEOUT", "180"))
MAX_HISTORY = 8
CACHE_SIZE = 64

INSTRUCTIONS = ROOT / ".github" / "copilot-instructions.md"


def _system_prompt() -> str:
    """Konteks tetap dari data workspace kita."""
    base = (
        "Kamu adalah asisten IT Agenty — Infinity. Pemilik: Tomi vier, "
        "lisensi Tom05ivier-commits-1.0. Jangan pernah mencuri atau membocorkan data. "
        "Aksi ofensif hanya di lab/localhost dengan izin."
    )
    try:
        extra = INSTRUCTIONS.read_text(encoding="utf-8")[:6000]
    except OSError:
        extra = ""
    return f"{base}\n\n{extra}".strip()


SYSTEM_PROMPT = _system_prompt()

_cache: dict[str, str] = {}
_metrics: dict[str, Any] = {
    "calls": 0,
    "errors": 0,
    "cache_hits": 0,
    "latencies": deque(maxlen=50),
    "started_at": datetime.now(timezone.utc).isoformat(),
}


def _extract_text(stdout: str) -> str:
    texts: list[str] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = event.get("part") or {}
        text = part.get("text") if isinstance(part, dict) else None
        if isinstance(text, str):
            texts.append(text)
    return "".join(texts).strip()


def invoke(prompt: str) -> str:
    """Jalankan OpenCode dengan retry dan cache."""
    key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if key in _cache:
        _metrics["cache_hits"] += 1
        return _cache[key]

    model = MODEL if not VARIANT else f"{MODEL}#{VARIANT}"
    command = [
        "opencode", "run", "--model", model, "--format", "json",
        "--", prompt,
    ]
    last_error = ""
    for attempt in range(2):
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            last_error = str(exc)
            time.sleep(0.5 * (attempt + 1))
            continue
        _metrics["latencies"].append(round(time.monotonic() - started, 3))
        if completed.returncode == 0:
            answer = _extract_text(completed.stdout)
            if answer:
                if len(_cache) >= CACHE_SIZE:
                    _cache.pop(next(iter(_cache)))
                _cache[key] = answer
                return answer
            last_error = "respons kosong"
        else:
            last_error = completed.stderr[:300] or "gagal"
        time.sleep(0.5 * (attempt + 1))
    _metrics["errors"] += 1
    return f"[bridge error] {last_error}"


def _prompt_from(messages: list[dict[str, Any]]) -> str:
    """Bangun prompt dengan system prompt dan riwayat terakhir."""
    history = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                str(item.get("text", ""))
                for item in content
                if isinstance(item, dict)
            )
        if role != "system" and str(content).strip():
            history.append(f"[{role}] {content}")
    recent = history[-MAX_HISTORY:]
    return f"{SYSTEM_PROMPT}\n\n---\n" + "\n".join(recent)


def _metrics_report() -> dict[str, Any]:
    latencies = list(_metrics["latencies"])
    return {
        "calls": _metrics["calls"],
        "errors": _metrics["errors"],
        "cache_hits": _metrics["cache_hits"],
        "cache_size": len(_cache),
        "avg_latency_seconds": (
            round(sum(latencies) / len(latencies), 3) if latencies else 0
        ),
        "started_at": _metrics["started_at"],
        "model": MODEL,
        "variant": VARIANT or "default",
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "CopilotBridge/2.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200) -> None:
        self._send(
            status,
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json",
        )

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.rstrip("/")
        if path.endswith("/models"):
            self._json(
                {
                    "object": "list",
                    "data": [
                        {
                            "id": MODEL_ID,
                            "object": "model",
                            "owned_by": "opencode",
                        }
                    ],
                }
            )
        elif path.endswith("/health"):
            self._json(
                {
                    "status": "OK",
                    "model": MODEL,
                    "variant": VARIANT or "default",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        elif path.endswith("/metrics"):
            self._json(_metrics_report())
        else:
            self._json({"error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.rstrip("/").endswith("/chat/completions"):
            self._json({"error": "not found"}, status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            self._json({"error": "invalid request"}, status=400)
            return

        _metrics["calls"] += 1
        prompt = _prompt_from(payload.get("messages", []))
        answer = invoke(prompt)
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created = int(time.time())

        if payload.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            for index in range(0, max(len(answer), 1), 120):
                piece = answer[index:index + 120]
                chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": payload.get("model", MODEL_ID),
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"role": "assistant", "content": piece},
                            "finish_reason": None,
                        }
                    ],
                }
                self.wfile.write(
                    f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n".encode()
                )
                self.wfile.flush()
            final = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": payload.get("model", MODEL_ID),
                "choices": [
                    {"index": 0, "delta": {}, "finish_reason": "stop"}
                ],
            }
            self.wfile.write(f"data: {json.dumps(final)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
            return

        self._json(
            {
                "id": completion_id,
                "object": "chat.completion",
                "created": created,
                "model": payload.get("model", MODEL_ID),
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": answer},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": len(prompt) // 4,
                    "completion_tokens": len(answer) // 4,
                },
            }
        )

    def log_message(self, fmt: str, *args: object) -> None:
        pass


def serve() -> None:
    import os

    host = os.environ.get("AGENTY_BIND_HOST", "127.0.0.1")
    ThreadingHTTPServer((host, PORT), Handler).serve_forever()


if __name__ == "__main__":
    serve()
