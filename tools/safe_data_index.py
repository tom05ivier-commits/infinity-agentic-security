#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Indeks data lokal yang aman — hanya sumber non-sensitif, selalu offline.

Prinsip (sesuai PANDUAN-OTORISASI-PUBLIK.md dan surat persetujuan otomatis):

* tidak pernah membaca ``credentials/``, berkas ``.env``, ``system/config.env``,
  atau surat/ draf yang memuat data pribadi;
* tidak pernah melakukan aksi jaringan;
* setiap berkas juga dipindai pola kredensial — jika ada penugasan
  ``NAMA=rahasia``, berkas dilewati dan tidak ada nilainya yang disimpan;
* keluaran hanya metadata: path, checksum, ukuran, ringkasan, kata kunci.

Ini bukan pengganti ``advanced.KnowledgeBase``; itu indeks dokumentasi umum,
sedangkan modul ini sengaja dipersempit untuk pemakaian publik.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "safe_data_index.json"

# Hanya direktori ini yang boleh dipindai.
ALLOWED_DIRS: tuple[str, ...] = ("docs", "dataset")
# Berkas root yang boleh ikut.
ALLOWED_FILES: tuple[str, ...] = ("README.md", "LICENSE", "Makefile")

DENIED_PARTS = frozenset(
    {
        ".git", ".env", "credentials", "__pycache__", "node_modules",
        ".cache", "local-data", "inbox", "output", "quarantine",
        "antigravity-cli", "antigravity-sdk-python", "gemini-cli",
    }
)
DENIED_PREFIXES: tuple[str, ...] = (
    "surat-", "DRAF-", "API-KEY", "SERTIFIKAT", ".env", "LICENSE.tom05ivier",
)
DENIED_SUFFIXES = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".mp4", ".pdf", ".zip", ".woff",
     ".woff2", ".ttf", ".bin", ".so", ".a", ".o", ".pyc", ".sqlite"}
)

# Pola penugasan kredensial — hanya untuk MEMUTUSKAN melewati berkas.
# RHS harus literal string/token, bukan panggilan fungsi seperti
# ``secrets = scan_secrets(...)`` (itu kode, bukan kebocoran).
SECRET_ASSIGN = re.compile(
    r"""(?im)^\s*(?:export\s+)?
        (?:[A-Za-z_][A-Za-z0-9_]*
           (?:KEY|TOKEN|SECRET|PASSWORD|PASSPHRASE|CREDENTIAL)
           [A-Za-z0-9_]*)
        \s*=\s*
        (?:['"][^'"]{4,}['"] | [A-Za-z0-9_\-]{8,}\b(?!\())
    """,
    re.VERBOSE,
)
MAX_BYTES = 512 * 1024
TEXT_SUFFIXES = frozenset({".md", ".py", ".json", ".jsonl", ".txt", ".sh", ""})


@dataclass(frozen=True)
class Entry:
    source: str
    checksum: str
    size: int
    summary: str
    keywords: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "checksum": self.checksum[:16],
            "size": self.size,
            "summary": self.summary,
            "keywords": list(self.keywords),
        }


def is_allowed(path: Path) -> bool:
    """Putuskan apakah berkas boleh masuk indeks berdasarkan path saja."""
    relative = path.relative_to(ROOT)
    parts = relative.parts
    if any(part in DENIED_PARTS for part in parts):
        return False
    name = path.name
    if name.startswith(DENIED_PREFIXES):
        return False
    if path.suffix.lower() in DENIED_SUFFIXES:
        return False
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    if len(parts) == 1:
        return name in ALLOWED_FILES
    return parts[0] in ALLOWED_DIRS


def has_secret_assignment(text: str) -> bool:
    return bool(SECRET_ASSIGN.search(text))


