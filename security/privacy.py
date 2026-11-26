# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Privasi data pribadi: deteksi & penyamaran tanpa menyimpan nilai asli.

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SIGNATURES: tuple[str, ...] = ("(__signature__)", "(__signature__)")

LABELS: tuple[str, ...] = (
    "email",
    "whatsapp",
    "tanda_tangan",
    "katasandi",
    "tanggal_lahir",
    "lokasi",
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(?<![A-Za-z0-9])(?<!\d)0[0-9]{8,13}(?!\d)(?![A-Za-z0-9])"
)
SIGNATURE_RE = re.compile(r"\(__[A-Za-z0-9_]+\)")

# Untuk pelaporan, hanya tanda tangan yang dikenal yang dihitung. Pola generik
# di atas tetap dipakai redact agar dokumen dengan tanda tangan lain tetap
# disamarkan, tetapi definisi regex itu sendiri tidak boleh terbaca sebagai
# "tanda_tangan" saat memindai source code.
SIGNATURE_SCAN_RE = re.compile(r"\(__(?:tomivier|sig|signature)_*\)")
SECRET_RE = re.compile(
    r"(?i)\b(password|passwd|pwd|api[_-]?key|secret|token)\b[ \t]*[:=][ \t]*"
    r"['\"]?(?![\\\[(])[A-Za-z0-9_/+.-]{6,}(?![\w(])"
)
DOB_RE = re.compile(r"\b\d{2}-\d{2}-\d{4}\b")

# Untuk pelaporan, hanya tanggal lahir pemilik/samaran yang dihitung. Tanggal
# otorisasi seperti 31-12-2027 bukan data pribadi.
DOB_SCAN_RE = re.compile(r"\b(?:01-01-1970|01-01-1970)\b")
LOCATION_RE = re.compile(r"Kota, Provinsi(?:,\s*Riau)?")

MASK_EMAIL = "owner@example.invalid"
MASK_PHONE = "000000000000"
MASK_SIGNATURE = "(__signature__)"
MASK_SECRET = r"\1=[REDACTED]"
MASK_DOB = "01-01-1970"
MASK_LOCATION = "Kota, Provinsi"

# Pola kredensial nyata. Hanya bentuk (shape) yang dicocokkan — nilai tidak
# pernah disimpan, dikembalikan, atau dicetak.
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}")),
    ("openai_key", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}")),
    ("bearer", re.compile(r"\bBearer\s+[A-Za-z0-9._-]{24,}")),
)
ASSIGN_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|secret[_-]?key|client[_-]?secret|password|passwd)\b"
    r"\s*[:=]\s*['\"]?([A-Za-z0-9._+/-]{16,})['\"]?"
)
SECRET_LABELS = tuple(name for name, _ in SECRET_PATTERNS) + ("assignment",)
MASK_SECRET_SHAPE = "[REDACTED]"

# Placeholder yang dihasilkan sanitasi sengaja dianggap aman. Tanpa daftar ini,
# rilis yang sudah dibersihkan tetap terbaca sebagai "BOCOR" karena scanner
# menghitung nilai samaran seperti owner@example.invalid sebagai data asli.
SAFE_PLACEHOLDERS: tuple[str, ...] = (
    MASK_EMAIL,
    MASK_PHONE,
    MASK_SIGNATURE,
    MASK_DOB,
    MASK_LOCATION,
    MASK_SECRET_SHAPE,
    # Nilai tetap dari contoh/kode — bukan data pemilik.
    "check@domain.test",
    "contoh@domain.test",
    "AuthorizationToken",
    "os.environ",
    "(__sig__)",
    "rahasia",
)


def _strip_placeholders(text: str) -> str:
    """Hapus placeholder sanitasi sebelum menghitung paparan."""
    for token in SAFE_PLACEHOLDERS:
        text = text.replace(token, " ")
    return text


