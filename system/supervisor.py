# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.1 — lihat file LICENSE di root proyek.
# Supervisor always-on: menjaga semua server tetap berjalan dari registry.

from __future__ import annotations

import json
import os
import signal
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
PID_DIR = ROOT / "system" / "reports" / "supervisor-pids"
MIN_RESTART_INTERVAL = 1.0  # backoff dasar; naik eksponensial sampai 60 detik
MAX_RESTART_INTERVAL = 60.0
STATUS_KEY = "supervisor-status"

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


def validate_services(services: list[dict[str, Any]]) -> list[str]:
    """Periksa registry tanpa mengubahnya."""
    issues: list[str] = []
    seen: set[str] = set()
    for item in services:
        name = str(item.get("name", "")).strip()
        kind = str(item.get("kind", "process"))
        if not name:
            issues.append("ada entri tanpa nama")
        elif name in seen:
            issues.append(f"nama duplikat: {name}")
        seen.add(name)
        if kind not in ("process", "http", "monitor", "tcp"):
            issues.append(f"{name}: kind tidak dikenal ({kind})")
        if kind in ("http", "monitor", "tcp") and not isinstance(item.get("port"), int):
            issues.append(f"{name}: port diperlukan untuk kind {kind}")
        if kind == "process" and not item.get("command"):
            issues.append(f"{name}: command diperlukan untuk kind process")
    return issues


