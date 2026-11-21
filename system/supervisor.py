# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Supervisor always-on: menjaga semua server tetap berjalan dari registry.

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HEARTBEAT = ROOT / "system" / "reports" / "heartbeat.json"
REGISTRY = ROOT / "system" / "services.json"

DEFAULT_SERVICES: list[dict[str, Any]] = [
    {
        "name": "server",
        "kind": "http",
        "port": 8765,
        "health": "/api/health",
        "command": ["python3", "system/cli.py", "serve", "--host", "127.0.0.1", "--port", "8765"],
    },
    {
        "name": "protection",
        "kind": "process",
        "command": ["python3", "system/cli.py", "protect", "--seconds", "3600", "--interval", "0.5"],
    },
    {
        "name": "bridge",
        "kind": "http",
        "port": 8766,
        "health": "/v1/health",
        "command": ["python3", "copilot-bridge/bridge.py"],
    },
    {
        "name": "files",
        "kind": "http",
        "port": 8767,
        "health": "/",
        "command": ["python3", "system/fileserver.py", "8767"],
    },
]


def load_services() -> list[dict[str, Any]]:
    """Baca registry server; jatuh ke default bila tidak ada/rusak."""
    if REGISTRY.exists():
        try:
            data = json.loads(REGISTRY.read_text(encoding="utf-8"))
            services = data.get("services", [])
            if services and all("name" in item for item in services):
                disabled = {
                    name
                    for name, env in (
                        ("tunnel", "AGENTY_DISABLE_TUNNEL"),
                        ("public", "AGENTY_DISABLE_PUBLIC"),
                    )
                    if os.environ.get(env) == "1"
                }
                return [item for item in services if item.get("name") not in disabled]
        except (OSError, json.JSONDecodeError):
            pass
    return DEFAULT_SERVICES


def port_open(port: int = 8765) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def http_alive(port: int, path: str = "/") -> bool:
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}{path}", timeout=1
        ) as response:
            return response.status == 200
    except Exception:
        return False


def server_alive(port: int = 8765) -> bool:
    """Cek dashboard dengan beberapa percobaan sebelum memutuskan mati."""
    for _ in range(3):
        if http_alive(port, "/api/health"):
            return True
        time.sleep(0.2)
    return port_open(port)


class Supervisor:
    """Menjalankan semua layanan dari registry tanpa henti."""

    def __init__(self, interval: float = 5.0, port: int = 8765) -> None:
        self.interval = max(1.0, interval)
        self.port = port
        self.definitions = load_services()
        self.processes: dict[str, subprocess.Popen[bytes]] = {}
        self.restarts: dict[str, int] = {}

    def definition(self, name: str) -> dict[str, Any]:
        for item in self.definitions:
            if item.get("name") == name:
                return item
        raise ValueError(f"Layanan tidak dikenal: {name}")

    @property
    def names(self) -> list[str]:
        return [item["name"] for item in self.definitions]

    def command(self, name: str) -> list[str]:
        raw = list(self.definition(name).get("command", []))
        command = [
            sys.executable if part == "python3" else part
            for part in raw
        ]
        return command

    def is_alive(self, name: str) -> bool:
        definition = self.definition(name)
        kind = definition.get("kind", "process")
        if kind == "http":
            port = int(definition.get("port", 0)) or self.port
            path = str(definition.get("health", "/"))
            if name == "server":
                return server_alive(port)
            return http_alive(port, path)
        process = self.processes.get(name)
        return process is not None and process.poll() is None

    def start(self, name: str) -> None:
        process = subprocess.Popen(
            self.command(name),
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.processes[name] = process
        self.restarts[name] = self.restarts.get(name, 0) + 1

    def heartbeat(self) -> dict[str, Any]:
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                name: {
                    "alive": self.is_alive(name),
                    "pid": getattr(self.processes.get(name), "pid", None),
                }
                for name in self.names
            },
            "restarts": dict(self.restarts),
            "rule": "selalu jalankan komputer; buat server untuk komponen baru",
            "registry": str(REGISTRY),
        }
        HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
        HEARTBEAT.write_text(
            json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return status

    def refresh(self) -> None:
        """Baca ulang registry agar layanan baru otomatis dijalankan."""
        self.definitions = load_services()
        active = set(self.names)
        for name in list(self.processes):
            if name not in active:
                process = self.processes.pop(name)
                if process.poll() is None:
                    process.terminate()
                self.restarts.pop(name, None)

    def run(self) -> None:
        while True:
            # Hot-reload: pendaftaran server baru langsung dikenali supervisor.
            self.refresh()
            for name in self.names:
                if not self.is_alive(name):
                    self.start(name)
            self.heartbeat()
            time.sleep(self.interval)
