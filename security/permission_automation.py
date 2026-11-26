# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Otomatisasi penerbitan surat izin tertulis untuk kategori rutin.

Modul ini TIDAK menciptakan otoritas baru. Ia hanya memakai meta-izin
`surat-persetujuan-otomatis.md` yang sudah ditandatangani, melalui
`security.auto_approval.AutoApproval`. Kategori dilarang, izin tanpa batas,
dan tanda tangan manual baru tetap ditolak.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .auto_approval import ALLOWED, DEFAULT_TTL, DENIED, AutoApproval
from .privacy import has_signature

ROOT = Path(__file__).resolve().parents[1]
LETTERS = ROOT / "security" / "reports" / "auto_permission_letters"
INDEX = ROOT / "security" / "reports" / "auto_permission_letters.jsonl"
EXPIRY_REPORT = ROOT / "security" / "reports" / "permission_expiry.json"
META_LETTER = ROOT / "surat-persetujuan-otomatis.md"
SIGNATURE = "(__signature__)"
MAX_TTL = DEFAULT_TTL
VALID_UNTIL = date(2027, 12, 31)
WARN_DAYS = 30
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"

DATE_PATTERNS = (
    re.compile(r"31\s+Desember\s+2027", re.I),
    re.compile(r"31-12-2027"),
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _append_index(record: dict[str, Any]) -> None:
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    with INDEX.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def issue(task: str, ttl: int = MAX_TTL, reason: str = "") -> dict[str, Any]:
    """Terbitkan izin otomatis + surat ringkas bila kategori diizinkan."""
    approval = AutoApproval().approve(task, ttl)
    if not approval.get("approved"):
        return {
            "status": "DITOLAK",
            "approval": approval,
            "letter": None,
            "license": LICENSE,
            "owner": OWNER,
        }

    LETTERS.mkdir(parents=True, exist_ok=True)
    identifier = str(approval["id"])
    path = LETTERS / f"{identifier}.md"
    issued = approval["timestamp"]
    expires = str(approval["expires_at"])
    scope = str(approval.get("scope", ""))
    text = f"""<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# SURAT IZIN OTOMATIS (KATEGORI RUTIN)

**Nomor:** `{identifier}`  
**Diterbitkan:** {issued}  
**Berlaku sampai:** {expires} (maksimal {ttl} detik)  
**Kategori:** `{task}`  
**Cakupan:** {scope}

Diterbitkan otomatis oleh IT Agenty / Tom05 berdasarkan
`surat-persetujuan-otomatis.md` (nomor `IT-AGENTY/OTO/2026/11-20`) yang
bertanda tangan `(__signature__)` dan berlaku sampai **31 Desember 2027**.

## Batasan

- Ini adalah izin rutin ber-scope dan berjangka, bukan otoritas baru.
- Bukan izin tanpa batas; tidak dapat diperpanjang otomatis.
- Tidak mencakup pencurian data, aksi jaringan eksternal, penghapusan
  lisensi pihak ketiga, atau tanda tangan manual atas nama pemilik.
- Dapat dicabut sewaktu-waktu secara tertulis oleh Owner / CEO.

## Penanda

Penanda persetujuan otomatis: `{SIGNATURE}` (dari meta-izin, bukan tanda
tangan manual baru). Kegiatan dicatat di `security/reports/auto_approvals.jsonl`
dan `security/reports/auto_permission_letters.jsonl`.

Alasan: {reason or "tugas operasional rutin"}

---

**Pemilik:** Tomi vier — Owner / CEO  
**Lisensi:** {LICENSE}
"""
    path.write_text(text, encoding="utf-8")
    record = {
        "id": identifier,
        "timestamp": issued,
        "task": task,
        "scope": scope,
        "ttl": ttl,
        "expires_at": expires,
        "letter": str(path.relative_to(ROOT)),
        "signature_marker": True,
        "status": "AKTIF",
        "license": LICENSE,
        "owner": OWNER,
    }
    _append_index(record)
    return {
        "status": "OK",
        "approval": approval,
        "letter": record,
        "license": LICENSE,
        "owner": OWNER,
    }


def letters(limit: int = 20) -> list[dict[str, Any]]:
    """Riwayat surat izin otomatis yang sudah diterbitkan."""
    if not INDEX.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _days_left(value: str) -> int | None:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (moment.date() - _now().date()).days


def _static_letters() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    paths = set(ROOT.glob("surat-*.md")) | set(ROOT.glob("DRAF-*.md"))
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8", errors="ignore")
        draft = path.name.startswith("DRAF-") or "DRAF" in text[:600].upper()
        expiry = VALID_UNTIL if any(pattern.search(text) for pattern in DATE_PATTERNS) else None
        if draft:
            state = "DRAF"
        elif expiry is None:
            state = "TANPA_TANGGAL"
        elif expiry < _now().date():
            state = "KEDALUWARSA"
        elif (expiry - _now().date()).days <= WARN_DAYS:
            state = "SEGERA_KEDALUWARSA"
        else:
            state = "AKTIF"
        rows.append({
            "file": path.name,
            "status": state,
            "bertanda_tangan": has_signature(text),
            "valid_until": expiry.isoformat() if expiry else None,
            "days_left": (expiry - _now().date()).days if expiry else None,
        })
    return rows


def check() -> dict[str, Any]:
    """Pemeriksaan read-only kedaluwarsa dan cakupan izin tertulis."""
    auto = []
    for item in letters(limit=500):
        left = _days_left(str(item.get("expires_at", "")))
        auto.append({
            "id": item.get("id"),
            "task": item.get("task"),
            "expires_at": item.get("expires_at"),
            "days_left": left,
            "status": str(item.get("status", "AKTIF")),
        })
    soon = [item for item in auto if item["days_left"] is not None
            and 0 <= item["days_left"] <= WARN_DAYS]
    static = _static_letters()
    warnings = [item for item in static if item["status"] in
                ("SEGERA_KEDALUWARSA", "KEDALUWARSA")]
    unsigned = [item["file"] for item in static
                if item["status"] == "AKTIF" and not item["bertanda_tangan"]]
    status = "PERINGATAN" if (soon or warnings or unsigned) else "AMAN"
    return {
        "status": status,
        "checked_at": _now().isoformat(),
        "meta_letter": META_LETTER.name,
        "meta_valid": META_LETTER.exists() and has_signature(
            META_LETTER.read_text(encoding="utf-8", errors="ignore")
        ),
        "valid_until": VALID_UNTIL.isoformat(),
        "warn_days": WARN_DAYS,
        "allowed_categories": sorted(ALLOWED),
        "denied_categories": sorted(DENIED),
        "auto_letters": auto,
        "auto_expiring_soon": soon,
        "static_letters": static,
        "warnings": warnings,
        "unsigned_active": unsigned,
        "note": "Pemeriksaan read-only; tidak menerbitkan atau memperpanjang izin.",
        "license": LICENSE,
        "owner": OWNER,
    }


def write_report(data: dict[str, Any]) -> Path:
    EXPIRY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    tmp = EXPIRY_REPORT.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(EXPIRY_REPORT)
    return EXPIRY_REPORT
