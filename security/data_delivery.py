# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Pengiriman laporan ke pemilik dengan gerbang DLP & daftar tujuan.

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .blue.dlp import scan_file
from .common.config import SECURITY_ROOT
from .privacy import SIGNATURES

REPORTS = SECURITY_ROOT / "reports"
DELIVERY_DIR = REPORTS / "deliveries"
AUDIT = REPORTS / "data_deliveries.jsonl"
ALLOWED_REPORTS = (
    "efficacy.json",
    "debug_report.json",
    "campaign.json",
    "final_report.json",
)
ALLOWED_DESTINATIONS = {"local", "webhook"}


def _destination_allowed(channel: str) -> tuple[bool, str]:
    if channel not in ALLOWED_DESTINATIONS:
        return False, f"Kanal '{channel}' tidak ada dalam daftar izin."
    if channel == "webhook":
        url = os.environ.get("AGENTY_DELIVERY_WEBHOOK", "")
        if not url.startswith("https://"):
            return False, "Webhook harus HTTPS dan ditetapkan via AGENTY_DELIVERY_WEBHOOK."
    return True, ""


def deliver(channel: str = "local", report_names: tuple[str, ...] = ALLOWED_REPORTS) -> dict[str, Any]:
    """Kirim ringkasan laporan hasil ke tujuan yang diizinkan."""
    allowed, reason = _destination_allowed(channel)
    if not allowed:
        return {"status": "DITOLAK", "reason": reason}

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": "Tomi vier",
        "license": "Tom05ivier-commits-1.0",
        "reports": {},
        "note": "Ringkasan non-sensitif; tanpa kredensial atau data pribadi mentah.",
    }
    blocked: list[str] = []
    for name in report_names:
        path = REPORTS / name
        if not path.exists():
            continue
        # Gerbang DLP: tolak berkas dengan temuan HIGH/CRITICAL.
        scan = scan_file(path)
        severe = [f for f in scan.findings if f.severity.value in ("HIGH", "CRITICAL")]
        if severe:
            blocked.append(name)
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        payload["reports"][name] = {
            key: data.get(key)
            for key in ("status", "skor_rata_rata", "siklus", "fulfilled", "risk_score")
            if key in data
        }

    DELIVERY_DIR.mkdir(parents=True, exist_ok=True)
    from .privacy import redact as redact_private

    out = DELIVERY_DIR / f"delivery-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.json"
    out.write_text(
        redact_private(json.dumps(payload, indent=2, ensure_ascii=False)),
        encoding="utf-8",
    )

    if channel == "webhook":
        url = os.environ["AGENTY_DELIVERY_WEBHOOK"]
        request = urllib.request.Request(
            url,
            data=out.read_bytes(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            remote_status = response.status
    else:
        remote_status = "local"

    record = {
        "timestamp": payload["generated_at"],
        "channel": channel,
        "status": "TERKIRIM",
        "file": str(out),
        "remote_status": remote_status,
        "reports": sorted(payload["reports"]),
        "blocked_by_dlp": blocked,
        "signature": SIGNATURES[0],
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
