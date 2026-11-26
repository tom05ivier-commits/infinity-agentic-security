# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Alur kerja cari bug & uji coba chip firewall.

1. Verifikasi exhaustif RTL vs model referensi.
2. Mutation testing: suntik 4 bug ke salinan RTL, pastikan terdeteksi.
3. Tulis laporan chip/reports/firewall_chip.json.
Exit 0 hanya bila verifikasi PASS dan semua mutan terdeteksi.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip.firewall_reference import SPECS, load_rtl, verify  # noqa: E402

MODE = os.environ.get("AGENTY_FIREWALL_MODE", "strict").strip().lower()
REPORT_NAME = os.environ.get("AGENTY_FIREWALL_REPORT", "firewall_chip").strip()
try:
    MAX_MUTANT_LOOSES = int(os.environ.get("AGENTY_FIREWALL_MAX_MUTANT_LOOSES", "0"))
except ValueError:
    MAX_MUTANT_LOOSES = 0
REPORT = ROOT / "chip" / "reports" / f"{REPORT_NAME}.json"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"

# (nama modul, teks asli, pengganti) — 4 mutan: flip operator logika.
MUTATIONS: list[tuple[str, str, str]] = [
    ("firewall_match", "& ~(p3 ^ r3)", "| ~(p3 ^ r3)"),
    ("firewall_match", "& enable", "& ~enable"),
    ("firewall_decide", "assign decision = allow_hit & ~deny_hit;",
     "assign decision = allow_hit | ~deny_hit;"),
    ("firewall_decide", "& deny_en", "| deny_en"),
]


def run() -> dict[str, Any]:
    results = [verify(name) for name in SPECS]
    verified = all(r["status"] == "PASS" for r in results)

    mutants: list[dict[str, Any]] = []
    for name, old, new in MUTATIONS:
        text = load_rtl(name)
        if old not in text:
            mutants.append({"module": name, "patch": old, "status": "SKIP",
                            "detected": False, "reason": "polakah tidak ditemukan"})
            continue
        mutated = text.replace(old, new, 1)
        result = verify(name, rtl_text=mutated)
        detected = result["status"] == "FAIL"
        mutants.append({
            "module": name,
            "patch": old,
            "status": "TERDETEKSI" if detected else "LOLOS",
            "detected": detected,
            "mismatches": result["mismatches"],
        })

    lolos = sum(1 for m in mutants if not m["detected"])
    all_detected = lolos <= MAX_MUTANT_LOOSES and len(mutants) == len(MUTATIONS)
    status = "PASS" if verified and all_detected else "FAIL"
    report = {
        "status": status,
        "verifikasi": {
            "lolos": verified,
            "modul": len(results),
            "vektor": sum(r["vectors"] for r in results),
            "results": results,
        },
        "mutation_testing": {
            "total": len(MUTATIONS),
            "terdeteksi": sum(1 for m in mutants if m["detected"]),
            "mutants": mutants,
            "catatan": "Bug disuntik ke salinan RTL; lolos berarti celah verifikasi.",
        },
        "batas": "Prototype 4-bit; bukan pengganti firewall kernel (CapBnd=0).",
        "license": LICENSE,
        "owner": OWNER,
    }
    if MODE != "observe":  # mode observe = tidak menulis laporan
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> int:
    report = run()
    print(json.dumps({
        "status": report["status"],
        "vektor": report["verifikasi"]["vektor"],
        "mutan_terdeteksi": report["mutation_testing"]["terdeteksi"],
        "mutan_total": report["mutation_testing"]["total"],
        "mode": MODE,
        "laporan": str(REPORT.relative_to(ROOT)) if MODE != "observe" else "(observe: tidak ditulis)",
    }, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
