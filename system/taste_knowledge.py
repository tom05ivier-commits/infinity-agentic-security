# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengetahuan rasa untuk lapisan indra kognitif (simbolik, read-only).

Ini BUKAN sensor lidah, bukan pengukur kimia, bukan data medis, dan bukan
data pribadi. Lima kategori rasa dipakai sebagai kosakata penalaran agar
lapisan indra memiliki "pengetahuan rasa" tanpa mengklaim kemampuan biologis.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONFIG = ROOT / "config" / "taste_knowledge.json"


def load() -> dict[str, Any]:
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def categories() -> tuple[str, ...]:
    data = load()
    items = data.get("categories", [])
    return tuple(
        str(item.get("id", "")) for item in items
        if isinstance(item, dict) and item.get("id")
    )


def describe() -> dict[str, Any]:
    """ Ringkasan pengetahuan rasa tanpa isi sensitif. """
    data = load()
    return {
        "sumber": "config/taste_knowledge.json",
        "schema": data.get("schema", "tom05-taste-knowledge/1"),
        "sensor": bool(data.get("sensor", False)),
        "jenis_sumber": data.get("source_kind", "symbolic-knowledge"),
        "kategori": list(categories()),
        "jumlah_kategori": len(categories()),
        "batasan": list(data.get("batasan", [])),
        "catatan": (
            "Pengetahuan rasa bersifat simbolik; tidak ada sensor kimia yang "
            "terhubung dan tidak ada data subjek yang disimpan."
        ),
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }


if __name__ == "__main__":
    print(json.dumps(describe(), indent=2, ensure_ascii=False))
