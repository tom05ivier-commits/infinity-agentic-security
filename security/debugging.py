# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Laporan debugging pasca-kampanye: before/after + per-siklus.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common.config import SECURITY_ROOT

CAMPAIGN = SECURITY_ROOT / "reports" / "campaign.json"
OUTPUT = SECURITY_ROOT / "reports" / "debug_report.json"


def _diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    b_mode = before.get("capability", {}).get("effective_mode")
    a_mode = after.get("capability", {}).get("effective_mode")
    b_policy = before.get("policy", {})
    a_policy = after.get("policy", {})
    b_integrity = before.get("integrity", {})
    a_integrity = after.get("integrity", {})
    return {
        "mode_sebelum": b_mode,
        "mode_sesudah": a_mode,
        "mode_stabil": b_mode == a_mode,
        "policy_sebelum": b_policy,
        "policy_sesudah": a_policy,
        "policy_stabil": b_policy == a_policy,
        "integritas_sebelum": b_integrity.get("changed"),
        "integritas_sesudah": a_integrity.get("changed"),
        "integritas_berubah": b_integrity.get("changed") != a_integrity.get("changed"),
    }


def report() -> dict[str, Any]:
    """Buat laporan debugging dari campaign terakhir."""
    if not CAMPAIGN.exists():
        return {"status": "BELUM ADA", "alasan": "Jalankan campaign terlebih dahulu"}
    try:
        campaign = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "INVALID"}

    before = campaign.get("debug_before", {})
    after = campaign.get("debug_after", {})
    cycles = campaign.get("cycles", [])
    cycle_debug = [
        {
            "cycle": item.get("cycle"),
            "integrity": item.get("debug", {}).get("integrity"),
            "policy": item.get("debug", {}).get("policy"),
            "mode": item.get("debug", {})
            .get("capability", {})
            .get("effective_mode"),
        }
        for item in cycles
    ]
    diff = _diff(before, after)
    response = campaign.get("response", {})

    stable = diff["mode_stabil"] and diff["policy_stabil"]
    result = {
        "status": "STABIL" if stable else "PERUBAHAN_TERDETEKSI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "siklus": len(cycles),
        "diff": diff,
        "debug_per_siklus": cycle_debug,
        "respons": {
            "dikarantina": len(response.get("quarantined", [])),
            "keputusan_policy": response.get("policy_decision"),
            "skor_risiko": response.get("risk_score"),
        },
        "catatan": "Debugging simulasi; tidak ada pencurian data.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    result["report"] = str(OUTPUT)
    return result
