# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Penilaian efikasi pertahanan setelah kampanye serangan berulang.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common.config import SECURITY_ROOT

CAMPAIGN = SECURITY_ROOT / "reports" / "campaign.json"
OUTPUT = SECURITY_ROOT / "reports" / "efficacy.json"


def _check_cycle(cycle: dict[str, Any]) -> dict[str, Any]:
    attack = cycle.get("attack", {})
    debug = cycle.get("debug", {})
    findings = attack.get("findings", [])
    checks = {
        "serangan_terdeteksi": bool(findings),
        "serangan_serius": len(findings) >= 4,
        "telemetri_tercatat": bool(attack.get("metadata", {}).get("telemetry")),
        "integritas_terpantau": "integrity" in debug,
        "kebijakan_aktif": bool(debug.get("policy")),
        "mode_terlaporkan": bool(debug.get("capability", {}).get("effective_mode")),
    }
    passed = sum(checks.values())
    return {
        "cycle": cycle.get("cycle"),
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "score": round(100 * passed / len(checks), 1),
    }


def evaluate() -> dict[str, Any]:
    """Nilai kampanye terakhir dan simpan laporan efikasi."""
    if not CAMPAIGN.exists():
        return {
            "status": "BELUM ADA",
            "alasan": "Jalankan: python3 security_cli.py campaign --times 3",
        }
    try:
        campaign = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "INVALID", "alasan": "campaign.json tidak dapat dibaca"}

    cycles = [_check_cycle(item) for item in campaign.get("cycles", [])]
    expected = campaign.get("times", 3)
    average = (
        round(sum(item["score"] for item in cycles) / len(cycles), 1)
        if cycles
        else 0.0
    )
    all_detected = all(item["checks"]["serangan_terdeteksi"] for item in cycles)
    complete = len(cycles) == expected

    report = {
        "status": "EFEKTIF" if all_detected and complete and average >= 80 else "PERLU PERBAIKAN",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "expected_cycles": expected,
        "actual_cycles": len(cycles),
        "deteksi_semua_siklus": all_detected,
        "skor_rata_rata": average,
        "risk_score": campaign.get("risk_score", 0),
        "cycles": cycles,
        "catatan": "Payload simulasi jinak; tidak ada pencurian data.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report["report"] = str(OUTPUT)
    return report
