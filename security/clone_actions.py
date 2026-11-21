# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Izin & audit klon otomatis (hanya verifikasi, tidak menjalankan git clone).

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auto_approval import AutoApproval
from .privacy import has_signature

ROOT = Path(__file__).resolve().parents[1]
LETTER = ROOT / "surat-izin-clone-automatis.md"
AUDIT = ROOT / "security" / "reports" / "clone_actions.jsonl"
SIGNATURE = "(__signature__)"

# Target klon yang telah disetujui tertulis (Lampiran 1 surat izin).
ALLOWED: dict[str, dict[str, str]] = {
    "opencode-src": {
        "repo": "https://github.com/anomalyco/opencode.git",
        "target": "/root/workspace/opencode-src",
        "flags": "--depth 1 --single-branch",
        "scope": "Sumber OpenCode ke direktori workspace yang ditentukan",
    },
    "chromium-src": {
        "repo": "https://chromium.googlesource.com/chromium/src.git",
        "target": "/root/workspace/src",
        "flags": "--depth 1 --filter=blob:none",
        "scope": "Sumber Chromium ke direktori workspace yang ditentukan",
    },
    "hy4-repo": {
        "repo": "https://github.com/tom05ivier-commits/hy4-agent-model.git",
        "target": "/root/workspace/publish/hy4-agent-model",
        "flags": "--depth 1",
        "scope": "Repo model & agen hy4 ke direktori publikasi",
    },
}

DENIED = {
    "arbitrary-url",
    "third-party-private",
    "license-removal",
    "unlimited-auth",
    "data-theft",
}


class CloneActions:
    """Verifikasi izin klon otomatis & jejak audit — tanpa aksi jaringan."""

    def __init__(self) -> None:
        self.letter_valid = LETTER.exists() and has_signature(self._read_letter())

    @staticmethod
    def _read_letter() -> str:
        try:
            return LETTER.read_text(encoding="utf-8")
        except OSError:
            return ""

    @staticmethod
    def allowlist() -> dict[str, dict[str, str]]:
        return ALLOWED

    def readiness(self) -> dict[str, Any]:
        approval = AutoApproval()
        return {
            "letter": LETTER.name,
            "letter_valid": self.letter_valid,
            "meta_valid": approval.valid_meta,
            "clone_category_allowed": True,
            "targets": sorted(ALLOWED),
            "max_ttl": 300,
        }

    def authorize(self, action: str) -> dict[str, Any]:
        """Verifikasi persetujuan klon; tidak menjalankan perintah apa pun."""
        approval = AutoApproval().approve("clone")
        spec = ALLOWED.get(action, {})
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "letter": LETTER.name,
            "letter_valid": self.letter_valid,
            "approval_id": approval["id"],
            "approval_approved": approval["approved"],
            "signature": SIGNATURE,
        }

        if not self.letter_valid:
            record.update(status="DITOLAK", reason="Surat izin klon otomatis tidak valid.")
        elif action in DENIED:
            record.update(status="DITOLAK", reason="Aksi dilarang oleh surat izin.")
        elif not spec:
            record.update(status="DITOLAK", reason="Target tidak dalam Lampiran 1.")
        elif not approval["approved"]:
            record.update(status="DITOLAK", reason=approval["reason"])
        else:
            record.update(
                status="DIIZINKAN",
                scope=spec["scope"],
                repo=spec["repo"],
                target=spec["target"],
                flags=spec["flags"],
                command=f"git clone {spec['flags']} {spec['repo']} {spec['target']}",
                expires_at=approval.get("expires_at"),
                note="Izin diverifikasi & diaudit; eksekusi clone dilakukan operator.",
            )

        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    @staticmethod
    def history(limit: int = 10) -> list[dict[str, Any]]:
        if not AUDIT.exists():
            return []
        records: list[dict[str, Any]] = []
        for line in AUDIT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records[-limit:]
