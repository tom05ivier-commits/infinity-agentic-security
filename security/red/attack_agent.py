# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Agen serangan (red team) dengan pembatasan ketat.

Setiap aksi mensyaratkan token otorisasi yang diterbitkan operator. Target
hanya localhost atau direktori laboratorium. Aksi bersifat simulasi jinak
untuk menguji efektivitas pertahanan.
"""

from __future__ import annotations

from pathlib import Path

from ..common.authorization import (
    AuthorizationError,
    AuthorizationToken,
    require_authorization,
)
from ..common.config import LAB_ROOT
from ..common.logging import audit, get_logger
from ..blue.capabilities import status as capability_status
from ..blue.integrity import IntegrityMonitor
from ..blue.policy import FirewallPolicy
from ..common.models import ScanResult
from .malware import MalwareSimulator
from .modules.recon import hardware_recon
from .modules.scanner import connect_scan, parse_ports, scan_lab_files
from .modules.simulator import weak_config_check
from .modules.stress import hardware_stress
from .modules.telemetry import capture as capture_telemetry
from .modules.telemetry import diff as diff_telemetry

logger = get_logger("red.attack")


class AttackAgent:
    """Orkestrator simulasi serangan pada hardware/lab lokal."""

    def __init__(self, auth_token: AuthorizationToken | None = None) -> None:
        self._auth = auth_token

    def authorize(self, token: AuthorizationToken) -> None:
        """Pasang token otorisasi sebelum menjalankan aksi ofensif."""
        self._auth = token
        audit(
            logger,
            "red.authorized",
            token_id=token.token_id,
            issued_by=token.issued_by,
        )

    @require_authorization
    def recon(self) -> ScanResult:
        """Inventaris hardware lokal (rekonesan jinak)."""
        assert self._auth is not None
        result = hardware_recon()
        audit(logger, "red.recon", findings=len(result.findings))
        return result

    @require_authorization
    def port_scan(self, target: str = "127.0.0.1", ports: str = "22,80,443,8080") -> ScanResult:
        """Pindai port pada target yang diizinkan token."""
        assert self._auth is not None
        resolved = self._auth.require_target(target)
        parsed = parse_ports(ports)
        # Enforcement userspace: aturan policy firewall benar-benar dipatuhi
        # oleh agen walau kernel iptables tidak tersedia (CapBnd = 0).
        policy = FirewallPolicy()
        allowed_ports = [
            port
            for port in parsed
            if policy.evaluate(resolved, port, "tcp") != "DENY"
        ]
        skipped_ports = sorted(set(parsed) - set(allowed_ports))
        if target != "lab":
            result = connect_scan(resolved, allowed_ports)
        else:
            result = scan_lab_files(Path(resolved))
        result.metadata["policy_enforced"] = True
        result.metadata["skipped_ports"] = skipped_ports
        audit(
            logger,
            "red.port_scan",
            target=target,
            ports=len(parsed),
            findings=len(result.findings),
        )
        return result

    @require_authorization
    def malware_attack(self, target: str = "lab") -> ScanResult:
        """Simulasikan serangan malware jinak ke target lab.

        Hanya target 'lab' yang diterima: artefak EICAR dan berkas pola
        mencurigakan ditulis ke direktori laboratorium lokal.
        """
        assert self._auth is not None
        if target != "lab":
            raise AuthorizationError(
                "Serangan malware hanya diizinkan pada target 'lab'."
            )
        resolved = Path(self._auth.require_target(target))
        simulator = MalwareSimulator(resolved)
        eicar = simulator.deploy_eicar()
        sample = simulator.deploy_suspicious_sample()
        combined = ScanResult(target=str(resolved))
        combined.findings = eicar.findings + sample.findings
        combined.scanned_items = 2
        audit(
            logger,
            "red.malware_attack",
            target=str(resolved),
            artifacts=combined.scanned_items,
        )
        return combined

    @require_authorization
    def weak_config_check(self) -> ScanResult:
        """Telusuri konfigurasi lemah di direktori lab."""
        assert self._auth is not None
        resolved = Path(self._auth.require_target("lab"))
        result = weak_config_check(resolved)
        audit(logger, "red.weak_config", findings=len(result.findings))
        return result

    @require_authorization
    def severe_attack(self, intensity: str = "moderate") -> ScanResult:
        """Serangan serius ke hardware lokal: malware + beban CPU/memori/disk/soket."""
        assert self._auth is not None
        resolved = Path(self._auth.require_target("lab"))
        profiles = {
            "light": (0.1, 1, 3, 5),
            "moderate": (0.3, 4, 10, 10),
            "severe": (1.0, 12, 20, 25),
        }
        if intensity not in profiles:
            raise ValueError(f"Intensitas tidak dikenal: {intensity}")
        duration, memory_mb, file_count, socket_count = profiles[intensity]
        before = capture_telemetry(resolved)
        malware = self.malware_attack("lab")
        stress = hardware_stress(
            resolved,
            duration=duration,
            memory_mb=memory_mb,
            file_count=file_count,
            socket_count=socket_count,
        )
        after = capture_telemetry(resolved)
        telemetry = diff_telemetry(before, after)

        combined = ScanResult(target=str(resolved))
        combined.findings = malware.findings + stress.findings
        combined.scanned_items = malware.scanned_items + stress.scanned_items
        combined.metadata = {
            "intensity": intensity,
            **stress.metadata,
            "telemetry": telemetry,
        }
        if telemetry["cpu_active_delta"] > 0:
            from ..common.models import Finding, FindingType, Severity

            combined.findings.append(
                Finding(
                    finding_type=FindingType.SUSPICIOUS_ACTIVITY,
                    severity=Severity.MEDIUM,
                    description=(
                        "Lonjakan aktivitas CPU terukur: "
                        f"{telemetry['cpu_active_delta']} jiffies "
                        f"({telemetry['cpu_active_rate_per_sec']}/dtk)"
                    ),
                    location="cpu",
                    metadata=telemetry,
                )
            )
        audit(
            logger,
            "red.severe_attack",
            intensity=intensity,
            findings=len(combined.findings),
        )
        return combined

    @require_authorization
    def repeated_attack(
        self, times: int = 3, intensity: str = "moderate"
    ) -> list[dict[str, object]]:
        """Ulangi serangan serius ``times`` kali, dengan debug tiap putaran.

        Setiap siklus mencatat: hasil serangan, status capability, policy
        firewall, dan perubahan integritas berkas. Tidak ada ekstraksi data.
        """
        assert self._auth is not None
        times = max(1, min(times, 10))
        integrity = IntegrityMonitor()
        cycles: list[dict[str, object]] = []
        for cycle in range(1, times + 1):
            attack = self.severe_attack(intensity)
            debug = {
                "cycle": cycle,
                "capability": capability_status(),
                "policy": FirewallPolicy().summary(),
                "integrity": integrity.check(),
            }
            cycles.append(
                {
                    "cycle": cycle,
                    "attack": attack.to_dict(),
                    "debug": debug,
                }
            )
            audit(
                logger,
                "red.repeated_attack_cycle",
                cycle=cycle,
                times=times,
                findings=len(attack.findings),
            )
        audit(logger, "red.repeated_attack_done", cycles=len(cycles))
        return cycles

    @require_authorization
    def full_drill(self) -> list[ScanResult]:
        """Jalankan seluruh rangkaian simulasi serangan."""
        assert self._auth is not None
        target = (
            "127.0.0.1"
            if "127.0.0.1" in self._auth.scope.allowed_targets
            else "lab"
        )
        return [
            self.recon(),
            self.port_scan(target, "22,80,443,8080"),
            self.severe_attack("moderate"),
            self.weak_config_check(),
        ]
