# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Alur pengukuran GPU ponsel lewat halaman WebGPU mandiri.

Halaman dibagikan ke perangkat (share sheet). Pengguna menjalankannya sendiri,
menyalin hasilnya ke clipboard, lalu `tom05 --gpu-result` membaca clipboard.
Modul ini hanya menerima berkas yang memuat penanda `tom05-webgpu`; isi clipboard
lain tidak pernah ditampilkan.
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
PAGE = "site/hardware/gpu.html"
MARKER = "tom05-webgpu"


def _call(*args: str) -> dict[str, Any]:
    if not HELPER.is_file():
        return {"success": False, "error": "helper skill android-device tidak ada"}
    try:
        out = subprocess.run(
            ["python3", str(HELPER), *args],
            capture_output=True, text=True, timeout=45, cwd=str(ROOT),
        )
        return json.loads(out.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"success": False, "error": type(exc).__name__}


def share_page() -> dict[str, Any]:
    """Bagikan halaman WebGPU ke perangkat lewat share sheet Android."""
    if not (ROOT / PAGE).is_file():
        return {"status": "GAGAL", "alasan": "halaman gpu.html tidak ada"}
    res = _call("file-share", "--path", PAGE)
    ok = bool(res.get("success"))
    return {
        "status": "TERKIRIM" if ok else "GAGAL",
        "halaman": PAGE,
        "langkah": [
            "Buka berkas yang dibagikan di browser ponsel.",
            "Tekan 'Jalankan pengukuran', lalu 'Salin hasil'.",
            "Kembali ke Tom05 dan jalankan: tom05 --gpu-result",
        ],
        "gpu_status": "PENGUKURAN_MANUAL",
        "detail_perangkat": res if ok else res.get("error"),
    }


def parse_result(text: str) -> dict[str, Any]:
    """Terima hanya JSON dengan penanda tom05-webgpu; jangan tampilkan lainnya."""
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {"status": "CLIPBOARD_BUKAN_HASIL_BENCHMARK"}
    if not isinstance(data, dict) or data.get("benchmark") != MARKER:
        return {"status": "CLIPBOARD_BUKAN_HASIL_BENCHMARK"}
    return {
        "status": data.get("status", "TIDAK_DIKETAHUI"),
        "benchmark": MARKER,
        "adapter": data.get("adapter", {}),
        "limits": data.get("limits", {}),
        "elems": data.get("elems"),
        "iterations": data.get("iterations"),
        "elapsed_ms": data.get("elapsed_ms"),
        "orientation": data.get("orientation"),
        "gpu_backends": data.get("gpu_backends", []),
        "gpu_mode": data.get("gpu_mode"),
        "alasan": data.get("alasan"),
        "catatan": "Hasil yang dilaporkan pengguna; bukan jaminan kapasitas agen.",
    }


def read_result() -> dict[str, Any]:
    res = _call("clipboard-get")
    if not res.get("success"):
        return {"status": "GAGAL", "alasan": res.get("error", "clipboard tidak tersedia")}
    return parse_result(str(res.get("text", "")))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Pengukuran GPU ponsel (manual, aman)")
    ap.add_argument("action", choices=("share", "result"))
    args = ap.parse_args()
    payload = share_page() if args.action == "share" else read_result()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
