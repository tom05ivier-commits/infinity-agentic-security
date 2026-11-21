# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Orkestrasi kampanye laboratorium: lindungi → debug → serang 3x → respons.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .blue.capabilities import status as capability_status
from .blue.defense_agent import DefenseAgent
from .blue.integrity import IntegrityMonitor
from .blue.policy import FirewallPolicy
from .blue.soc_agent import SOCAgent
from .common.authorization import issue_token
from .common.config import SECURITY_ROOT
from .common.models import Finding, FindingType, ScanResult, Severity
from .red.attack_agent import AttackAgent


def _debug(label: str) -> dict[str, Any]:
    """Ambil snapshot debugging untuk satu titik kampanye."""
    return {
        "label": label,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "capability": capability_status(),
        "policy": FirewallPolicy().summary(),
        "integrity": IntegrityMonitor().check(),
    }


def run_campaign(times: int = 3, intensity: str = "moderate") -> dict[str, Any]:
    """Jalankan siklus pertahanan + serangan berulang lengkap."""
    defense = DefenseAgent()
    token = issue_token(
        token_id="campaign",
        issued_by="Tomi vier",
        allowed_targets=("lab", "127.0.0.1"),
        duration_seconds=300,
    )
    agent = AttackAgent(token)

    debug_before = _debug("sebelum")
    protection = defense.protect_hardware()
    cycles = agent.repeated_attack(times=times, intensity=intensity)
    debug_after = _debug("sesudah")

    findings: list[ScanResult] = []
    for cycle in cycles:
        raw = cycle["attack"]
        reconstructed = ScanResult(
            target=raw["target"],
            scanned_items=raw.get("scanned_items", 0),
            errors=raw.get("errors", []),
        )
        for item in raw["findings"]:
            reconstructed.findings.append(
                Finding(
                    finding_type=FindingType(item["type"]),
                    severity=Severity(item["severity"]),
                    description=item["description"],
                    location=item.get("location", ""),
                    evidence=item.get("evidence", ""),
                    metadata=item.get("metadata", {}),
                )
            )
        findings.append(reconstructed)

    # Respons insiden: karantina artefak, DLP, blokir IP, dan policy.
    response = defense.respond_to_attack(findings)
    alerts = SOCAgent().correlate(findings)
    report = {
        "status": "SELESAI",
        "times": times,
        "intensity": intensity,
        "debug_before": debug_before,
        "protection": protection,
        "cycles": cycles,
        "debug_after": debug_after,
        "response": response,
        "risk_score": SOCAgent().risk_score(alerts),
        "alerts": [a.to_dict() for a in alerts],
        "catatan": "Serangan adalah simulasi jinak; tidak ada pencurian data.",
    }
    path = SECURITY_ROOT / "reports" / "campaign.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report["report"] = str(path)
    return report