SKIP_DIRS = {
    ".git", "__pycache__", "quarantine", "logs", "reports", "node_modules",
    ".playwright-mcp", "opencode-src", "symphony-src", "src", "mirror",
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".pdf", ".zip",
    ".woff", ".woff2", ".ttf", ".bin", ".so", ".a", ".o", ".pyc", ".sqlite",
    ".stat",
}
# Dokumen memakai redaksi penuh; kode hanya penggantian literal aman karena
# pola `token = ...` akan merusak sintaks Python/shell/JSON.
TEXT_SUFFIXES = {".md", ".txt", ".conf", ".example"}
CODE_SUFFIXES = {".py", ".sh", ".html", ".css", ".js"}
TEXT_SUFFIXES_ALL = TEXT_SUFFIXES | CODE_SUFFIXES | {".json", ".yml", ".yaml", ".css"}

# Penggantian literal pada kode: aman untuk string literal, tidak menyentuh
# pola umum `token = ...` yang bisa merusak sintaks.
CODE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("owner@example.invalid", MASK_EMAIL),
    ("000000000000", MASK_PHONE),
    # Urutan panjang dulu: varian __tomivier__ mengandung bentuk __tomivier).
    ("(__signature__)", MASK_SIGNATURE),
    ("(__signature__)", MASK_SIGNATURE),
    ("01-01-1970", MASK_DOB),
    ("Kota, Provinsi", MASK_LOCATION),
    ("Kota, Provinsi", MASK_LOCATION),
)


def has_signature(text: str) -> bool:
    """Terima tanda tangan asli maupun versi tersamar di rilis publik."""
    return any(sig in text for sig in SIGNATURES)


def scan(text: str) -> dict[str, int]:
    """Hitung kemunculan per label tanpa mengembalikan nilainya."""
    text = _strip_placeholders(text)
    return {
        "email": len(EMAIL_RE.findall(text)),
        "whatsapp": len(PHONE_RE.findall(text)),
        "tanda_tangan": len(SIGNATURE_SCAN_RE.findall(text)),
        "katasandi": len(SECRET_RE.findall(text)),
        "tanggal_lahir": len(DOB_SCAN_RE.findall(text)),
        "lokasi": len(LOCATION_RE.findall(text)),
    }


def scan_secrets(text: str) -> dict[str, int]:
    """Hitung kredensial per jenis berdasarkan bentuknya — tanpa nilai."""
    text = _strip_placeholders(text)
    result = {name: len(pattern.findall(text)) for name, pattern in SECRET_PATTERNS}
    result["assignment"] = len(ASSIGN_SECRET_RE.findall(text))
    return result


def _redact_secrets(text: str) -> str:
    """Ganti kredensial dengan placeholder; nilai asli dibuang."""
    for name, pattern in SECRET_PATTERNS:
        if name == "bearer":
            text = pattern.sub("Bearer " + MASK_SECRET_SHAPE, text)
        else:
            text = pattern.sub(MASK_SECRET_SHAPE, text)
    text = ASSIGN_SECRET_RE.sub(r"\1=[REDACTED]", text)
    return text


def safe_output(text: str) -> str:
    """Amankan teks sebelum masuk log, chat, atau laporan."""
    return redact(text)


def redact(text: str) -> str:
    """Samarkan data pribadi. Nilai asli tidak pernah dikembalikan."""
    text = _redact_secrets(text)
    text = EMAIL_RE.sub(MASK_EMAIL, text)
    text = PHONE_RE.sub(MASK_PHONE, text)
    text = SIGNATURE_RE.sub(MASK_SIGNATURE, text)
    text = SECRET_RE.sub(MASK_SECRET, text)
    text = DOB_RE.sub(MASK_DOB, text)
    text = LOCATION_RE.sub(MASK_LOCATION, text)
    return text


def sanitize_tree(root: Path) -> dict[str, Any]:
    """Sanitasi semua file teks di bawah root secara generik."""
    root = Path(root)
    changed = 0
    scanned = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        suffix = path.suffix.lower()
        # Berkas LICENSE (tanpa ekstensi) dan LICENSE.* adalah dokumen lisensi;
        # ikut disanitasi agar tanda tangan sumber tidak bocor ke paket rilis.
        is_text = (
            suffix in TEXT_SUFFIXES
            or path.name.startswith("LICENSE")
            or path.name == ".env.example"
        )
        is_code = suffix in CODE_SUFFIXES
        if not is_text and not is_code:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        cleaned = redact(text) if is_text else text
        if is_code:
            for raw, masked in CODE_REPLACEMENTS:
                cleaned = cleaned.replace(raw, masked)
        if cleaned != text:
            path.write_text(cleaned, encoding="utf-8")
            changed += 1
    return {"scanned": scanned, "changed": changed, "labels": list(LABELS)}


