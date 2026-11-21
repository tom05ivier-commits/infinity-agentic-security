# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Verifikasi kepatuhan objective keamanan.

Memetakan setiap kebutuhan objective menjadi satu pemeriksaan dengan bukti:
 - perlindungan hardware
 - perangkat lunak antivirus
 - agent firewall cyber security
 - debugging
 - serangan malware serius ke hardware
 - lisensi & otorisasi tertulis
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auto_approval import META_LETTER, AutoApproval
from .blue.antivirus_agent import AntivirusAgent
from .blue.defense_agent import DefenseAgent
from .blue.dlp import exposure_report, scan_file
from .blue.integrity import BASELINE_PATH, IntegrityMonitor
from .blue.policy import FirewallPolicy
from .common.authorization import issue_token
from .common.config import EICAR_SIGNATURE, LAB_ROOT, SECURITY_ROOT, ensure_dirs
from .privacy import has_signature
from .red.attack_agent import AttackAgent

OWNER = "Tomi vier"


class ComplianceVerifier:
    """Menjalankan seluruh pemeriksaan dan menghasilkan laporan."""

    def __init__(self) -> None:
        ensure_dirs()
        self.checks: list[dict[str, Any]] = []

    def _add(
        self, name: str, passed: bool, evidence: str, requirement: str
    ) -> None:
        self.checks.append(
            {
                "requirement": requirement,
                "check": name,
                "status": "PASS" if passed else "FAIL",
                "evidence": evidence,
            }
        )

    def check_license(self) -> None:
        license_path = SECURITY_ROOT.parent / "LICENSE"
        text = license_path.read_text(encoding="utf-8") if license_path.exists() else ""
        headers = [
            path
            for path in SECURITY_ROOT.rglob("*.py")
            if "quarantine" not in path.parts
            and "logs" not in path.parts
            and "reports" not in path.parts
        ]
        with_headers = sum(
            1
            for p in headers
            if "Tom05ivier-commits" in p.read_text(errors="ignore")[:400]
        )
        owner_ok = OWNER in text and "Tom05ivier-commits" in text
        self._add(
            "lisensi & pemilik",
            owner_ok and with_headers == len(headers),
            f"owner={OWNER}, header={with_headers}/{len(headers)} file .py",
            "lisensi Tom05ivier-commits atas nama Tomi vier",
        )

    def check_authorization_letter(self) -> None:
        letter = SECURITY_ROOT.parent / "surat-izin-keamanan.md"
        text = letter.read_text(encoding="utf-8") if letter.exists() else ""
        required = (
            "Tomi vier",
            "Owner / CEO",
            "31 Desember 2027",
        )
        # Nilai kontak bisa asli (dokumen lokal) atau tersamar (rilis publik).
        contact_ok = (
            ("000000000000" in text or "000000000000" in text)
            and ("Kota, Provinsi" in text or "Kota, Provinsi" in text)
        )
        attorney = SECURITY_ROOT.parent / "surat-kuasa-tandatangan.md"
        attorney_text = attorney.read_text(encoding="utf-8") if attorney.exists() else ""
        signed = has_signature(text) and has_signature(attorney_text)
        self._add(
            "surat izin & kuasa tanda tangan",
            all(item in text for item in required) and contact_ok and signed,
            f"surat={letter.exists()}, kuasa={attorney.exists()}, "
            f"field={sum(r in text for r in required)}/{len(required)}, "
            f"tanda_tangan={signed}",
            "izin tertulis & kuasa penandatanganan",
        )

    def check_hardware(self) -> None:
        profile = DefenseAgent().hardware.report()
        interfaces = profile.get("interfaces", [])
        self._add(
            "inventaris hardware",
            bool(interfaces),
            f"system={profile['system']['system']}, interfaces={len(interfaces)}",
            "lindungi hardware",
        )

    def check_antivirus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "eicar.bin"
            sample.write_bytes(EICAR_SIGNATURE)
            result = AntivirusAgent().scan_file(sample)
        self._add(
            "deteksi antivirus",
            result.infected,
            f"EICAR terdeteksi={result.infected}, temuan={len(result.findings)}",
            "perangkat lunak antivirus",
        )

    def check_firewall(self) -> None:
        policy = FirewallPolicy()
        policy.deny_port(23)
        decision = policy.evaluate("192.0.2.10", 23)
        self._add(
            "agent firewall",
            decision == "DENY",
            f"mode=userspace-policy, decision tcp/23={decision}, aturan={policy.summary()}",
            "agent cyber security firewall",
        )

    def check_debugging(self) -> None:
        cli = (SECURITY_ROOT / "security_cli.py").read_text(encoding="utf-8")
        available = (
            cli.count('add_parser("debug"') >= 2
            and 'fw_sub.add_parser("policy"' in cli
            and 'add_parser("verify"' in cli
        )
        self._add(
            "debugging",
            available,
            "subcommand: debug, firewall debug, firewall policy, verify",
            "debugging",
        )

    def check_severe_attack(self) -> None:
        token = issue_token(
            token_id="verify",
            issued_by=OWNER,
            allowed_targets=("lab", "127.0.0.1"),
            duration_seconds=120,
        )
        agent = AttackAgent(token)
        result = agent.severe_attack("moderate")
        gated = False
        try:
            AttackAgent().severe_attack("moderate")
        except Exception:  # noqa: BLE001
            gated = True
        self._add(
            "serangan malware serius",
            bool(result.findings) and gated,
            f"temuan={len(result.findings)}, intensitas={result.metadata.get('intensity')}, "
            f"elapsed={result.metadata.get('elapsed_seconds')}s, gating={gated}",
            "lakukan serangan serius dengan malware ke hardware",
        )

    def check_auto_approval(self) -> None:
        valid = AutoApproval().valid_meta
        self._add(
            "izin persetujuan otomatis",
            valid,
            f"meta={META_LETTER.name}, valid={valid}, kategori dibatasi & diaudit",
            "meta-izin otomatis terbatas",
        )

    def check_clone_automation(self) -> None:
        from .clone_actions import CloneActions

        agent = CloneActions()
        self._add(
            "izin klon otomatis",
            agent.letter_valid,
            f"surat= surat-izin-clone-automatis.md, valid={agent.letter_valid}, "
            "target dibatasi & diaudit",
            "persetujuan klon otomatis terbatas",
        )

    def check_dlp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "sample.txt"
            sample.write_text("contact: contoh@domain.test", encoding="utf-8")
            result = scan_file(sample)
        report = exposure_report([result])
        self._add(
            "pencegahan kebocoran data",
            bool(result.findings) and report["total_exposures"] > 0,
            "deteksi paparan aktif; nilai data tidak diekstraksi",
            "lindungi data (bukan mencuri data)",
        )

    def check_integrity(self) -> None:
        monitor = IntegrityMonitor()
        result = monitor.check()
        self._add(
            "pemantauan integritas",
            result["total"] > 0 and BASELINE_PATH.exists(),
            f"baseline={BASELINE_PATH.exists()}, berkas={result['total']}, "
            f"perubahan={result['changed']}",
            "deteksi perubahan berkas akibat serangan",
        )

    def run(self) -> dict[str, Any]:
        for checker in (
            self.check_license,
            self.check_authorization_letter,
            self.check_hardware,
            self.check_antivirus,
            self.check_firewall,
            self.check_debugging,
            self.check_severe_attack,
            self.check_integrity,
            self.check_dlp,
            self.check_auto_approval,
            self.check_clone_automation,
        ):
            checker()
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "owner": OWNER,
            "license": "Tom05ivier-commits-1.0",
            "summary": {
                "pass": sum(c["status"] == "PASS" for c in self.checks),
                "fail": sum(c["status"] == "FAIL" for c in self.checks),
            },
            "status": (
                "COMPLIANT"
                if all(c["status"] == "PASS" for c in self.checks)
                else "NON_COMPLIANT"
            ),
            "checks": self.checks,
        }
        path = SECURITY_ROOT / "reports" / "verification.json"
        path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        report["report"] = str(path)
        return report
