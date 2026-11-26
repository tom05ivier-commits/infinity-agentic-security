# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Telemetri hardware lokal untuk mengukur dampak serangan serius.

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any


def _read_first(path: str) -> str:
    try:
        return Path(path).read_text().splitlines()[0]
    except (OSError, IndexError):
        return ""


def cpu_snapshot() -> dict[str, int]:
    """Ambil hitungan jiffies CPU dari /proc/stat (baris pertama)."""
    line = _read_first("/proc/stat")
    if not line.startswith("cpu "):
        return {}
    parts = line.split()[1:]
    try:
        values = [int(part) for part in parts[:8]]
    except ValueError:
        return {}
    keys = ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal")
    return dict(zip(keys, values))


def memory_snapshot() -> dict[str, int]:
    """Ambil MemTotal/MemAvailable dari /proc/meminfo (satuan kB)."""
    result: dict[str, int] = {}
    try:
        lines = Path("/proc/meminfo").read_text().splitlines()
    except OSError:
        return result
    for line in lines:
        if line.startswith(("MemTotal:", "MemAvailable:")):
            key, value = line.split(":", 1)
            try:
                result[key.strip()] = int(value.strip().split()[0])
            except (ValueError, IndexError):
                continue
    return result


def disk_snapshot(path: str | Path) -> dict[str, int]:
    """Gunakan ruang disk pada path yang diberikan."""
    try:
        usage = shutil.disk_usage(path)
    except OSError:
        return {}
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
    }


def capture(path: str | Path) -> dict[str, Any]:
    """Ambil satu snapshot telemetri lengkap."""
    return {
        "timestamp": time.time(),
        "cpu": cpu_snapshot(),
        "memory": memory_snapshot(),
        "disk": disk_snapshot(path),
    }


def diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Hitung perubahan antar dua snapshot."""
    before_cpu = before.get("cpu", {})
    after_cpu = after.get("cpu", {})
    before_mem = before.get("memory", {})
    after_mem = after.get("memory", {})
    before_disk = before.get("disk", {})
    after_disk = after.get("disk", {})

    cpu_delta: dict[str, int] = {}
    for key in set(before_cpu) | set(after_cpu):
        cpu_delta[key] = after_cpu.get(key, 0) - before_cpu.get(key, 0)

    active_before = sum(
        v for k, v in before_cpu.items() if k != "idle"
    )
    active_after = sum(v for k, v in after_cpu.items() if k != "idle")
    elapsed = max(after.get("timestamp", 0) - before.get("timestamp", 0), 0.001)

    return {
        "elapsed_seconds": round(elapsed, 3),
        "cpu_delta": cpu_delta,
        "cpu_active_delta": active_after - active_before,
        "cpu_active_rate_per_sec": round(
            (active_after - active_before) / elapsed, 1
        ),
        "memory_available_delta_kb": (
            after_mem.get("MemAvailable", 0) - before_mem.get("MemAvailable", 0)
        ),
        "disk_used_delta": after_disk.get("used", 0) - before_disk.get("used", 0),
    }
