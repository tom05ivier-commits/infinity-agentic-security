#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Audit pola penanganan kredensial tanpa pernah menampilkan nilainya.

Skrip hanya mencocokkan *nama* penanda. Untuk berkas mirip .env, yang
dicatat hanyalah nama variabel di sisi kiri tanda '='. Nilai di sisi kanan
tidak diekstrak, tidak disimpan, dan tidak dicetak.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOTS = [Path(p) for p in (sys.argv[1:] or ["/root/workspace", "/root/infinity"])]
SKIP_DIRS = {
    ".git", "target", "node_modules", "__pycache__", ".cache", ".rustup",
    ".cargo", "dist", "build", ".playwright-mcp", "opencode-src", "src",
    "site", "chromium", ".bun", ".npm", ".local", "quarantine",
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".mp4", ".pdf", ".zip", ".woff",
    ".woff2", ".ttf", ".bin", ".so", ".a", ".o", ".pyc", ".sqlite",
}
MARKER = re.compile(
    r"(?i)\b(api[_-]?key|apikey|secret[_-]?key|client[_-]?secret|access[_-]?token|"
    r"refresh[_-]?token|bearer|private[_-]?key|password|passwd|passphrase|"
    r"credential|authorization|auth[_-]?token|session[_-]?token)\b"
)
ENV_ASSIGN = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
MAX_BYTES = 512 * 1024
MAX_FILES = 8000


def is_env_like(path: Path) -> bool:
    return path.name.startswith(".env") or "credentials" in path.parts


def main() -> None:
    findings: set[tuple[str, int, str]] = set()
    env_files: list[tuple[str, str]] = []
    scanned = 0

    for root in ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if path.suffix.lower() in SKIP_SUFFIXES or path.is_symlink():
                    continue
                try:
                    if not path.is_file() or path.stat().st_size > MAX_BYTES:
                        continue
                    mode = oct(path.stat().st_mode & 0o777)
                except OSError:
                    continue
                scanned += 1
                if scanned > MAX_FILES:
                    print(f"[audit] batas {MAX_FILES} berkas tercapai", file=sys.stderr)
                    break
                if is_env_like(path):
                    env_files.append((str(path), mode))
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    match = MARKER.search(line)
                    if not match:
                        continue
                    if is_env_like(path):
                        assign = ENV_ASSIGN.match(line)
                        label = assign.group(1) if assign else match.group(1).lower()
                    else:
                        label = match.group(1).lower()
                    findings.add((str(path), lineno, label))
            if scanned > MAX_FILES:
                break
        if scanned > MAX_FILES:
            break

    print("=== Berkas mirip .env / direktori kredensial (path + mode saja) ===")
    for path, mode in sorted(env_files):
        print(f"{mode}\t{path}")
    if not env_files:
        print("(tidak ada dalam cakupan)")
    print()
    print("=== Penanda kredensial (nama saja; nilai tidak dicetak) ===")
    for path, lineno, label in sorted(findings):
        print(f"{path}:{lineno}\t{label}")
    print()
    print(f"Berkas dipindai: {scanned}")
    print(f"Total penanda: {len(findings)}")


if __name__ == "__main__":
    main()
