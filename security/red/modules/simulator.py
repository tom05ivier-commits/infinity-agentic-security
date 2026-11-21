# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Skenario simulasi serangan untuk menguji kontrol pertahanan."""

from __future__ import annotations

import re
from pathlib import Path

from ...common.models import Finding, FindingType, ScanResult, Severity


def weak_config_check(root: Path) -> ScanResult:
    """Temukan konfigurasi lemah di berkas lab (kata sandi jelas, debug)."""
    result = ScanResult(target=str(root))
    patterns = [
        (r"(?im)^\s*password\s*=\s*\S+", "Kata sandi disimpan plaintext"),
        (r"(?im)^\s*debug\s*=\s*true", "Mode debug aktif"),
    ]
    if not root.exists():
        return result
    files = [p for p in root.rglob("*.conf") if p.is_file()]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern, label in patterns:
            match = re.search(pattern, text)
            if match:
                result.findings.append(
                    Finding(
                        finding_type=FindingType.WEAK_CONFIG,
                        severity=Severity.HIGH,
                        description=label,
                        location=str(path),
                        evidence=match.group(0)[:120],
                    )
                )
    result.scanned_items = len(files)
    return result