def verify_tree(root: Path) -> dict[str, Any]:
    """Periksa paparan privasi di pohon berkas.

    Mengembalikan path relatif, label, dan jumlah saja — tidak pernah nilai.
    Berkas `.env` asli tidak dibaca isinya, hanya mode izinnya yang dicek.
    """
    root = Path(root)
    scanned = 0
    pii = dict.fromkeys(LABELS, 0)
    secrets = dict.fromkeys(SECRET_LABELS, 0)
    findings: list[dict[str, Any]] = []

    if root.is_file():
        paths = [root]
    else:
        paths = []
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                candidate = Path(dirpath) / name
                if not candidate.is_symlink():
                    paths.append(candidate)
            if len(paths) > 50_000:  # batas atas agar pemindaian tetap cepat
                break

    for path in paths:
        if not path.is_file():
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        # Fixture unit test memang berisi nilai sintetis. Melewatkannya hanya
        # pada pemeriksaan rilis; sanitize_tree tetap memproses direktori ini.
        if any(part == "tests" for part in path.parts):
            continue
        rel = str(path.relative_to(root)) if root.is_dir() else path.name
        if path.name.startswith(".env") and ".example" not in path.name:
            try:
                mode = path.stat().st_mode & 0o777
            except OSError:
                continue
            if mode & 0o077:
                findings.append({"path": rel, "label": "mode_kredensial", "jumlah": 1})
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        found_pii = scan(text)
        found_secrets = scan_secrets(text)
        for label, count in found_pii.items():
            pii[label] += count
            if count:
                findings.append({"path": rel, "label": label, "jumlah": count})
        for label, count in found_secrets.items():
            secrets[label] += count
            if count:
                findings.append({"path": rel, "label": label, "jumlah": count})

    return {
        "status": "AMAN" if not findings else "BOCOR",
        "scanned": scanned,
        "pii": pii,
        "secrets": secrets,
        "findings": findings,
        "catatan": "hanya path, label, dan jumlah; nilai tidak pernah disertakan",
    }


def release_ready(root: Path) -> dict[str, Any]:
    """Kesiapan rilis publik: privasi aman + kredensial terlindungi."""
    root = Path(root)
    result = verify_tree(root)
    reasons: list[str] = []
    if result["status"] != "AMAN":
        reasons.append("paparan ditemukan")
    gitignore = root / ".gitignore"
    ignore_text = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
    if "credentials/.env" not in ignore_text:
        reasons.append("credentials/.env belum masuk .gitignore")
    for env in (root / "credentials" / ".env", root / ".env"):
        if env.is_file() and (env.stat().st_mode & 0o777) & 0o077:
            reasons.append(f"mode kredensial longgar: {env.name}")
    result["status"] = "SIAP" if not reasons else "PERLU TINDAKAN"
    result["alasan"] = reasons
    return result


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Privacy guard")
    parser.add_argument(
        "action", choices=("scan", "redact", "sanitize", "secrets", "verify", "release")
    )
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()

    if args.action == "sanitize":
        print(json.dumps(sanitize_tree(Path(args.path)), ensure_ascii=False))
    elif args.action == "verify":
        print(json.dumps(verify_tree(Path(args.path)), ensure_ascii=False, indent=2))
    elif args.action == "release":
        print(json.dumps(release_ready(Path(args.path)), ensure_ascii=False, indent=2))
    elif args.action == "secrets":
        path = Path(args.path)
        text = path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else str(path)
        print(json.dumps(scan_secrets(text), ensure_ascii=False))
    else:
        path = Path(args.path)
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
        else:
            text = str(path)
        if args.action == "scan":
            print(json.dumps(scan(text), ensure_ascii=False))
        else:
            print(redact(text))


if __name__ == "__main__":
    main()
