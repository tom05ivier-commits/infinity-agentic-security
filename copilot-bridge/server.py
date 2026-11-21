# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Bridge OpenAI-compatible untuk Copilot CLI → OpenCode hy4-flash-free.

from __future__ import annotations

import json
import subprocess
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

MODEL = "opencode/hy4-flash-free"
PUBLIC_MODEL = "hy4-flash-free"
DEFAULT_PORT = 8766


def _extract_text(stdout: str) -> str:
    """Ambil teks dari keluaran JSON `opencode run --format json`."""
    chunks: list[str] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            chunks.append(line)
            continue
        if isinstance(event, dict):
            part = event.get("part")
            if isinstance(part, dict) and part.get("type") == "text":
                chunks.append(str(part.get("text", "")))
            elif isinstance(part, str):
                chunks.append(part)
            elif "content" in event:
                chunks.append(str(event["content"]))
    return "".join(chunks).strip()


def call_opencode(messages: list[dict[str, Any]]) -> str:
    """Teruskan percakapan ke OpenCode dan kembalikan jawaban asisten."""
    prompt_parts = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                str(
                    item.get("text", "")
                    if isinstance(item, dict)
                    else item
                )
                for item in content
            )
        if str(content).strip():
            prompt_parts.append(f"{role}: {content}")
    if not prompt_parts:
        return ""

    command = [
        "opencode", "run", "--model", MODEL, "--format", "json",
        "\n".join(prompt_parts),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"[bridge error] {exc}"
    if completed.returncode != 0:
        return f"[bridge error] {completed.stderr[:400]}"
    return _extract_text(completed.stdout)


class Handler(BaseHTTPRequestHandler):
    server_version = "InfinityCopilotBridge/1.0"

    def _json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/").endswith("/models"):
            self._json(
                {
                    "object": "list",
                    "data": [
                        {
                            "id": PUBLIC_MODEL,
                            "object": "model",
                            "created": int(time.time()),
                            "owned_by": "opencode",
                        }
                    ],
                }
            )
        else:
            self._json({"error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.rstrip("/").endswith("/chat/completions"):
            self._json({"error": "not found"}, status=404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            request = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json({"error": "invalid json"}, status=400)
            return

        messages = request.get("messages", [])
        answer = call_opencode(messages)
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

        if request.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": PUBLIC_MODEL,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": answer},
                        "finish_reason": None,
                    }
                ],
            }
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            final = dict(chunk)
            final["choices"] = [
                {"index": 0, "delta": {}, "finish_reason": "stop"}
            ]
            self.wfile.write(f"data: {json.dumps(final)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
            return

        self._json(
            {
                "id": completion_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": PUBLIC_MODEL,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": answer},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            }
        )

    def log_message(self, fmt: str, *args: object) -> None:
        pass


def serve(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    serve(port=int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT)