def summarize(text: str) -> tuple[str, tuple[str, ...]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates = [
        line for line in lines
        if not line.startswith(("#", "//", "<!--", "-->", "---"))
        and len(line) > 12
    ]
    summary = (candidates[0] if candidates else (lines[0] if lines else "kosong"))[:180]
    normalized = text.replace("-", " ").replace("/", " ").replace("_", " ")
    words = {
        word.strip(" .,:;()[]{}`*\"'").lower()
        for word in normalized.split()
        if len(word) > 4
    }
    return summary, tuple(sorted(words))


def collect(root: Path = ROOT) -> tuple[list[Entry], list[str]]:
    entries: list[Entry] = []
    skipped: list[str] = []
    candidates: list[Path] = []
    for directory in ALLOWED_DIRS:
        base = root / directory
        if base.is_dir():
            candidates.extend(p for p in base.rglob("*") if p.is_file())
    candidates.extend(root / name for name in ALLOWED_FILES if (root / name).is_file())

    for path in sorted(set(candidates)):
        if not is_allowed(path):
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                skipped.append(f"terlalu-besar: {path.relative_to(root)}")
                continue
            data = path.read_bytes()
        except OSError as exc:
            skipped.append(f"gagal-baca: {path.relative_to(root)} ({exc.__class__.__name__})")
            continue
        text = data.decode("utf-8", errors="ignore")
        if has_secret_assignment(text):
            skipped.append(f"mengandung-penugasan-rahasia: {path.relative_to(root)}")
            continue
        summary, keywords = summarize(text)
        entries.append(
            Entry(
                source=str(path.relative_to(root)),
                checksum=hashlib.sha256(data).hexdigest(),
                size=len(data),
                summary=summary,
                keywords=keywords,
            )
        )
    return entries, skipped


def build(root: Path = ROOT, destination: Path = OUTPUT) -> dict[str, Any]:
    entries, skipped = collect(root)
    document = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "offline": True,
        "allowed_dirs": list(ALLOWED_DIRS),
        "allowed_files": list(ALLOWED_FILES),
        "documents": len(entries),
        "total_bytes": sum(entry.size for entry in entries),
        "skipped": skipped,
        "entries": [entry.to_dict() for entry in entries],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return document


def verify(document: dict[str, Any]) -> dict[str, Any]:
    """Pastikan tidak ada path terlarang yang masuk indeks."""
    violations = []
    for entry in document.get("entries", []):
        if not is_allowed(ROOT / entry["source"]):
            violations.append(entry["source"])
        if has_secret_assignment(entry.get("summary", "")):
            violations.append(entry["source"])
    return {
        "ok": not violations,
        "violations": violations,
        "documents": document.get("documents", 0),
    }


def search(document: dict[str, Any], query: str, limit: int = 10) -> list[dict[str, Any]]:
    terms = {term.lower() for term in query.split() if len(term) > 2}
    scored: list[tuple[int, dict[str, Any]]] = []
    for entry in document.get("entries", []):
        haystack = set(entry["keywords"]) | {entry["source"].lower()}
        score = len(terms & haystack)
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda item: (-item[0], item[1]["source"]))
    results = []
    for _, entry in scored[:limit]:
        compact = dict(entry)
        compact["keyword_count"] = len(compact["keywords"])
        compact["keywords"] = compact["keywords"][:8]
        results.append(compact)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="safe_data_index.py", description=__doc__)
    parser.add_argument("command", choices=("build", "stats", "verify", "search"))
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)

    if args.command == "build":
        document = build(destination=args.output)
        print(json.dumps({"documents": document["documents"],
                          "total_bytes": document["total_bytes"],
                          "skipped": document["skipped"]},
                         ensure_ascii=False, indent=2))
    else:
        if not args.output.exists():
            print("Indeks belum ada — jalankan 'build' dulu.", file=sys.stderr)
            return 1
        document = json.loads(args.output.read_text(encoding="utf-8"))
        if args.command == "stats":
            print(json.dumps({"documents": document["documents"],
                              "total_bytes": document["total_bytes"],
                              "generated_at": document["generated_at"],
                              "offline": document["offline"]},
                             ensure_ascii=False, indent=2))
        elif args.command == "verify":
            print(json.dumps(verify(document), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(search(document, args.query), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
