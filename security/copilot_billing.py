# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Panduan, status, dan gerbang otorisasi tagihan Copilot CLI.

Modul ini **tidak melakukan pembayaran** dan tidak menyimpan data kartu,
token, atau kredensial. `surat-kuasa-tandatangan.md` §2 secara eksplisit
melarang transaksi keuangan; auto-approval juga menolak
`external-network-action`. Karena itu aksi `payment` hanya dapat dibuka oleh
surat izin tertulis baru bermeterai tanda tangan pemilik, dan tetap memerlukan
token sekali pakai berjangka pendek yang diberikan pemilik sendiri.

Semua catatan audit memuat metadata saja (aksi, status, waktu, sidik jari
token), tidak pernah nilai token atau data pembayaran.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.privacy import has_signature  # noqa: E402
from system.hy4_auth import local_status  # noqa: E402

AUDIT = ROOT / "security" / "reports" / "copilot_billing.jsonl"
LETTER = ROOT / "surat-kuasa-tandatangan.md"
PAYMENT_LETTER = ROOT / "surat-izin-pembayaran-copilot.md"
AUTH_ENV = "AGENTY_BILLING_AUTH"
MAX_TTL = 300
BILLING_URL = "https://github.com/settings/billing"
PLANS_URL = "https://github.com/features/copilot/plans"

ALLOWED_ACTIONS = ("status", "guide", "plan-review", "record-confirmation")
DENIED_ACTIONS = ("payment", "auto-renew", "card-update", "token-export")


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _audit(entry: dict[str, Any]) -> None:
    try:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        blob = json.dumps(entry, ensure_ascii=False)
        with AUDIT.open("a", encoding="utf-8") as handle:
            handle.write(blob + "\n")
        os.chmod(AUDIT, 0o600)
    except OSError:
        pass


def _new_entry(action: str, status: str, reason: str, token: str = "") -> dict[str, Any]:
    entry: dict[str, Any] = {
        "waktu": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "aksi": action,
        "status": status,
        "alasan": reason,
    }
    if token:
        entry["sidik_token"] = _fingerprint(token)
    return entry


def guide() -> dict[str, Any]:
    """Panduan tagihan tanpa kredensial dan tanpa aksi jaringan."""
    return {
        "prinsip": "Sistem tidak menyimpan data pembayaran dan tidak menjalankan transaksi otomatis.",
        "pembayaran_manual": [
            f"Buka halaman tagihan resmi: {BILLING_URL}",
            f"Bandingkan paket di: {PLANS_URL}",
            "Lakukan pembayaran sendiri di browser dengan sesi akun Anda.",
            "Catat konfirmasi lewat: python3 security/copilot_billing.py record <referensi>",
        ],
        "batasan": [
            "surat-kuasa-tandatangan.md §2 melarang transaksi keuangan.",
            "auto-approval menolak external-network-action dan unlimited-auth.",
            f"Aksi payment hanya dibuka bila {PAYMENT_LETTER.name} ber-tanda tangan pemilik.",
            "Token otorisasi sekali pakai, maksimal 300 detik, tidak pernah dicetak.",
        ],
        "pemeriksaan": [
            "python3 copilot-bridge/doctor.py",
            "python3 security/copilot_billing.py status",
            "make billing-reminder",
        ],
    }


