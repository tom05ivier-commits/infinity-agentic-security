# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Latar keseimbangan kepentingan dan hak untuk perencana kognitif.

Modul read-only ini membaca kebijakan dari ``config/rights_balance.json``.
Kepentingan operasional dijalankan hanya di dalam batas hak: privasi, lisensi,
izin tertulis yang dapat dicabut, dan audit. Bila kategori dilarang atau aksi
terbatas diminta tanpa izin, keputusan ``hak_mendahului`` digunakan.

Ini kebijakan perangkat lunak, bukan nasihat hukum dan bukan otoritas baru.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONFIG = ROOT / "config" / "rights_balance.json"
RESTRICTED_WORDS = ("drill", "campaign", "serangan", "eksploit", "ofensif")


def load() -> dict[str, Any]:
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def evaluate(goal: str = "status sistem", authorize: bool = False) -> dict[str, Any]:
    """Nilai tujuan terhadap keseimbangan kepentingan dan hak."""
    data = load()
    text = str(goal).lower()
    restricted = any(word in text for word in RESTRICTED_WORDS)
    if restricted and not authorize:
        decision = "hak_mendahului"
        reason = "Aksi terbatas ditolak tanpa izin tertulis; privasi dan batas izin diutamakan."
    elif restricted and authorize:
        decision = "seimbang_terbatas"
        reason = "Izin ada, tetapi tetap tunduk batas waktu dan jejak audit."
    else:
        decision = "seimbang"
        reason = "Kepentingan operasional dijalankan di dalam batas hak."
    limits = data.get("batas", {})
    return {
        "keputusan": decision,
        "alasan": reason,
        "kepentingan": len(data.get("kepentingan", [])) if isinstance(
            data.get("kepentingan", []), list) else 0,
        "hak": len(data.get("hak", [])) if isinstance(data.get("hak", []), list) else 0,
        "prioritas": data.get("prioritas", "hak_mendahului_bila_bertentangan"),
        "ttl_maks_detik": limits.get("ttl_maks_detik", 300),
        "audit": bool(limits.get("audit", True)),
        "izin": bool(authorize),
        "catatan": "Kebijakan perangkat lunak, bukan nasihat hukum atau otoritas baru.",
    }


def check() -> dict[str, Any]:
    """Pastikan kedua sisi kebijakan hadir dan batasnya valid."""
    data = load()
    interests = data.get("kepentingan", [])
    rights = data.get("hak", [])
    limits = data.get("batas", {})
    ttl = limits.get("ttl_maks_detik", 0)
    ok = (
        isinstance(interests, list) and bool(interests)
        and isinstance(rights, list) and bool(rights)
        and isinstance(ttl, int) and 0 < ttl <= 300
        and bool(limits.get("audit"))
        and data.get("prioritas") == "hak_mendahului_bila_bertentangan"
    )
    return {
        "status": "SEIMBANG" if ok else "TIDAK_SEIMBANG",
        "jumlah_kepentingan": len(interests) if isinstance(interests, list) else 0,
        "jumlah_hak": len(rights) if isinstance(rights, list) else 0,
        "ttl_maks_detik": ttl,
        "sumber": "config/rights_balance.json",
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }


def describe() -> dict[str, Any]:
    return {
        "sumber": "config/rights_balance.json",
        "schema": load().get("schema", "tom05-rights-balance/1"),
        "kepentingan": list(load().get("kepentingan", [])),
        "hak": list(load().get("hak", [])),
        "batas": load().get("batas", {}),
        "prioritas": load().get("prioritas", ""),
        "status": check()["status"],
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }


if __name__ == "__main__":
    print(json.dumps({"check": check(), "contoh": evaluate()},
                     indent=2, ensure_ascii=False))
