# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Supervisor lokal: pemantau kesehatan agen & server, dengan audit & restart aman.

Tanpa eskalasi permsisi, tanpa ekstra akses, tanpa network eksternal. Aktif kemungkinan minimal → pemeriksaan proses/heartbeat (read-only).

Jalur pakai: python3 system/agent_manager.py — atau AGENTS agent-manager.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AGENTS_DIR = Path("/root/.config/opencode/agents")
HEARTBEAT = ROOT / "system" / "reports" / "heartbeat.json"
AUDIT = ROOT / "security" / "reports" / "agent_manager.jsonl"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"


def _audit(action: str, **fields: Any) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat(),
        "action": action, "license": LICENSE, "owner": OWNER, **fields}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def list_agents() -> list[dict[str, Any]]:
    """Daftar agen (dari dir konfig) dengan cuplikan status proses."""
    names: set[str] = set()
    if AGENTS_DIR.is_dir():
        names |= {p.stem for p in AGENTS_DIR.glob("*.md") if p.stem}
    from system.hy4_manager import AGENTS
    names |= set(AGENTS.keys())
    out = []
    for name in sorted(names):
        hb = _proc_alive(name)
        out.append({"name": name, "alive": hb, "source": "agent-manager"})
    return out


def _proc_alive(name: str) -> bool:
    """Check proses agen: pattern nama di ps (tanpa nyambil token)."""
    try:
        r = subprocess.run(
            ["bash", "-c", f"ps -eo args | grep -c '[ {name} ].{name}.' || true"],
            capture_output=True, text=True, timeout=10)
        return bool(r.stdout.strip() and int(r.stdout.strip()) >= 1)
    except Exception:
        return False


def check_health(name: str) -> dict[str, Any]:
    return {"name": name, "alive": _proc_alive(name),
            "license": LICENSE, "owner": OWNER}


def force_restart(name: str) -> dict[str, Any]:
    r = subprocess.run(
        ["bash", "-c", f"pkill -f '{name}' 2>/dev/null; true"],
        capture_output=True, text=True, timeout=30)
    _audit("force_restart", target=name, exit=r.returncode)
    return {"action": "restart_requested", "target": name,
            "status": "issued", "license": LICENSE}


def export_config() -> dict[str, Any]:
    d = AGENTS_DIR if AGENTS_DIR.is_dir() else Path(".")
    files = sorted(p.name for p in d.glob("*.md")) if d.exists() else []
    return {"dir": str(d), "agents": files, "license": LICENSE, "owner": OWNER}


def supervisor_loop(interval: float = 30.0, once: bool = False) -> dict[str, Any]:
    """Pengawas: catat per-detik status agen ke audit (read-only)."""
    _audit("supervisor_start", interval=interval)
    while True:
        for a in list_agents():
            _audit("scan", agent=a["name"], alive=a["alive"])
        if once:
            break
        import time
        time.sleep(interval)
    _audit("supervisor_stop")
    return {"status": "OK", "license": LICENSE, "owner": OWNER}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Supervisor lokal agen IT Agenty")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("check")
    p.add_argument("name")
    sub.add_parser("restart")
    sub.add_parser("export")
    sub.add_parser("supervise")
    args = ap.parse_args()
    out = {
        "list": list_agents,
        "check": lambda: check_health(args.name),
        "restart": lambda: force_restart(args.name),
        "export": export_config,
    }.get(args.cmd)()
    if args.cmd == "supervise":
        out = supervisor_loop(once=True)
    import json
    print(json.dumps(out, indent=2, ensure_ascii=False))