def status() -> dict[str, Any]:
    """Status lokal read-only; tidak menyentuh jaringan atau menampilkan nilai."""
    import importlib.util

    doctor_path = ROOT / "copilot-bridge" / "doctor.py"
    doctor: dict[str, Any] = {}
    if doctor_path.is_file():
        spec = importlib.util.spec_from_file_location("copilot_billing_doctor", doctor_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            doctor = module.diagnose()
    local = local_status()
    entry = _new_entry("status", "DILAKSANAKAN", "pemeriksaan lokal read-only")
    _audit(entry)
    return {
        "cli_tersedia": bool(doctor.get("cli_available")),
        "model": doctor.get("configured_model", "-"),
        "doctor": doctor.get("status", "TIDAK DIKETAHUI"),
        "kredensial_lokal": {
            "copilot": bool(local["copilot_auth"]),
            "opencode": bool(local["opencode_auth"]),
        },
        "status_langganan": "TIDAK DAPAT DITENTUKAN OFFLINE",
        "cara_cek": f"Periksa sendiri di {BILLING_URL}",
        "catatan": "Hanya boolean dan status; tidak ada nilai kredensial.",
    }


def payment_letter_valid() -> bool:
    return PAYMENT_LETTER.is_file() and has_signature(
        PAYMENT_LETTER.read_text(encoding="utf-8", errors="ignore")
    )


def _read_token(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"format token tidak valid: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("token harus berupa objek JSON")
    return data


def authorize(action: str, token: str = "") -> dict[str, Any]:
    """Validasi otorisasi eksplisit; tidak pernah menjalankan pembayaran."""
    token = token or os.environ.get(AUTH_ENV, "")
    if action in DENIED_ACTIONS:
        if action == "payment" and payment_letter_valid():
            reason = "surat izin ada; token masih wajib dan pembayaran tetap manual"
        else:
            reason = (
                f"DITOLAK: {LETTER.name} §2 melarang transaksi keuangan; "
                "perlu surat izin tertulis baru"
            )
        entry = _new_entry(action, "DITOLAK", reason, token)
        _audit(entry)
        return {"status": "DITOLAK", "alasan": reason, "catatan": "tidak ada transaksi yang dijalankan"}

    if action not in ALLOWED_ACTIONS:
        return {"status": "DITOLAK", "alasan": f"aksi '{action}' tidak dikenal"}

    if not token:
        return {
            "status": "DITOLAK",
            "alasan": f"Atur {AUTH_ENV} dengan JSON token sekali pakai dari pemilik.",
        }

    try:
        data = _read_token(token)
        now = time.time()
        issued_at = float(data["issued_at"])
        expires_at = float(data["expires_at"])
        token_action = str(data["action"])
        issued_by = str(data["issued_by"])
    except (KeyError, ValueError, TypeError) as exc:
        entry = _new_entry(action, "DITOLAK", f"token cacat: {type(exc).__name__}", token)
        _audit(entry)
        return {"status": "DITOLAK", "alasan": "token cacat"}

    reason = "disetujui"
    approved = (
        token_action == action
        and issued_at <= now <= expires_at
        and 0 < expires_at - issued_at <= MAX_TTL
        and bool(issued_by)
    )
    if not approved:
        reason = "token tidak cocok, kedaluwarsa, atau melebihi 300 detik"
    entry = _new_entry(action, "DIIZINKAN" if approved else "DITOLAK", reason, token)
    _audit(entry)
    return {
        "status": "DIIZINKAN" if approved else "DITOLAK",
        "alasan": reason,
        "aksi": action,
        "sidik_token": entry.get("sidik_token"),
        "catatan": "pembayaran tetap dilakukan manual oleh pemilik",
    }


def record(reference: str) -> dict[str, Any]:
    """Catat referensi konfirmasi; isi bebas disimpan sebagai metadata ringkas."""
    safe = "".join(ch for ch in reference if ch.isalnum() or ch in "-_.:/")[:120]
    entry = _new_entry("record-confirmation", "DICATAT", f"referensi={safe or '-'}")
    _audit(entry)
    return {"status": "DICATAT", "referensi": safe or "-", "catatan": "nilai pembayaran tidak disimpan"}


def history(limit: int = 20) -> list[dict[str, Any]]:
    """Riwayat audit metadata saja."""
    if not AUDIT.is_file():
        return []
    lines = [line for line in AUDIT.read_text(encoding="utf-8").splitlines() if line.strip()]
    result: list[dict[str, Any]] = []
    for line in lines[-max(1, limit):]:
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Panduan & gerbang tagihan Copilot CLI")
    sub = parser.add_subparsers(dest="aksi", required=True)
    sub.add_parser("guide")
    sub.add_parser("status")
    auth = sub.add_parser("authorize")
    auth.add_argument("action", choices=ALLOWED_ACTIONS + DENIED_ACTIONS)
    rec = sub.add_parser("record")
    rec.add_argument("reference")
    hist = sub.add_parser("history")
    hist.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    if args.aksi == "guide":
        print(json.dumps(guide(), indent=2, ensure_ascii=False))
    elif args.aksi == "status":
        print(json.dumps(status(), indent=2, ensure_ascii=False))
    elif args.aksi == "authorize":
        result = authorize(args.action)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "DIIZINKAN" else 1
    elif args.aksi == "record":
        print(json.dumps(record(args.reference), indent=2, ensure_ascii=False))
    elif args.aksi == "history":
        print(json.dumps(history(args.limit), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
