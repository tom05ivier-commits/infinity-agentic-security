# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Knowledge base dari seluruh data yang kita punya.

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SOURCES: tuple[str, ...] = (
    "LICENSE",
    "README.md",
    "surat-izin-keamanan.md",
    "surat-kuasa-tandatangan.md",
    "surat-izin-host.md",
    "surat-izin-github.md",
    "surat-izin-konfigurasi-otomatis.md",
    "surat-persetujuan-clone.md",
    "surat-persetujuan-otomatis.md",
    "surat-persetujuan-terbatas.md",
    "STRATEGI-GLOBAL.md",
    "DOCKER.md",
    "DOCTOR_CLI.md",
    "PM_CLI.md",
    "PLATFORM_CLIS.md",
    "Makefile",
    "hosts",
    "config/README.md",
    "security/README.md",
    "system/README.md",
    "agent/README.md",
    "security/reports/verification.json",
    "security/reports/campaign.json",
    "security/firewall/rules.json",
    "agent/state.json",
)


@dataclass(frozen=True)
class Entry:
    """Satu dokumen dalam knowledge base."""

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


def _summarize(text: str) -> tuple[str, tuple[str, ...]]:
    """Ringkasan ringan tanpa membocorkan isi sensitif."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates = [
        line for line in lines
        if not line.startswith(("#", "//", "<!--", "-->"))
        and len(line) > 12
    ]
    summary = (candidates[0] if candidates else (lines[0] if lines else " kosong"))[:180]
    normalized = text.replace("-", " ").replace("/", " ").replace("_", " ")
    words = {
        word.strip(" .,:;()[]{}`*\"'").lower()
        for word in normalized.split()
        if len(word) > 4
    }
    keywords = tuple(sorted(words))
    return summary, keywords


class KnowledgeBase:
    """Indeks dokumen workspace dengan checksum untuk deteksi perubahan."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.entries: dict[str, Entry] = {}

    def refresh(self) -> dict[str, Entry]:
        """Baca ulang semua sumber yang tersedia."""
        self.entries.clear()
        for relative in SOURCES:
            path = self.root / relative
            if not path.is_file():
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            text = data.decode("utf-8", errors="ignore")
            summary, keywords = _summarize(text)
            self.entries[relative] = Entry(
                source=relative,
                checksum=hashlib.sha256(data).hexdigest(),
                size=len(data),
                summary=summary,
                keywords=keywords,
            )
        return self.entries

    def search(self, query: str) -> list[dict[str, Any]]:
        """Cari dokumen berdasarkan kata kunci."""
        if not self.entries:
            self.refresh()
        terms = {term.lower() for term in query.split() if len(term) > 2}
        results: list[tuple[int, Entry]] = []
        for entry in self.entries.values():
            haystack = set(entry.keywords) | {entry.source.lower()}
            score = len(terms & haystack)
            if score:
                results.append((score, entry))
        results.sort(key=lambda item: (-item[0], item[1].source))
        return [entry.to_dict() for _, entry in results]

    def stats(self) -> dict[str, Any]:
        if not self.entries:
            self.refresh()
        return {
            "documents": len(self.entries),
            "total_bytes": sum(entry.size for entry in self.entries.values()),
            "sources": sorted(self.entries),
        }