def pid_alive(pid: int) -> bool:
    """Periksa PID tanpa mengirim sinyal apa pun."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def pid_command(pid: int) -> str:
    """Baca cmdline proses lokal; kembalikan string kosong bila tidak ada."""
    if not isinstance(pid, int) or pid <= 0:
        return ""
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return ""
    return raw.replace(b"\0", b" ").decode("utf-8", errors="ignore")


def wrapper_tokens(command: list[str]) -> list[str]:
    """Ubah `bash skrip.sh` menjadi token exec di dalam skrip tersebut.

    Wrapper daemon memakai `exec python3 ...`, jadi cmdline proses akhirnya
    berisi perintah python, bukan `bash` lagi. Tanpa ini adopsi selalu gagal
    dan supervisor membuat proses duplikat saat restart.
    """
    tokens = list(command)
    if not tokens or tokens[0] not in ("bash", "sh", "dash", "/bin/bash", "/bin/sh"):
        return tokens
    if len(tokens) < 2:
        return tokens
    script = Path(tokens[1])
    if not script.is_absolute():
        script = ROOT / script
    try:
        text = script.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return tokens
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("exec "):
            continue
        exec_tokens = [
            part.strip().strip('"\'')
            .replace("$ROOT", str(ROOT))
            .replace("${ROOT}", str(ROOT))
            for part in stripped[5:].split()
            if part.strip() and part.strip() != "\\"
        ]
        if exec_tokens:
            return exec_tokens + tokens[2:]
    return tokens


def command_matches(pid: int, command: list[str]) -> bool:
    """Cocokkan PID hasil adopsi dengan definisi layanan."""
    line = pid_command(pid)
    if not line or not command:
        return False
    lowered = line.lower()
    for token in wrapper_tokens(command):
        if token == "python3":
            if "python3" not in lowered:
                return False
        elif token.lower() not in lowered:
            return False
    return True


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
            code = getattr(response, "status", 200)
            # 401/403 berarti server hidup tetapi butuh auth; 5xx baru gagal.
            return code < 500
    except urllib.error.HTTPError as exc:
        return exc.code < 500
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
        self.adopted: dict[str, int] = {}
        self.restarts: dict[str, int] = {}
        self.failures: dict[str, int] = {}
        self.next_start: dict[str, float] = {}
        self.last_started: dict[str, float] = {}
        self._stop = False
        self._adopt()

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
        return [
            sys.executable if part == "python3" else part
            for part in raw
        ]

    def _pid_file(self, name: str) -> Path:
        return PID_DIR / f"{name}.pid"

    def _write_pid(self, name: str, pid: int) -> None:
        if not isinstance(pid, int) or pid <= 0:
            return
        try:
            PID_DIR.mkdir(parents=True, exist_ok=True)
            target = self._pid_file(name)
            tmp = target.with_suffix(".tmp")
            tmp.write_text(json.dumps({"pid": pid, "name": name}), encoding="utf-8")
            tmp.replace(target)
        except OSError:
            pass

    def _remove_pid(self, name: str) -> None:
        try:
            self._pid_file(name).unlink(missing_ok=True)
        except OSError:
            pass

    def _adopt(self) -> None:
        """Adopsi proses dari PID file/heartbeat agar restart tidak menggandakan."""
        known = set(self.names)
        try:
            files = sorted(PID_DIR.glob("*.pid"))
        except OSError:
            files = []
        for path in files:
            name = path.stem
            if name not in known:
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                pid = int(data.get("pid", 0))
            except (OSError, ValueError, TypeError):
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
                continue
            try:
                matches = self.definition(name).get("kind", "process") == "process"
                matches = matches and command_matches(pid, self.command(name))
            except ValueError:
                matches = False
            if matches and pid_alive(pid):
                self.adopted[name] = pid
                self.last_started[name] = time.monotonic()
            else:
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass

        # Heartbeat lama dipakai bila PID file belum ada (upgrade pertama kali).
        try:
            old = json.loads(HEARTBEAT.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        for name, info in old.get("services", {}).items():
            if name not in known or name in self.adopted:
                continue
            try:
                kind = self.definition(name).get("kind", "process")
            except ValueError:
                continue
            if kind != "process" or not isinstance(info, dict):
                continue
            pid = info.get("pid")
            if pid_alive(pid) and command_matches(pid, self.command(name)):
                self.adopted[name] = pid
                self.last_started[name] = time.monotonic()
                self._write_pid(name, pid)

    def is_alive(self, name: str) -> bool:
        definition = self.definition(name)
        kind = definition.get("kind", "process")
        if kind in ("monitor", "tcp"):
            return port_open(int(definition.get("port", 0)))
        if kind == "http":
            port = int(definition.get("port", 0)) or self.port
            path = str(definition.get("health", "/"))
            if name == "server":
                return server_alive(port)
            return http_alive(port, path)

        adopted = self.adopted.get(name)
        if adopted is not None:
            if pid_alive(adopted):
                started = self.last_started.get(name, 0.0)
                if started and time.monotonic() - started > self.interval * 2:
                    self.failures[name] = 0
                return True
            self.adopted.pop(name, None)
            self._remove_pid(name)

        process = self.processes.get(name)
        if process is not None and process.poll() is None:
            started = self.last_started.get(name, 0.0)
            if started and time.monotonic() - started > self.interval * 2:
                self.failures[name] = 0
            return True
        return False

    def start(self, name: str) -> None:
        kind = self.definition(name).get("kind", "process")
        if kind in ("monitor", "tcp"):
            return  # hanya dipantau, tidak dijalankan supervisor

        now = time.monotonic()
        if now < self.next_start.get(name, 0.0):
            return
        if self.is_alive(name):
            return

        try:
            process = subprocess.Popen(
                self.command(name),
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            self.failures[name] = self.failures.get(name, 0) + 1
            delay = min(
                MAX_RESTART_INTERVAL,
                MIN_RESTART_INTERVAL * (2 ** max(0, self.failures[name] - 1)),
            )
            self.next_start[name] = now + delay
            return

        self.processes[name] = process
        self.restarts[name] = self.restarts.get(name, 0) + 1
        self.failures[name] = self.failures.get(name, 0) + 1
        self.last_started[name] = now
        self._write_pid(name, getattr(process, "pid", 0))
        delay = min(
            MAX_RESTART_INTERVAL,
            MIN_RESTART_INTERVAL * (2 ** max(0, self.failures[name] - 1)),
        )
        self.next_start[name] = now + delay

    def _terminate(self, name: str) -> None:
        """Hentikan proses milik layanan dengan aman."""
        adopted = self.adopted.pop(name, None)
        if adopted is not None and pid_alive(adopted):
            try:
                os.kill(adopted, signal.SIGTERM)
            except OSError:
                pass
        process = self.processes.pop(name, None)
        if process is not None:
            try:
                process.terminate()
                process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    process.kill()
                except OSError:
                    pass
        if adopted is not None:
            for _ in range(10):
                if not pid_alive(adopted):
                    break
                time.sleep(0.1)
            else:
                try:
                    os.kill(adopted, signal.SIGKILL)
                except OSError:
                    pass
        self._remove_pid(name)
        self.restarts.pop(name, None)
        self.failures.pop(name, None)
        self.next_start.pop(name, None)
        self.last_started.pop(name, None)

    def shutdown(self) -> None:
        for name in list(self.processes) + list(self.adopted):
            self._terminate(name)

    def heartbeat(self) -> dict[str, Any]:
        services: dict[str, Any] = {}
        for name in self.names:
            pid = self.adopted.get(name)
            if pid is None:
                pid = getattr(self.processes.get(name), "pid", None)
            services[name] = {"alive": self.is_alive(name), "pid": pid}
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": services,
            "restarts": dict(self.restarts),
            "backoff": {k: round(v - time.monotonic(), 1)
                        for k, v in self.next_start.items()
                        if v > time.monotonic()},
            "issues": validate_services(self.definitions),
            "rule": "selalu jalankan komputer; buat server untuk komponen baru",
            "registry": str(REGISTRY),
        }
        HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
        try:
            PID_DIR.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        tmp = HEARTBEAT.with_suffix(".tmp")
        tmp.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(HEARTBEAT)
        return status

    def status(self) -> dict[str, Any]:
        """Laporan read-only untuk CLI; tidak memulai/mematikan proses."""
        issues = validate_services(self.definitions)
        try:
            last = json.loads(HEARTBEAT.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            last = {}
        recorded = last.get("services", {})
        if not isinstance(recorded, dict):
            recorded = {}
        alive: list[str] = []
        for name in self.names:
            if self.is_alive(name):
                alive.append(name)
                continue
            # Instance status berbeda dengan supervisor yang berjalan, jadi
            # proses anaknya tak terlihat di self.processes. Percayakan PID
            # dari heartbeat bila masih hidup dan ada di registry.
            info = recorded.get(name)
            pid = info.get("pid") if isinstance(info, dict) else None
            kind = self.definition(name).get("kind", "process")
            if kind == "process" and pid_alive(pid) and command_matches(
                pid, self.command(name)
            ):
                alive.append(name)
        return {
            STATUS_KEY: "OK" if not issues else "PERLU_PERBAIKAN",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "layanan": len(self.definitions),
            "hidup": len(alive),
            "mati": [name for name in self.names if name not in alive],
            "adopsi": dict(self.adopted),
            "restarts": dict(self.restarts),
            "masalah": issues,
            "heartbeat": last.get("timestamp"),
        }

    def refresh(self) -> None:
        """Baca ulang registry agar layanan baru otomatis dijalankan."""
        self.definitions = load_services()
        active = set(self.names)
        for name in list(self.processes):
            if name not in active:
                self._terminate(name)
        for name in list(self.adopted):
            if name not in active:
                self._terminate(name)
        try:
            for path in PID_DIR.glob("*.pid"):
                if path.stem not in active:
                    path.unlink(missing_ok=True)
        except OSError:
            pass

    def _request_stop(self, *_: Any) -> None:
        self._stop = True

    def run(self) -> None:
        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                signal.signal(sig, self._request_stop)
            except (OSError, ValueError):
                pass
        try:
            while not self._stop:
                self.refresh()
                for name in self.names:
                    if not self.is_alive(name):
                        self.start(name)
                self.heartbeat()
                time.sleep(self.interval)
        finally:
            self.shutdown()
            self.heartbeat()
