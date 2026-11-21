#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pemindai nilai rahasia untuk CI.

Berbeda dengan credential_audit.py yang hanya mencari *nama*, skrip ini
mencari *nilai* yang menyerupai kredensial. Untuk menjaga kerahasiaan,
keluaran hanya memuat path, nomor baris, jenis pola, dan panjang nilai —
tidak ada satu pun karakter dari nilai yang dicetak.
"""

from __future__ import annotations

import math
import os
import re
import sys
from pathlib import Path

ROOTS = [Path(p) for p in (sys.argv[1:] or ["/root/workspace"])]
SKIP_DIRS = {
    ".git", "target", "node_modules", "__pycache__", ".cache", ".rustup",
    ".cargo", "dist", "build", ".playwright-mcp", "opencode-src", "src",
    "site", "chromium", "quarantine", "security/lab",
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".mp4", ".pdf", ".zip", ".woff",
    ".woff2", ".ttf", ".bin", ".so", ".a", ".o", ".pyc", ".sqlite",
}
SKIP_PATH_PARTS = ("docs/", "tests/", "test_", ".example", "secret_scan.py")

HIGH: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
]
GENERIC = re.compile(
    r"(?i)\b(api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|"
    r"private[_-]?key|password|passwd)\b\s*[:=]\s*['\"]([^'\"]{12,})['\"]"
)
MAX_BYTES = 512 * 1024
MAX_FILES = 8000


def entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {c: value.count(c) for c in set(value)}
    return -sum((n / len(value)) * math.log2(n / len(value)) for n in counts.values())


def skip(path: Path) -> bool:
    text = str(path)
    return any(part in text for part in SKIP_PATH_PARTS)


def main() -> int:
    high_hits: list[tuple[str, int, str, int]] = []
    warnings: list[tuple[str, int, str, int]] = []
    scanned = 0

    for root in ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            sources = [(str(root.parent), [], [root.name])]
        else:
            sources = os.walk(root)
        for dirpath, dirnames, filenames in sources:
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if path.suffix.lower() in SKIP_SUFFIXES or path.is_symlink() or skip(path):
                    continue
                try:
                    if not path.is_file() or path.stat().st_size > MAX_BYTES:
                        continue
                except OSError:
                    continue
                scanned += 1
                if scanned > MAX_FILES:
                    break
                try:
                    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
                except OSError:
                    continue
                for lineno, line in enumerate(lines, 1):
                    for label, pattern in HIGH:
                        match = pattern.search(line)
                        if match:
                            high_hits.append((str(path), lineno, label, len(match.group(0))))
                    for match in GENERIC.finditer(line):
                        label, value = match.group(1).lower(), match.group(2)
                        if "${" in value or "{" in value or value.lower() in ("changeme", "placeholder"):
                            continue
                        if len(value) >= 16 and entropy(value) >= 3.6:
                            warnings.append((str(path), lineno, f"high_entropy:{label}", len(value)))
            if scanned > MAX_FILES:
                break
        if scanned > MAX_FILES:
            break

    print("=== Temuan keyakinan tinggi (nilai tidak ditampilkan) ===")
    for path, lineno, label, length in sorted(set(high_hits)):
        print(f"HIGH\t{path}:{lineno}\t{label}\tlen={length}")
    if not high_hits:
        print("(tidak ada)")

    print("=== Indikasi nilai entropi tinggi (peringatan) ===")
    for path, lineno, label, length in sorted(set(warnings)):
        print(f"WARN\t{path}:{lineno}\t{label}\tlen={length}")
    if not warnings:
        print("(tidak ada)")

    print(f"Berkas dipindai: {scanned}")
    print(f"High: {len(set(high_hits))} | Warning: {len(set(warnings))}")
    return 1 if high_hits else 0


if __name__ == "__main__":
    sys.exit(main())
