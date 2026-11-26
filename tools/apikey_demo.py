#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Demo aman untuk API key + tanda tangan HMAC-SHA256.

Terinspirasi oleh artikel BRIAPI tentang API key (Client ID dalam OAuth 2.0,
otorisasi proyek/pengguna, dan HMAC-SHA256 untuk integritas pesan).

Tidak ada kredensial yang disimpan di berkas ini. Nilai dibaca dari variabel
lingkungan saat runtime, dan keluaran bawaan tidak pernah menampilkan kunci.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import sys
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

KEY_ENV = "BRIAPI_CLIENT_ID"
SECRET_ENV = "BRIAPI_CLIENT_SECRET"
TIMESTAMP_TOLERANCE = 300  # detik
REPLAY_WINDOW = 1024
ROTATION_DAYS = 90
ROTATION_FILE = Path(
    os.environ.get("BRIAPI_ROTATION_FILE", "/root/workspace/security/reports/apikey-rotation.json")
)
REDACT_PATTERNS = [
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[^-]*-----END [^-]*-----", re.S),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{16,}"),
]


@dataclass
class Verifier:
    """Penyimpanang nonce dalam memori untuk menolak pemakaian ulang."""

    seen: set[str] = field(default_factory=set)

    def remember(self, nonce: str) -> bool:
        if nonce in self.seen:
            return False
        self.seen.add(nonce)
        if len(self.seen) > REPLAY_WINDOW:
            self.seen.clear()
        return True


def load_credentials() -> tuple[str, str]:
    key = os.environ.get(KEY_ENV, "")
    secret = os.environ.get(SECRET_ENV, "")
    if not key or not secret:
        raise SystemExit(
            f"Set variabel lingkungan {KEY_ENV} dan {SECRET_ENV} terlebih dahulu. "
            "Jangan pernah menuliskan kunci di dalam kode atau argumen baris perintah."
        )
    return key, secret


def canonical_string(method: str, path: str, timestamp: int, nonce: str, body: str) -> str:
    body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return "\n".join([method.upper(), path, str(timestamp), nonce, body_hash])


def signature_for(secret: str, message: str) -> str:
    return hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()


def build_headers(
    key: str,
    secret: str,
    method: str,
    path: str,
    body: str = "",
    timestamp: int | None = None,
    nonce: str | None = None,
) -> dict[str, str]:
    timestamp = int(time.time()) if timestamp is None else timestamp
    nonce = secrets.token_hex(16) if nonce is None else nonce
    message = canonical_string(method, path, timestamp, nonce, body)
    return {
        "X-Client-Id": key,
        "X-Timestamp": str(timestamp),
        "X-Nonce": nonce,
        "X-Signature": signature_for(secret, message),
    }


def redacted(headers: dict[str, str]) -> dict[str, str]:
    view = dict(headers)
    view["X-Client-Id"] = "***REDACTED***"
    view["X-Signature"] = view["X-Signature"][:8] + "…"
    return view


def verify_headers(
    headers: dict[str, str],
    secret: str,
    method: str,
    path: str,
    body: str,
    verifier: Verifier,
    now: int | None = None,
) -> tuple[bool, str]:
    now = int(time.time()) if now is None else now
    try:
        timestamp = int(headers["X-Timestamp"])
        nonce = headers["X-Nonce"]
        received = headers["X-Signature"]
    except (KeyError, ValueError):
        return False, "header tidak lengkap"

    if abs(now - timestamp) > TIMESTAMP_TOLERANCE:
        return False, "timestamp di luar jendela toleransi"
    if not verifier.remember(nonce):
        return False, "nonce sudah dipakai"

    message = canonical_string(method, path, timestamp, nonce, body)
    expected = signature_for(secret, message)
    if not hmac.compare_digest(received, expected):
        return False, "tanda tangan tidak cocok"
    return True, "valid"


