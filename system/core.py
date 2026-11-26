# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Inti sistem: mengumpulkan seluruh data yang tersedia menjadi satu snapshot."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(WORKSPACE))

from security.privacy import has_signature  # noqa: E402


def _field(text: str, label: str) -> str:
    """Ambil nilai dari baris tabel markdown ``| Label | Nilai |``."""
    match = re.search(
        rf"\|\s*{re.escape(label)}\s*\|\s*([^|]+?)\s*\|", text
    )
    if not match:
        return ""
    return match.group(1).strip().strip("*").strip("`").strip()


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


class ComputerSystem:
    """Sumber kebenaran tunggal untuk seluruh data sistem."""

    def identity(self) -> dict[str, str]:
        text = _read(WORKSPACE / "surat-kuasa-tandatangan.md")
        return {
            "nama": _field(text, "Nama") or "Tomi vier",
            "jabatan": _field(text, "Jabatan") or "Owner / CEO",
            "email": _field(text, "Email"),
            "telepon": _field(text, "Nomor HP"),
            "tanggal_lahir": _field(text, "Tanggal lahir"),
            "tempat": _field(text, "Tempat"),
            "tanda_tangan": _field(text, "Tanda tangan digital"),
        }

    def license(self) -> dict[str, str]:
        text = _read(WORKSPACE / "LICENSE")
        identity = re.search(r"Identitas lisensi\s*:\s*(\S+)", text)
        version = re.search(r"Versi\s*:\s*([^\n]+)", text)
        owner = re.search(r"Pemilik\s*:\s*([^\n]+)", text)
        return {
            "identitas": identity.group(1) if identity else "Tom05ivier-commits",
            "versi": version.group(1).strip() if version else "1.0",
            "pemilik": owner.group(1).strip() if owner else "Tomi vier",
            "status": "draf" if "DRAF" in text else "final",
        }

    def authorization(self) -> dict[str, Any]:
        letter = _read(WORKSPACE / "surat-izin-keamanan.md")
        power = _read(WORKSPACE / "surat-kuasa-tandatangan.md")
        return {
            "surat_izin": (WORKSPACE / "surat-izin-keamanan.md").exists(),
            "surat_kuasa": (WORKSPACE / "surat-kuasa-tandatangan.md").exists(),
            "nomor_izin": "IT-AGENTY/SEC/2026/11-19" if "SEC/2026" in letter else "",
            "nomor_kuasa": (
                "IT-AGENTY/KUASA/2026/11-19" if "KUASA/2026" in power else ""
            ),
            "bertanda_tangan": has_signature(letter) and has_signature(power),
            "berlaku": "2026-11-19 s.d. 2027-12-31",
        }

    def environment(self) -> dict[str, Any]:
        profile = WORKSPACE / "config" / "profile.d"
        scripts = sorted(p.name for p in profile.glob("*.sh")) if profile.exists() else []
        rgb = WORKSPACE / "config" / "X11" / "rgb.txt"
        lines = len(_read(rgb).splitlines()) if rgb.exists() else 0
        return {
            "profile_scripts": scripts,
            "jumlah_script": len(scripts),
            "rgb_colors": lines,
            "sitecustomize": (WORKSPACE / "sitecustomize.py").exists(),
        }

    def security(self) -> dict[str, Any]:
        from security.blue.policy import FirewallPolicy
        from security.common.config import SECURITY_ROOT

        reports_dir = SECURITY_ROOT / "reports"
        reports = (
            sorted(p.name for p in reports_dir.glob("*.json"))
            if reports_dir.exists()
            else []
        )
        verification: dict[str, Any] = {}
        path = reports_dir / "verification.json"
        if path.exists():
            try:
                verification = json.loads(_read(path))
            except json.JSONDecodeError:
                verification = {}
        from security.blue.integrity import IntegrityMonitor

        integrity = IntegrityMonitor().check()
        policy = FirewallPolicy()
        policy_summary = policy.summary()
        policy_summary["daftar_ip_diblokir"] = policy.rules["blocked_ips"]
        policy_summary["daftar_port_ditolak"] = policy.rules["denied_ports"]
        return {
            "firewall_policy": policy_summary,
            "integritas": integrity,
            "laporan": reports,
            "verifikasi": verification.get("status", "tidak ada"),
            "verifikasi_pass": verification.get("summary", {}).get("pass", 0),
        }

    def files(self) -> dict[str, int]:
        """Hitung berkas proyek tanpa menyusuri sumber pihak ketiga."""
        import os

        suffixes = (".py", ".md", ".sh", ".html", ".css", ".js", ".json", ".txt")
        counts: dict[str, int] = {suffix: 0 for suffix in suffixes}
        excluded = {"src", "opencode-src", "quarantine", "logs", "reports", "__pycache__"}
        for root, dirs, files in os.walk(WORKSPACE):
            dirs[:] = [d for d in dirs if d not in excluded]
            for name in files:
                for suffix in suffixes:
                    if name.endswith(suffix):
                        counts[suffix] += 1
                        break
        return counts

    def advanced(self) -> dict[str, Any]:
        """Status Advanced Computer & knowledge base."""
        from advanced.knowledge import KnowledgeBase

        kb = KnowledgeBase(self._root()).stats()
        memory = WORKSPACE / "advanced" / "memory.jsonl"
        records = 0
        if memory.exists():
            records = sum(
                1 for line in memory.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        return {"dokumen": kb["documents"], "memori": records}

    @staticmethod
    def _root() -> Path:
        return WORKSPACE

    def campaign(self) -> dict[str, Any]:
        """Ringkasan hasil kampanye terakhir."""
        from security.common.config import SECURITY_ROOT

        path = SECURITY_ROOT / "reports" / "campaign.json"
        empty = {"ada": False, "status": "belum dijalankan", "siklus": 0, "skor_risiko": 0}
        if not path.exists():
            return empty
        try:
            data = json.loads(_read(path))
        except json.JSONDecodeError:
            return dict(empty, ada=True, status="invalid")
        return {
            "ada": True,
            "status": data.get("status", "unknown"),
            "siklus": len(data.get("cycles", [])),
            "skor_risiko": data.get("risk_score", 0),
        }

    def agent(self) -> dict[str, Any]:
        """Status runtime Agent Computer."""
        path = WORKSPACE / "agent" / "state.json"
        if not path.exists():
            return {"aktif": False, "jalankan": 0, "status_terakhir": "belum ada"}
        try:
            data = json.loads(_read(path))
        except json.JSONDecodeError:
            return {"aktif": False, "jalankan": 0, "status_terakhir": "invalid"}
        return {
            "aktif": True,
            "jalankan": len(data.get("runs", [])),
            "status_terakhir": data.get("last_status", "unknown"),
        }

    def snapshot(self) -> dict[str, Any]:
        """Snapshot lengkap seluruh subsistem."""
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sistem": "IT Agenty — Infinity Computer System",
            "versi": __import__("system").__version__,
            "identitas": self.identity(),
            "lisensi": self.license(),
            "otorisasi": self.authorization(),
            "lingkungan": self.environment(),
            "keamanan": self.security(),
            "agen": self.agent(),
            "kampanye": self.campaign(),
            "advanced": self.advanced(),
            "berkas": self.files(),
        }
