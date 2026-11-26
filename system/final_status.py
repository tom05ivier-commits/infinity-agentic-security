# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Status final seluruh sistem — agregat read-only, tanpa kredensial."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from system.connection_status import check as connection  # noqa: E402
from system.shared_data import verify as shared  # noqa: E402
from system.infinity_connectivity import check as infinity  # noqa: E402
from system.license_formalization import status as license_status  # noqa: E402

SCORES = (
    ("chip", ROOT / "chip" / "reports" / "chip_score.json"),
    ("security", ROOT / "security" / "reports" / "security_score.json"),
    ("tom05", ROOT / "system" / "reports" / "tom05_score.json"),
    ("device", ROOT / "system" / "reports" / "device_score.json"),
    ("container", ROOT / "system" / "reports" / "container_score.json"),
)


def _score(path: Path) -> tuple[int, str]:
    if not path.is_file():
        return 0, "tidak ada"
    data = json.loads(path.read_text(encoding="utf-8"))
    if "score" in data:
        return int(data["score"]), str(data.get("status", "tidak ada"))
    grade = str(data.get("skor_keamanan", "0/100"))
    value = int(grade.split("/")[0]) if grade.split("/")[0].isdigit() else 0
    status = str(data.get("summary", {}).get("status", "tidak ada"))
    return value, status


def final() -> dict[str, Any]:
    scores = {name: _score(path) for name, path in SCORES}
    total = sum(value[0] for value in scores.values())
    conn = connection()
    sh = shared()
    inf = infinity()
    lic = license_status()
    ok = (
        total == 500
        and conn["status"] == "TERHUBUNG"
        and sh["status"] == "TERHUBUNG"
        and inf["status"] == "TERHUBUNG"
    )
    return {
        "status": "SEMPURNA" if ok else "PERLU_PERBAIKAN",
        "skor_total": f"{total}/500",
        "skor": {k: {"nilai": v[0], "status": v[1]} for k, v in scores.items()},
        "koneksi": conn["status"],
        "data_bersama": sh["status"],
        "konektivitas_infinity": inf["status"],
        "lisensi": lic["status"],
        "catatan": (
            "Lisensi dan draf surat masih belum ditandatangani pemilik; gate teknis tidak "
            "mengubah status otorisasi. Tidak ada kredensial yang dibaca."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(final(), indent=2, ensure_ascii=False))
