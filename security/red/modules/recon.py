# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Rekonesans perangkat keras/local untuk keperluan inventaris laboratorium.

Hanya membaca informasi sistem yang sudah tersedia publik (platform, CPU,
antarmuka jaringan). Tidak mengumpulkan kredensial atau data sensitif.
"""

from __future__ import annotations

from typing import Any

from ...blue.hardware_agent import HardwareAgent
from ...common.models import Finding, FindingType, ScanResult, Severity


def hardware_recon() -> ScanResult:
    """Kumpulkan peta hardware lokal sebagai dasar pengujian pertahanan."""
    agent = HardwareAgent()
    info = agent.report()
    result = ScanResult(target="localhost:hardware")

    interfaces = info.get("interfaces", [])
    result.scanned_items = len(interfaces) + 1
    for interface in interfaces:
        if interface.get("state") == "up":
            result.findings.append(
                Finding(
                    finding_type=FindingType.OPEN_PORT,
                    severity=Severity.INFO,
                    description=(
                        f"Antarmuka '{interface['name']}' aktif "
                        f"(MAC {interface.get('mac', 'n/a')})"
                    ),
                    location=interface["name"],
                )
            )

    result.findings.append(
        Finding(
            finding_type=FindingType.SUSPICIOUS_ACTIVITY,
            severity=Severity.INFO,
            description=(
                f"Profil sistem: {info['system']['system']} "
                f"{info['system']['release']} / {info['system']['machine']}"
            ),
            location="localhost",
            metadata=info,
        )
    )
    return result
