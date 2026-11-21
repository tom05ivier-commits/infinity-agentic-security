# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Daftar & pengecekan aksi host yang diizinkan (tidak menjalankan langsung).

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auto_approval import AutoApproval
from .privacy import has_signature

ROOT = Path(__file__).resolve().parents[1]
LETTER = ROOT / "surat-izin-host.md"
AUDIT = ROOT / "security" / "reports" / "host_actions.jsonl"
SIGNATURE = "(__signature__)"

ALLOWED: dict[str, dict[str, str]] = {
    "capbnd": {
        "command": "bash security/firewall/setup-capbnd.sh",
        "purpose": "Mengisi CapBnd dengan CAP_NET_ADMIN via systemd",
    },
    "firewall": {
        "command": "bash security/firewall/install-net-admin.sh",
        "purpose": "Menerapkan aturan firewall kernel",
    },
    "docker": {
        "command": "docker run --cap-add=NET_ADMIN --network host ...",
        "purpose": "Menjalankan kontainer dengan capability",
    },
    "publish": {
        "command": "bash push_github.sh",
        "purpose": "Mempublikasikan repo dengan GITHUB_TOKEN",
    },
    "systemd": {
        "command": "sudo systemctl enable --now infinity-security",
        "purpose": "Mengaktifkan unit systemd",
    },
}

DENIED_EXAMPLES = (
    "rm -rf /",
    "passwd",
    "export data pribadi",
    "mematikan firewall",
)


class HostActions:
    """Mengelola izin dan jejak aksi host."""

    def __init__(self) -> None:
        self.valid_letter = LETTER.exists() and has_signature(self._read())

    @staticmethod
    def _read() -> str:
        try:
            return LETTER.read_text(encoding="utf-8")
        except OSError:
            return ""

    @staticmethod
    def allowlist() -> dict[str, dict[str, str]]:
        return ALLOWED

    def authorize(self, action: str) -> dict[str, Any]:
        """Verifikasi izin tanpa menjalankan perintah apa pun."""
        approval = AutoApproval().approve("host")
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "letter": LETTER.name,
            "letter_valid": self.valid_letter,
            "approval_id": approval["id"],
            "signature": SIGNATURE,
        }
        if not self.valid_letter:
            record.update(status="DITOLAK", reason="Surat izin host tidak valid.")
        elif not approval["approved"]:
            record.update(status="DITOLAK", reason=approval["reason"])
        elif action not in ALLOWED:
            record.update(status="DITOLAK", reason="Aksi tidak ada dalam Lampiran 1.")
        else:
            record.update(
                status="DIIZINKAN",
                command=ALLOWED[action]["command"],
                purpose=ALLOWED[action]["purpose"],
                note="Jalankan dari host; sistem ini hanya memberi izin & audit.",
            )
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    @staticmethod
    def readiness() -> dict[str, Any]:
        """Laporkan kesiapan host tanpa menampilkan kredensial."""
        from .blue.capabilities import has_cap_net_admin

        return {
            "docker_cli": shutil.which("docker") is not None,
            "docker_daemon": Path("/var/run/docker.sock").exists(),
            "systemd": Path("/run/systemd/system").exists(),
            "github_token": bool(os.environ.get("GITHUB_TOKEN")),
            "cap_net_admin": has_cap_net_admin(),
        }
