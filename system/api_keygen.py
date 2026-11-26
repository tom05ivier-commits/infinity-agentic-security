# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pembangkit kunci API aman — adaptasi lokal dari HEX Hero Random Key Generator.

Kemampuan yang di-clone (https://share.google/6GMmCzrbL3tEz57Ji):
  * pembangkitan acak kriptografis (CSPRNG) setara Web Crypto API / ``openssl rand``;
  * pilihan format Base64, Hexadecimal, URL-safe Base64, Alphanumeric;
  * kekuatan 128 / 256 / 384 / 512 bit; jumlah 1..100.

Penyempurnaan untuk IT Agenty:
  * kunci disimpan otomatis per-pemasangan di ``credentials/.env`` (mode 0600);
  * ``ensure_api_key()`` membuat kunci hanya bila belum ada — langsung "bekerja";
  * rotasi + audit; nilai kunci TIDAK PERNAH dicetak/dicatat, hanya sidik jari
    SHA-256 dan metadata (path, panjang, format, waktu);
  * ``load_api_key()`` membaca dari environment lalu berkas kredensial lokal.

Prinsip ``PANDUAN-OTORISASI-PUBLIK.md`` dipatuhi: token per pemasangan, tidak
dibagikan, tidak masuk chat/log/repo publik. Kunci cloud milik akun tetap
didapat lewat ``opencode auth login``; modul ini mengelola kunci API lokal
yang Anda miliki sendiri.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import secrets
import string
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CRED_DIR = ROOT / "credentials"
ENV_FILE = CRED_DIR / ".env"
AUDIT_FILE = ROOT / "security" / "reports" / "api_keygen.jsonl"

FORMATS = ("base64", "hex", "urlsafe", "alphanumeric")
STRENGTHS = (128, 256, 384, 512)
DEFAULT_STRENGTH = 256
DEFAULT_FORMAT = "base64"
# Kunci yang dikelola lokal. Kunci cloud OpenCode bukan kunci acak buatan
# lokal — untuk itu tetap pakai `opencode auth login`.
DEFAULT_KEY = "AGENTY_API_KEY"
CLOUD_KEY = "OPENCODE_API_KEY"
KNOWN_KEYS = (
    "OPENCODE_API_KEY",
    "GITHUB_TOKEN",
    "AGENTY_RED_AUTH_TOKEN",
    "AGENTY_API_KEY",
)
ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
ALPHANUM = string.ascii_letters + string.digits

# Pola kunci nyata untuk pengaman audit: dipakai untuk memastikan tidak ada
# nilai kunci yang terselip ke dalam catatan.
_SECRET_SHAPES: tuple[re.Pattern[str], ...] = (
    re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"),
    re.compile(r"[A-Fa-f0-9]{64,}"),
)


class KeygenError(ValueError):
    """Kesalahan validasi pembangkitan kunci."""


def _validate(strength: int, format_name: str, quantity: int) -> None:
    if strength not in STRENGTHS:
        raise KeygenError(f"kekuatan harus salah satu dari {STRENGTHS}")
    if format_name not in FORMATS:
        raise KeygenError(f"format harus salah satu dari {FORMATS}")
    if not 1 <= quantity <= 100:
        raise KeygenError("jumlah kunci harus antara 1 dan 100")


def generate_key(strength: int = DEFAULT_STRENGTH, format_name: str = DEFAULT_FORMAT) -> str:
    """Bangkitkan satu kunci dari CSPRNG. Tidak ada nilai yang dicetak."""
    _validate(strength, format_name, 1)
    nbytes = strength // 8
    raw = secrets.token_bytes(nbytes)
    if format_name == "base64":
        return base64.b64encode(raw).decode("ascii")
    if format_name == "hex":
        return raw.hex()
    if format_name == "urlsafe":
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    # alphanumeric: sampling tanpa bias, panjang cukup untuk ~`strength` bit.
    count = math.ceil(strength / math.log2(len(ALPHANUM)))
    return "".join(secrets.choice(ALPHANUM) for _ in range(count))


def generate_keys(
    strength: int = DEFAULT_STRENGTH,
    format_name: str = DEFAULT_FORMAT,
    quantity: int = 1,
) -> list[str]:
    """Bangkitkan beberapa kunci sekaligus (maks. 100)."""
    _validate(strength, format_name, quantity)
    return [generate_key(strength, format_name) for _ in range(quantity)]


def fingerprint(value: str) -> str:
    """Sidik jari SHA-256 (16 hex awal) untuk mengenali kunci tanpa menampilnya."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _metadata(value: str, *, name: str, action: str, strength: int, format_name: str) -> dict[str, Any]:
    return {
        "aksi": action,
        "nama": name,
        "sidik_jari": fingerprint(value),
        "panjang": len(value),
        "kekuatan_bit": strength,
        "format": format_name,
        "waktu": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "lokasi": str(ENV_FILE),
        "peringatan": "nilai kunci sengaja tidak disertakan",
    }


def _audit(meta: dict[str, Any]) -> None:
    """Catat metadata ke JSONL. Menolak baris yang mengandung pola kunci nyata."""
    try:
        AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        blob = json.dumps(meta, ensure_ascii=False)
        if any(pattern.search(blob) for pattern in _SECRET_SHAPES):
            raise KeygenError("audit mengandung pola kunci nyata — ditolak")
        with AUDIT_FILE.open("a", encoding="utf-8") as handle:
            handle.write(blob + "\n")
        os.chmod(AUDIT_FILE, 0o600)
    except OSError:
        # Audit gagal tidak boleh membatalkan pembangkitan, tetapi kunci
        # tetap tidak pernah ditampilkan.
        pass


def _read_env_lines() -> list[str]:
    try:
        return ENV_FILE.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []


def _parse_env() -> dict[str, str]:
    data: dict[str, str] = {}
    for line in _read_env_lines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key[7:].strip()
        value = value.strip().strip('"').strip("'")
        data[key] = value
    return data


def _write_env(lines: list[str]) -> None:
    """Tulis berkas kredensial secara atomik dengan mode 0600."""
    parent = ENV_FILE.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".env.", dir=str(parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines).rstrip("\n") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, ENV_FILE)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _set_env_value(name: str, value: str) -> None:
    if not ENV_NAME_RE.match(name):
        raise KeygenError("nama variabel harus huruf kapital/angka/garis bawah")
    pattern = re.compile(rf"^\s*(?:export\s+)?{re.escape(name)}\s*=")
    lines = _read_env_lines()
    result: list[str] = []
    replaced = False
    for line in lines:
        if pattern.match(line):
            if not replaced:
                result.append(f"{name}={value}")
                replaced = True
            continue
        result.append(line)
    if not replaced:
        result.append(f"{name}={value}")
    _write_env(result)


def load_api_key(name: str = DEFAULT_KEY) -> str | None:
    """Ambil kunci dari environment lebih dulu, lalu berkas kredensial lokal."""
    value = os.environ.get(name)
    if value:
        return value.strip()
    value = _parse_env().get(name)
    return value or None


def status() -> dict[str, Any]:
    """Laporkan keberadaan kunci sebagai boolean — tanpa nilai."""
    data = _parse_env()
    presence: dict[str, bool] = {}
    for name in KNOWN_KEYS:
        presence[name] = bool(os.environ.get(name) or data.get(name))
    try:
        mode = oct(ENV_FILE.stat().st_mode & 0o777)
    except OSError:
        mode = "tidak ada"
    return {
        "lokasi": str(ENV_FILE),
        "mode": mode,
        "kunci": presence,
        "catatan": "hanya status boolean; nilai kunci tidak pernah ditampilkan",
    }


GUARD_SKIP_DIRS = {
    ".git", "__pycache__", "quarantine", "logs", "node_modules",
    ".playwright-mcp", "opencode-src", "symphony-src", "src",
}
GUARD_SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".pdf", ".zip",
    ".woff", ".woff2", ".ttf", ".bin", ".so", ".a", ".o", ".pyc", ".sqlite",
}


def guard(name: str = DEFAULT_KEY, root: Path = ROOT) -> dict[str, Any]:
    """Audit privasi kunci: mode, .gitignore, audit, dan kebocoran nilai.

    Mengembalikan path dan alasan saja; nilai kunci tidak pernah disertakan.
    """
    root = Path(root)
    key = load_api_key(name)
    if not key:
        return {
            "status": "PERLU TINDAKAN",
            "nama": name,
            "alasan": ["kunci belum ada"],
            "catatan": "jalankan: ./api-key.sh ensure",
        }

    issues: list[str] = []
    try:
        mode = ENV_FILE.stat().st_mode & 0o777
    except OSError:
        mode = None
    if mode is None or mode & 0o077:
        issues.append("mode kredensial longgar")
    ignore_text = ""
    gitignore = root / ".gitignore"
    if gitignore.is_file():
        try:
            ignore_text = gitignore.read_text(encoding="utf-8")
        except OSError:
            pass
    if "credentials/.env" not in ignore_text:
        issues.append("credentials/.env belum masuk .gitignore")

    audit_clean = True
    if AUDIT_FILE.is_file():
        try:
            audit_clean = key not in AUDIT_FILE.read_text(encoding="utf-8")
        except OSError:
            audit_clean = False
    if not audit_clean:
        issues.append("audit mengandung nilai kunci")

    leaks: list[str] = []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in GUARD_SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path == ENV_FILE or path.suffix.lower() in GUARD_SKIP_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            scanned += 1
            if key in text:
                leaks.append(str(path.relative_to(root)))
            if scanned > 20_000:
                break
        if scanned > 20_000:
            break
    if leaks:
        issues.append("kunci ditemukan di berkas lain")

    return {
        "status": "AMAN" if not issues else "PERLU TINDAKAN",
        "nama": name,
        "sidik_jari": fingerprint(key),
        "mode": oct(mode) if mode is not None else "tidak ada",
        "gitignore": "credentials/.env" in ignore_text,
        "audit_bersih": audit_clean,
        "lokasi_bocor": sorted(set(leaks)),
        "file_diperiksa": scanned,
        "alasan": issues,
        "catatan": "hanya path dan alasan; nilai kunci tidak disertakan",
    }


def set_api_key(
    name: str = DEFAULT_KEY,
    value: str | None = None,
    *,
    strength: int = DEFAULT_STRENGTH,
    format_name: str = DEFAULT_FORMAT,
    action: str = "set",
) -> dict[str, Any]:
    """Simpan kunci (dibangkitkan bila ``value`` kosong) dan kembalikan metadata."""
    if value is None:
        value = generate_key(strength, format_name)
    _set_env_value(name, value)
    meta = _metadata(
        value, name=name, action=action, strength=strength, format_name=format_name
    )
    _audit(meta)
    return meta


def ensure_api_key(
    name: str = DEFAULT_KEY,
    *,
    strength: int = DEFAULT_STRENGTH,
    format_name: str = DEFAULT_FORMAT,
) -> dict[str, Any]:
    """Buat kunci hanya bila belum ada — membuat API key otomatis "bekerja"."""
    existing = load_api_key(name)
    if existing:
        return {
            "aksi": "ensure",
            "nama": name,
            "sidik_jari": fingerprint(existing),
            "dibuat": False,
            "status": "ADA",
            "catatan": "kunci sudah ada; tidak ditimpa",
        }
    meta = set_api_key(name, strength=strength, format_name=format_name, action="ensure")
    meta["dibuat"] = True
    meta["status"] = "ADA"
    return meta


def rotate_api_key(
    name: str = DEFAULT_KEY,
    *,
    strength: int = DEFAULT_STRENGTH,
    format_name: str = DEFAULT_FORMAT,
) -> dict[str, Any]:
    """Rotasi kunci: bangkitkan nilai baru, timpa yang lama, catat metadata."""
    # Audit bersifat append-only: rotasi menambah catatan baru, bukan menimpa
    # riwayat kunci lama.
    return set_api_key(
        name, strength=strength, format_name=format_name, action="rotate"
    )


def _print(data: object, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="api_keygen.py",
        description="Pembangkit kunci API aman — nilai kunci tidak dicetak kecuali diminta eksplisit",
    )
    sub = parser.add_subparsers(dest="aksi", required=True)

    def add_opts(p: argparse.ArgumentParser) -> None:
        p.add_argument("--strength", type=int, choices=STRENGTHS, default=DEFAULT_STRENGTH)
        p.add_argument("--format", dest="format_name", choices=FORMATS, default=DEFAULT_FORMAT)
        p.add_argument("--name", default=DEFAULT_KEY)

    gen = sub.add_parser("generate", help="Bangkitkan kunci tanpa menyimpannya")
    add_opts(gen)
    gen.add_argument("--quantity", type=int, default=1)
    gen.add_argument("--show", action="store_true", help="TAMPILKAN nilai kunci (rahasia; eksplisit)")

    for name, help_text in (
        ("set", "Bangkitkan lalu simpan ke kredensial lokal"),
        ("ensure", "Buat hanya bila belum ada (otomatis, idempoten)"),
        ("rotate", "Rotasi kunci yang tersimpan"),
    ):
        p = sub.add_parser(name, help=help_text)
        add_opts(p)

    stat = sub.add_parser("status", help="Status keberadaan kunci (boolean saja)")
    stat.add_argument("--json", action="store_true", dest="as_json")

    guard_cmd = sub.add_parser("guard", help="Audit privasi kunci tanpa menampilkan nilai")
    guard_cmd.add_argument("--name", default=DEFAULT_KEY)

    load = sub.add_parser("load", help="Ambil kunci untuk dipakai aplikasi")
    load.add_argument("--name", default=DEFAULT_KEY)
    load.add_argument(
        "--export",
        action="store_true",
        help="Cetak 'export NAME=...' untuk dievaluasi shell (menyingkap nilai)",
    )

    args = parser.parse_args(argv)
    as_json = getattr(args, "as_json", False)

    if args.aksi == "generate":
        keys = generate_keys(args.strength, args.format_name, args.quantity)
        if args.show:
            print("PERINGATAN: nilai kunci berikut adalah rahasia.", file=sys.stderr)
            for key in keys:
                print(key)
        else:
            result = [
                {
                    "sidik_jari": fingerprint(key),
                    "panjang": len(key),
                    "format": args.format_name,
                    "kekuatan_bit": args.strength,
                }
                for key in keys
            ]
            _print(result if len(result) > 1 else result[0], as_json)

    elif args.aksi == "set":
        _print(set_api_key(args.name, strength=args.strength, format_name=args.format_name), False)

    elif args.aksi == "ensure":
        _print(ensure_api_key(args.name, strength=args.strength, format_name=args.format_name), False)

    elif args.aksi == "rotate":
        _print(rotate_api_key(args.name, strength=args.strength, format_name=args.format_name), False)

    elif args.aksi == "status":
        _print(status(), args.as_json)

    elif args.aksi == "guard":
        result = guard(args.name)
        _print(result, True)
        if result["status"] != "AMAN":
            return 1

    elif args.aksi == "load":
        value = load_api_key(args.name)
        if value is None:
            print(f"{args.name}: kosong", file=sys.stderr)
            return 1
        if args.export:
            print("PERINGATAN: perintah ini menyingkap nilai kunci ke shell.", file=sys.stderr)
            escaped = value.replace("'", "'\\''")
            print(f"export {args.name}='{escaped}'")
        else:
            print(f"{args.name}: ADA ({len(value)} karakter, sidik {fingerprint(value)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
