# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Agen pertahanan terpadu untuk melindungi hardware.

Menggabungkan inventaris hardware, firewall, antivirus, dan SOC menjadi
satu alur kerja perlindungan serta respons insiden.
"""

from __future__ import annotations

from pathlib import Path

from ..common.config import LAB_ROOT, ensure_dirs
from ..common.logging import audit, get_logger
from ..common.models import ScanResult, Severity
from .antivirus_agent import AntivirusAgent
from .firewall_agent import FirewallAgent
from .dlp import exposure_report, quarantine_sensitive, scan_paths
from .hardware_agent import HardwareAgent
from .integrity import IntegrityMonitor
from .policy import FirewallPolicy
from .soc_agent import SOCAgent

logger = get_logger("blue.defense")


class DefenseAgent:
    """Fasade pertahanan: lindungi hardware dari malware & ancaman jaringan."""

    def __init__(self, firewall_dry_run: bool = True) -> None:
        ensure_dirs()
        self.hardware = HardwareAgent()
        self.firewall = FirewallAgent(dry_run=firewall_dry_run)
        self.policy = FirewallPolicy()
        self.integrity = IntegrityMonitor()
        self.antivirus = AntivirusAgent()
        self.soc = SOCAgent()

    def protect_hardware(self) -> dict[str, object]:
        """Alur perlindungan hardware: inventaris + aturan firewall + baseline AV."""
        audit(logger, "defense.protect_start")
        profile = self.hardware.report()
        baseline_rules = self.firewall.list_rules()

        # Kebijakan userspace tetap diterapkan walau kernel firewall absen.
        self.policy.deny_port(23)
        self.policy.allow_port(22)
        self.policy.save()
        self.integrity.create_baseline()

        baseline_scan = self.antivirus.scan_directory(LAB_ROOT)
        alerts = self.soc.correlate(baseline_scan)
        report = self.soc.write_report(alerts, "baseline_report.json")

        audit(
            logger,
            "defense.protect_done",
            interfaces=len(profile.get("interfaces", [])),
            firewall_command=baseline_rules.command,
            files_scanned=sum(r.scanned_items for r in baseline_scan),
            risk_score=self.soc.risk_score(alerts),
        )
        return {
            "hardware": profile,
            "firewall": baseline_rules.to_dict(),
            "policy": self.policy.summary(),
            "integrity": self.integrity.check(),
            "dlp": exposure_report(scan_paths([LAB_ROOT])),
            "scan": [r.to_dict() for r in baseline_scan],
            "report": str(report),
            "alerts": [a.to_dict() for a in alerts],
        }

    def respond_to_attack(self, attack_results: list[ScanResult]) -> dict[str, object]:
        """Respons insiden: pindai lab, karantina artefak, blokir IP, laporkan."""
        audit(logger, "defense.incident_start", events=len(attack_results))
        all_targets: list[ScanResult] = list(attack_results)

        # Pindai ulang direktori lab setelah simulasi serangan.
        post_scan = self.antivirus.scan_directory(LAB_ROOT)
        all_targets.extend(post_scan)

        dlp_results = scan_paths([LAB_ROOT])
        dlp_quarantined = quarantine_sensitive(dlp_results)

        integrity = self.integrity.check()
        if integrity["changed"]:
            audit(
                logger,
                "defense.integrity_changed",
                modified=integrity["modified"],
                added=integrity["added"],
            )
        quarantined: list[str] = []
        for result in post_scan:
            if result.infected:
                path = Path(result.target)
                moved = self.antivirus.quarantine(path)
                if moved:
                    quarantined.append(str(moved))

        # Blokir alamat IP mencurigakan yang muncul sebagai pola serangan.
        attacker_ip = "203.0.113.66"  # IP dokumentasi RFC 5737
        blocked = self.firewall.block_ip(attacker_ip)
        self.policy.block_ip(attacker_ip)
        decision = self.policy.evaluate(attacker_ip, 22)
        audit(
            logger,
            "defense.policy_enforced",
            ip=attacker_ip,
            decision=decision,
        )

        alerts = self.soc.correlate(all_targets)
        report = self.soc.write_report(alerts, "incident_report.json")

        audit(
            logger,
            "defense.incident_done",
            quarantined=len(quarantined),
            blocked=blocked.command,
            risk_score=self.soc.risk_score(alerts),
        )
        return {
            "quarantined": quarantined + dlp_quarantined,
            "dlp_quarantined": dlp_quarantined,
            "firewall_block": blocked.to_dict(),
            "policy": self.policy.summary(),
            "policy_decision": decision,
            "integrity": integrity,
            "risk_score": self.soc.risk_score(alerts),
            "report": str(report),
            "alerts": [a.to_dict() for a in alerts],
        }
