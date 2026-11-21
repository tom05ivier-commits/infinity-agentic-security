# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Penerbit izin otomatis untuk tugas operasional rutin (meta-izin).

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .common.config import SECURITY_ROOT
from .privacy import SIGNATURES, has_signature

META_LETTER = SECURITY_ROOT.parent / "surat-persetujuan-otomatis.md"
AUDIT_PATH = SECURITY_ROOT / "reports" / "auto_approvals.jsonl"
SIGNATURE = "(__signature__)"
DEFAULT_TTL = 300

ALLOWED: dict[str, str] = {
    "server-add": "Mendaftarkan server baru ke registry",
    "verify": "Verifikasi kepatuhan",
    "integrity": "Cek/reset integritas",
    "dlp": "Deteksi & karantina paparan data",
    "campaign": "Kampanye serangan laboratorium 3x",
    "debug": "Laporan debugging",
    "efficacy": "Penilaian efikasi",
    "finalize": "Laporan penyelesaian",
    "delivery": "Pengiriman laporan ringkas ke pemilik",
    "config": "Konfigurasi otomatis terbatas sesuai surat izin",
    "host": "Aksi host terbatas sesuai surat izin host",
    "github": "Aksi GitHub terbatas sesuai surat izin GitHub",
    "clone": "Klon ke target dalam Lampiran 1 sesuai surat izin klon otomatis",
}

DENIED = {
    "data-theft",
    "unlimited-auth",
    "third-party-license-removal",
    "external-network-action",
}


class AutoApproval:
    """Menerbitkan izin otomatis terbatas sesuai meta-izin tertulis."""

    def __init__(self) -> None:
        self.valid_meta = META_LETTER.exists() and has_signature(self._read_meta())

    @staticmethod
    def _read_meta() -> str:
        try:
            return META_LETTER.read_text(encoding="utf-8")
        except OSError:
            return ""

    def approve(self, task: str, ttl: int = DEFAULT_TTL) -> dict[str, Any]:
        """Terbitkan izin otomatis bila kategori diizinkan meta-izin."""
        now = datetime.now(timezone.utc)
        record: dict[str, Any] = {
            "id": f"oto-{uuid.uuid4().hex[:10]}",
            "timestamp": now.isoformat(),
            "task": task,
            "signature": SIGNATURE,
            "meta_letter": META_LETTER.name,
            "meta_valid": self.valid_meta,
        }

        if task in DENIED:
            record.update(
                approved=False,
                reason="Kategori dilarang oleh meta-izin; butuh izin tertulis baru.",
            )
        elif task not in ALLOWED:
            record.update(
                approved=False,
                reason="Kategori tidak tercantum dalam meta-izin.",
            )
        elif not self.valid_meta:
            record.update(
                approved=False,
                reason="Surat meta-izin tidak ditemukan atau tidak bertanda tangan.",
            )
        elif ttl > DEFAULT_TTL:
            record.update(
                approved=False,
                reason=(
                    f"Durasi {ttl}s melebihi batas meta-izin ({DEFAULT_TTL}s). "
                    "Izin tanpa batas tidak tersedia."
                ),
            )
        else:
            record.update(
                approved=True,
                scope=ALLOWED[task],
                expires_at=(now + timedelta(seconds=ttl)).isoformat(),
                reason="Izin otomatis diterbitkan sesuai meta-izin tertulis.",
            )

        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    @staticmethod
    def history(limit: int = 10) -> list[dict[str, Any]]:
        if not AUDIT_PATH.exists():
            return []
        records = []
        for line in AUDIT_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records[-limit:]
