# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Drul firewall: serangan hardware/software → pertahanan → debug → ulang.

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from security.blue.capabilities import status as capability_status
    from security.blue.defense_agent import DefenseAgent
    from security.blue.integrity import IntegrityMonitor
    from security.blue.policy import FirewallPolicy
    from security.common.authorization import issue_token
    from security.common.config import SECURITY_ROOT
    from security.common.models import ScanResult
    from security.privacy import scan as privacy_scan
    from security.red.attack_agent import AttackAgent
else:
    from .blue.capabilities import status as capability_status
    from .blue.defense_agent import DefenseAgent
    from .blue.integrity import IntegrityMonitor
    from .blue.policy import FirewallPolicy
    from .common.authorization import issue_token
    from .common.config import SECURITY_ROOT
    from .common.models import ScanResult
    from .privacy import scan as privacy_scan  # noqa: F401
    from .red.attack_agent import AttackAgent

REPORTS = SECURITY_ROOT / "reports"
OUTPUT = REPORTS / "firewall_drill.json"
AUDIT = REPORTS / "firewall_drill_cycles.jsonl"
ATTACKER_IP = "203.0.113.66"


def _to_result(raw: dict[str, Any]) -> ScanResult:
    """Rekonstruksi ScanResult dari keluaran attack agent."""
    result = ScanResult(
        target=raw.get("target", ""),
        scanned_items=raw.get("scanned_items", 0),
        errors=raw.get("errors", []),
        metadata=raw.get("metadata", {}),
    )
    if __package__ in (None, ""):
        from security.common.models import Finding, FindingType, Severity
    else:
        from .common.models import Finding, FindingType, Severity

    for item in raw.get("findings", []):
        result.findings.append(
            Finding(
                finding_type=FindingType(item["type"]),
                severity=Severity(item["severity"]),
                description=item.get("description", ""),
                location=item.get("location", ""),
                evidence=item.get("evidence", ""),
                metadata=item.get("metadata", {}),
            )
        )
    return result


def _chip_ok() -> bool:
    """Verifikasi hardware (RTL chip) masih PASS."""
    path = SECURITY_ROOT.parent / "chip" / "reports" / "chip_verification.json"
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return data.get("status") == "PASS" and data.get("modules", 0) >= 5


def _criteria(
    protection: dict[str, Any],
    response: dict[str, Any],
    privacy: dict[str, int],
    remaining_infected: int = 0,
) -> dict[str, bool]:
    """Kriteria firewall berhasil untuk hardware + software."""
    integrity = response.get("integrity", {})
    return {
        "policy_blokir_ip": FirewallPolicy().evaluate(ATTACKER_IP, 22) == "DENY",
        "port_berbahaya_ditolak": "tcp/23" in FirewallPolicy().rules["denied_ports"],
        "software_dikarantina": (
            len(response.get("quarantined", [])) >= 1 or remaining_infected == 0
        ),
        "integritas_terpantau": bool(integrity.get("changed"))
        or bool(protection.get("integrity", {}).get("changed")),
        "hardware_chip_pass": _chip_ok(),
        "privasi_aman": sum(privacy.values()) == 0,
    }


def run_cycle(intensity: str = "moderate") -> dict[str, Any]:
    """Satu siklus serangan + pertahanan + debugging."""
    token = issue_token(
        token_id="firewall-drill",
        issued_by="Tomi vier",
        allowed_targets=("lab", "127.0.0.1"),
        duration_seconds=300,
    )
    attack_agent = AttackAgent(token)
    defense = DefenseAgent()

    protection = defense.protect_hardware()
    recon = attack_agent.recon().to_dict()
    port_scan = attack_agent.port_scan("127.0.0.1", "22,23,65534").to_dict()
    severe = attack_agent.severe_attack(intensity).to_dict()
    weak = attack_agent.weak_config_check().to_dict()

    results = [_to_result(item) for item in (recon, port_scan, severe, weak)]
    response = defense.respond_to_attack(results)

    # Daemon proteksi dapat mengarantina lebih dulu, jadi keberhasilan
    # diukur dari ketiadaan berkas terinfeksi yang tersisa di lab.
    from security.blue.antivirus_agent import AntivirusAgent
    from security.common.config import LAB_ROOT

    remaining_infected = sum(
        1 for scan in AntivirusAgent().scan_directory(LAB_ROOT) if scan.infected
    )

    # Privasi diukur dari rilis publik, bukan surat izin lokal yang memang
    # berisi data pemilik secara sah.
    from system.hy4_auth import scan_public

    privacy_report = scan_public()
    privacy = {"publik_aman": 0 if privacy_report["status"] == "AMAN" else 1}
    criteria = _criteria(protection, response, privacy, remaining_infected)
    debug = {
        "capability": capability_status(),
        "policy": FirewallPolicy().summary(),
        "integrity": response.get("integrity", {}),
        "quarantined": len(response.get("quarantined", [])),
        "remaining_infected": remaining_infected,
        "privacy": privacy,
    }
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "recon": recon,
        "port_scan": port_scan,
        "severe_attack": severe,
        "weak_config": weak,
        "protection": protection,
        "response": response,
        "debug": debug,
        "criteria": criteria,
        "success": all(criteria.values()),
    }


def run_until_success(max_attempts: int = 3, intensity: str = "moderate") -> dict[str, Any]:
    """Ulangi drill sampai semua kriteria firewall terpenuhi."""
    cycles: list[dict[str, Any]] = []
    for attempt in range(1, max(1, max_attempts) + 1):
        cycle = run_cycle(intensity)
        cycle["attempt"] = attempt
        cycles.append(cycle)
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(
                {
                    "attempt": attempt,
                    "success": cycle["success"],
                    "failed": [k for k, v in cycle["criteria"].items() if not v],
                    "timestamp": cycle["timestamp"],
                },
                ensure_ascii=False,
            ) + "\n")
        if cycle["success"]:
            break

    final = cycles[-1]
    report = {
        "status": "BERHASIL" if final["success"] else "GAGAL",
        "attempts": len(cycles),
        "max_attempts": max_attempts,
        "intensity": intensity,
        "criteria": final["criteria"],
        "failed": [k for k, v in final["criteria"].items() if not v],
        "cycles": cycles,
        "license": "Tom05ivier-commits-1.0",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Firewall cyber drill")
    parser.add_argument("--max", type=int, default=3)
    parser.add_argument(
        "--intensity", choices=("light", "moderate", "severe"), default="moderate"
    )
    args = parser.parse_args()
    report = run_until_success(args.max, args.intensity)
    print(json.dumps(
        {
            "status": report["status"],
            "attempts": report["attempts"],
            "criteria": report["criteria"],
            "failed": report["failed"],
            "report": str(OUTPUT),
        },
        indent=2,
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
