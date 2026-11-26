# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Data Guard — protokol ekspor opsional, defensively, lengkap & teraudit.

Di-tetapkan use-case: "Lindungi data dari kirim data ilegal" — guard
pra-aktif blocking untuk text yang TIDAK BOLEH diekspor:
  * BLOCK pada kredensial (github token/PAT, OpenAI key, bearer, assignment api_key=...),
  * BLOCK pada password + email + tanggal lahir (PII tidak boleh ekspor sederhana),
  * WARN pada isyarat PII ringan (nama-tanda-tanda).

Semua penanda di-normalisasi ke lowercase; semua kata berkal di warna wajar
di namespace security/reports/data_guard_actions.jsonl (append-only).
Nilai kredensial tidak pernah dicetak.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "security" / "reports" / "data_guard_actions.jsonl"
SIGNATURE = "(__signature__)"

BLOCK_LABELS = {"github_token", "github_pat", "openai_key", "bearer", "assignment"}
WARN_LABELS = {"email", "whatsapp", "tanda_tangan"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def audit(action: str, payload: dict[str, Any]) -> None:
    try:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": _now(), "action": action, **payload},
                               ensure_ascii=False) + "\n")
    except OSError:
        pass  # guard MUST NOT crash the exporter


def check(text: str) -> dict[str, Any]:
    """Pemandu preflight. Return {"status": "OK"|"WARN"|"BLOCK", "laporan": {...}}."""
    from security.privacy import scan, scan_secrets

    s = str(text)
    secrets = scan_secrets(s)
    pii = scan(s)

    # BLOCK pada kredensial (lupa saja, kata sandi = PII yang sensitif).
    block = {k: v for k, v in secrets.items() if v > 0 and k in BLOCK_LABELS}
    if pii.get("katasandi", 0) > 0:
        block["katasandi"] = block.get("katasandi", 0) + pii.get("katasandi", 0)
    # WARN pada PII ringan yang tetap sensif: email + tanda tangan.
    warn = {k: v for k, v in pii.items() if v > 0 and k in WARN_LABELS and k not in block}
    status = "BLOCK" if block else ("WARN" if warn else "OK")
    laporan = {
        "secrets": {k: v for k, v in secrets.items() if v > 0},
        "pii": {k: v for k, v in pii.items() if v > 0},
        "blocked_labels": sorted(block),
        "warn_labels": sorted(warn) if warn else [],
    }
    if status != "OK":
        audit(status, {"laporan": laporan})
    return {"status": status, "laporan": laporan}


def scan_before_send(path: Path) -> dict[str, Any]:
    """Baca berkas terlebih dahulu (read-only) lalu guard."""
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return check(text)


def data_guard_path() -> str:
    return str(ROOT)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Data Guard — preflight pemblokiran ekspor")
    ap.add_argument("text", nargs="?")
    ap.add_argument("--file", "-f", type=Path)
    a = ap.parse_args()
    if a.file:
        out = scan_before_send(a.file)
    elif a.text:
        out = check(a.text)
    else:
        ap.print_help(); raise SystemExit(2)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if out["status"] == "BLOCK":
        raise SystemExit(1)
    if out["status"] == "WARN":
        raise SystemExit(0)
