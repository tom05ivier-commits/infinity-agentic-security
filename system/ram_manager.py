# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""R.A.M. — laporan & perencanaan memori virtual (RAM + swap).

Tidak menambah RAM fisik. Perubahan swap hanya dengan --authorize eksplisit,
maksimal 300 detik untuk jendela eksekusi, dan dicatat di audit proyek.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "security" / "reports" / "ram_actions.jsonl"
SWAPFILE = Path("/tmp/opencode/ram-swapfile")
TARGET_RATIO = 2
MAX_TTL = 300


def _meminfo() -> dict[str, int]:
    values: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        key, _, rest = line.partition(":")
        if key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
            values[key] = int(rest.strip().split()[0])
    return values


def _audit(action: str, **fields: Any) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "action": action, **fields}
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def status() -> dict[str, Any]:
    m = _meminfo()
    total = m.get("MemTotal", 0) + m.get("SwapTotal", 0)
    ratio = round(total / m["MemTotal"], 2) if m.get("MemTotal") else 0
    return {
        "status": "OK",
        "agent": "ram",
        "fisik_kb": m.get("MemTotal", 0),
        "tersedia_kb": m.get("MemAvailable", 0),
        "swap_total_kb": m.get("SwapTotal", 0),
        "swap_bebas_kb": m.get("SwapFree", 0),
        "virtual_total_kb": total,
        "rasio": ratio,
        "target_rasio": TARGET_RATIO,
        "target_tercapai": ratio >= TARGET_RATIO,
        "catatan": "RAM fisik tidak dapat ditambah dari dalam container; angka adalah RAM + swap.",
        "license": "Tom05ivier-commits-1.0",
    }


def plan() -> dict[str, Any]:
    s = status()
    if s["target_tercapai"]:
        return {
            "status": "TIDAK_PERLU",
            "alasan": "memori virtual sudah mencapai atau melebihi 2× RAM fisik",
            "rasio": s["rasio"],
            "target_rasio": TARGET_RATIO,
            "perubahan_diperlukan": False,
        }
    needed = s["fisik_kb"] * TARGET_RATIO - s["virtual_total_kb"]
    return {
        "status": "RENCANA",
        "tambahan_swap_kb": needed,
        "swapfile": str(SWAPFILE),
        "target_rasio": TARGET_RATIO,
        "perubahan_diperlukan": True,
        "peringatan": "Swap lebih lambat dari RAM; ini bukan penambahan RAM fisik.",
        "cara": "tom05 --ram enable --authorize",
    }


def enable(authorize: bool = False, ttl: int = MAX_TTL) -> dict[str, Any]:
    p = plan()
    if not authorize:
        return {"status": "DITOLAK", "alasan": "perlu --authorize eksplisit"}
    if ttl > MAX_TTL:
        return {"status": "DITOLAK", "alasan": f"TTL melebihi {MAX_TTL} detik"}
    if not p["perubahan_diperlukan"]:
        return {"status": "TIDAK_PERLU", "rasio": p["rasio"]}
    if SWAPFILE.exists():
        return {"status": "DITOLAK", "alasan": "swapfile sudah ada; jalankan disable dulu"}
    try:
        SWAPFILE.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["fallocate", "-l", f"{p['tambahan_swap_kb']}K", str(SWAPFILE)],
                       check=True, capture_output=True, timeout=MAX_TTL)
        os.chmod(SWAPFILE, 0o600)
        subprocess.run(["mkswap", str(SWAPFILE)], check=True, capture_output=True, timeout=60)
        subprocess.run(["swapon", str(SWAPFILE)], check=True, capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        SWAPFILE.unlink(missing_ok=True)
        _audit("enable_gagal", error=type(exc).__name__)
        return {"status": "GAGAL", "alasan": type(exc).__name__}
    _audit("enable", swapfile=str(SWAPFILE), ttl=ttl, rasio=status()["rasio"])
    return {"status": "AKTIF", "swapfile": str(SWAPFILE), "rasio": status()["rasio"]}


def disable(authorize: bool = False) -> dict[str, Any]:
    if not authorize:
        return {"status": "DITOLAK", "alasan": "perlu --authorize eksplisit"}
    if not SWAPFILE.exists():
        return {"status": "TIDAK_ADA"}
    try:
        subprocess.run(["swapoff", str(SWAPFILE)], check=True, capture_output=True, timeout=60)
        SWAPFILE.unlink(missing_ok=True)
    except (OSError, subprocess.SubprocessError) as exc:
        _audit("disable_gagal", error=type(exc).__name__)
        return {"status": "GAGAL", "alasan": type(exc).__name__}
    _audit("disable", swapfile=str(SWAPFILE))
    return {"status": "DINONAKTIFKAN"}


def dispatch(action: str = "status", authorize: bool = False) -> dict[str, Any]:
    actions = {
        "status": lambda: status(),
        "plan": lambda: plan(),
        "enable": lambda: enable(authorize),
        "disable": lambda: disable(authorize),
    }
    if action not in actions:
        return {"status": "DITOLAK", "alasan": "aksi tidak dikenal"}
    return actions[action]()


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="R.A.M. — memori virtual")
    ap.add_argument("action", nargs="?", default="status",
                    choices=("status", "plan", "enable", "disable"))
    ap.add_argument("--authorize", action="store_true")
    args = ap.parse_args()
    print(json.dumps(dispatch(args.action, args.authorize), indent=2, ensure_ascii=False))
