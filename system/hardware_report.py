# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Laporan hardware read-only dari perangkat Android lewat skill android-device.

Tidak menyimpan berkas laporan karena data perangkat bisa bersifat pribadi.
Tidak ada kredensial yang dibaca atau dicetak oleh modul ini.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER = Path(
    os.environ.get("OPENCODE_CONFIG_HOME", "/root/.config/opencode")
) / "skills" / "android-device" / "android_device.py"


def _call(action: str) -> dict[str, Any]:
    if not HELPER.is_file():
        return {"success": False, "error": "helper skill android-device tidak ada"}
    try:
        out = subprocess.run(
            ["python3", str(HELPER), action],
            capture_output=True, text=True, timeout=20, cwd=str(ROOT),
        )
        return json.loads(out.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"success": False, "error": type(exc).__name__}


def report() -> dict[str, Any]:
    device = _call("device-info")
    diag = _call("file-diagnostics")
    ok = bool(device.get("success")) and bool(diag.get("success"))
    return {
        "status": "TERHUBUNG" if ok else "PERANGKAT_TIDAK_TERHUBUNG",
        "agent": "hardware",
        "model": "tom05/tom05-flash-free",
        "device": {
            key: device.get(key)
            for key in ("manufacturer", "brand", "model", "sdk_int", "release",
                        "battery_percent")
        },
        "storage_free_bytes": diag.get("storage_free_bytes"),
        "workspace_writable": diag.get("workspace_writable"),
        "gpu_status": "TIDAK_TEREKSPOS",
        "gpu_catatan": (
            "Bridge android-device tidak menyediakan API GPU/Vulkan/NPU. "
            "Pengukuran GPU dilakukan manual lewat WebGPU di browser ponsel; "
            "hasil disalin ke clipboard dan dibaca hanya atas permintaan."
        ),
        "sumber": "system/hardware_report.py",
        "catatan": "Read-only; tidak menyimpan data perangkat; tanpa kredensial.",
        "license": "Tom05ivier-commits-1.0",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, ensure_ascii=False))