def rotation_status() -> int:
    """Lacak usia kunci memakai sidik jari; kunci itu sendiri tidak disimpan."""
    key, _ = load_credentials()
    fingerprint = hashlib.sha256(key.encode("utf-8")).hexdigest()
    state: dict[str, dict[str, int]] = {}
    if ROTATION_FILE.exists():
        try:
            state = json.loads(ROTATION_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            state = {}

    now = int(time.time())
    entry = state.get(fingerprint)
    if not entry:
        state[fingerprint] = {"first_seen": now}
        ROTATION_FILE.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(ROTATION_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle)
        print(f"Kunci dicatat. Rotasi berikutnya dalam {ROTATION_DAYS} hari.")
        return 0

    age = max(0, (now - int(entry.get("first_seen", now))) // 86400)
    if age >= ROTATION_DAYS:
        print(f"PERLU ROTASI: kunci berusia {age} hari, batas {ROTATION_DAYS} hari.")
        return 1
    print(f"MASIH BERLAKU: kunci berusia {age} hari dari batas {ROTATION_DAYS} hari.")
    return 0


def redact_text(text: str) -> str:
    """Samarkan nilai kredensial sebelum teks ditulis ke log."""
    values = [os.environ.get(name, "") for name in (KEY_ENV, SECRET_ENV)]
    for value in sorted((v for v in values if v), key=len, reverse=True):
        text = text.replace(value, "***REDACTED***")
    for pattern in REDACT_PATTERNS:
        text = pattern.sub("***REDACTED***", text)
    return text


def selftest() -> int:
    """Uji memakai nilai buatan; tidak menyentuh kredensial asli."""
    dummy_key = "demo-client-" + secrets.token_hex(4)
    dummy_secret = secrets.token_hex(32)
    now = int(time.time())
    headers = build_headers(dummy_key, dummy_secret, "POST", "/v1/demo", "amount=1000", now)

    ok, reason = verify_headers(headers, dummy_secret, "POST", "/v1/demo", "amount=1000", Verifier(), now)
    assert ok and reason == "valid", reason
    print("PASS  tanda tangan valid diterima")

    tampered = dict(headers, **{"X-Signature": "0" * 64})
    ok, reason = verify_headers(tampered, dummy_secret, "POST", "/v1/demo", "amount=1000", Verifier(), now)
    assert not ok and reason == "tanda tangan tidak cocok", reason
    print("PASS  tanda tangan diubah ditolak")

    ok, reason = verify_headers(headers, dummy_secret, "POST", "/v1/demo", "amount=9999", Verifier(), now)
    assert not ok and reason == "tanda tangan tidak cocok", reason
    print("PASS  perubahan isi payload ditolak")

    ok, reason = verify_headers(
        headers, dummy_secret, "POST", "/v1/demo", "amount=1000", Verifier(), now + TIMESTAMP_TOLERANCE + 1
    )
    assert not ok and "timestamp" in reason, reason
    print("PASS  timestamp kadaluarsa ditolak")

    replay = Verifier()
    ok, reason = verify_headers(headers, dummy_secret, "POST", "/v1/demo", "amount=1000", replay, now)
    assert ok, reason
    ok, reason = verify_headers(headers, dummy_secret, "POST", "/v1/demo", "amount=1000", replay, now)
    assert not ok and "nonce" in reason, reason
    print("PASS  pemakaian ulang nonce ditolak")

    sample = "authorization: ghp_" + "a" * 36 + "\n"
    redacted = redact_text(sample)
    assert "ghp_" not in redacted and "REDACTED" in redacted
    print("PASS  pola token pada log disamarkan")

    print("SELFTEST OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sign = sub.add_parser("sign", help="bangun header bertanda tangan")
    sign.add_argument("--method", default="POST")
    sign.add_argument("--path", default="/v1/demo")
    sign.add_argument("--body", default="")
    sign.add_argument("--emit-file", help="tulis header lengkap ke berkas dengan izin 0600")

    verify = sub.add_parser("verify", help="verifikasi header dari JSON")
    verify.add_argument("json", help="JSON header bertanda tangan")
    verify.add_argument("--method", default="POST")
    verify.add_argument("--path", default="/v1/demo")
    verify.add_argument("--body", default="")

    sub.add_parser("selftest", help="uji dengan nilai buatan tanpa kredensial")
    sub.add_parser("rotate-status", help="cek usia kunci memakai sidik jari")
    sub.add_parser("redact", help="samarkan kredensial dari stdin sebelum dicatat")

    args = parser.parse_args()
    if args.command == "selftest":
        return selftest()
    if args.command == "rotate-status":
        return rotation_status()
    if args.command == "redact":
        sys.stdout.write(redact_text(sys.stdin.read()))
        return 0

    key, secret = load_credentials()
    if args.command == "sign":
        headers = build_headers(key, secret, args.method, args.path, args.body)
        if args.emit_file:
            fd = os.open(args.emit_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(headers, handle)
            print(f"Header lengkap ditulis ke {args.emit_file} (mode 0600)")
        print(json.dumps(redacted(headers), indent=2))
        return 0

    try:
        headers = json.loads(args.json)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON tidak valid: {exc}") from exc
    ok, reason = verify_headers(headers, secret, args.method, args.path, args.body, Verifier())
    print("VALID" if ok else f"DITOLAK: {reason}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
