# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Status koneksi OpenCode/tom05 — read-only, tanpa kredensial."""

from __future__ import annotations

import json
import socket
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "tom05-connections.json"


def _http(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.status == 200
    except Exception:
        return False


def _tcp(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def check() -> dict[str, Any]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    results: dict[str, Any] = {}
    for name, endpoint in data["endpoints"].items():
        url = endpoint["url"] + endpoint.get("health", "/")
        http_ok = _http(url)
        default_port = int(url.split(":", 2)[2].split("/")[0]) if "://" in url else 80
        tcp_ok = _tcp(
            endpoint.get("host", "127.0.0.1"),
            int(endpoint.get("port", default_port)),
        )
        # Penanda eksplisit dari konfigurasi mengalahkan hasil probe HTTP:
        # kandidat dengan protokol belum dikenal tidak boleh dilaporkan
        # "terhubung" hanya karena satu health check sesaat berhasil.
        ditandai_mati = endpoint.get("status") == "tidak_terhubung"
        results[name] = {
            "role": endpoint.get("role"),
            "http": http_ok,
            "tcp": tcp_ok,
            "terhubung": http_ok and not ditandai_mati,
        }
        if ditandai_mati:
            results[name]["alasan"] = endpoint.get("alasan")
    aktif = [n for n, v in results.items() if v["terhubung"]]
    return {
        "status": "TERHUBUNG" if len(aktif) >= 3 else "SEBAGIAN",
        "terhubung": aktif,
        "endpoint": results,
        "catatan": (
            "Pemeriksaan tanpa kredensial: tidak ada kredensial yang dibaca "
            "atau dikirim; hanya health check lokal."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(check(), indent=2, ensure_ascii=False))
