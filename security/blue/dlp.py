# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Data Loss Prevention — mendeteksi paparan data sensitif, BUKAN mencurinya.

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..common.models import Finding, FindingType, ScanResult, Severity
from ..privacy import redact as redact_private

# Pola generik untuk deteksi paparan. Tidak berisi data milik siapa pun.
SENSITIVE_PATTERNS: list[tuple[str, re.Pattern[str], Severity]] = [
    (
        "kunci privat",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        Severity.CRITICAL,
    ),
    (
        "kredensial tersimpan",
        re.compile(r"(?im)^\s*(password|passwd|pwd|api[_-]?key|secret)\s*[:=]\s*\S+"),
        Severity.HIGH,
    ),
    (
        "alamat email",
        re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        Severity.LOW,
    ),
    (
        "nomor telepon",
        re.compile(r"\b0[0-9]{9,13}\b"),
        Severity.LOW,
    ),
]

_MAX_BYTES = 2 * 1024 * 1024


def scan_file(path: Path) -> ScanResult:
    """Temukan jejak data sensitif pada satu berkas."""
    result = ScanResult(target=str(path))
    try:
        if not path.is_file() or path.stat().st_size > _MAX_BYTES:
            return result
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return result

    result.scanned_items = 1
    for label, pattern, severity in SENSITIVE_PATTERNS:
        match = pattern.search(text)
        if match:
            result.findings.append(
                Finding(
                    finding_type=FindingType.SUSPICIOUS_ACTIVITY,
                    severity=severity,
                    description=f"Paparan data sensitif: {label}",
                    location=str(path),
                    evidence=redact_private(match.group(0))[:40],
                    metadata={"label": label},
                )
            )
    return result


def scan_paths(paths: list[Path]) -> list[ScanResult]:
    """Pindai sekumpulan berkas/direktori."""
    results: list[ScanResult] = []
    for path in paths:
        if path.is_dir():
            results.extend(
                scan_file(child)
                for child in sorted(path.rglob("*"))
                if child.is_file()
            )
        elif path.exists():
            results.append(scan_file(path))
    return results


def quarantine_sensitive(results: list[ScanResult]) -> list[str]:
    """Karantina berkas dengan temuan sensitif tingkat HIGH/CRITICAL."""
    from ..common.config import QUARANTINE_DIR, ensure_dirs
    from ..common.logging import audit, get_logger

    logger = get_logger("blue.dlp")
    ensure_dirs()
    moved: list[str] = []
    for result in results:
        severe = [
            finding
            for finding in result.findings
            if finding.severity.value in ("HIGH", "CRITICAL")
        ]
        if not severe:
            continue
        source = Path(result.target)
        if not source.is_file():
            continue
        target = QUARANTINE_DIR / f"dlp_{source.stem}{source.suffix}"
        counter = 1
        while target.exists():
            target = QUARANTINE_DIR / (
                f"dlp_{source.stem}_{counter}{source.suffix}"
            )
            counter += 1
        try:
            source.replace(target)
        except OSError:
            continue
        moved.append(str(target))
        audit(
            logger,
            "dlp.quarantined",
            source=str(source),
            target=str(target),
            labels=[f.metadata.get("label") for f in severe],
        )
    return moved


def exposure_report(results: list[ScanResult]) -> dict[str, Any]:
    """Ringkas paparan data tanpa menampilkan isi sensitif mentah."""
    labels: dict[str, int] = {}
    for result in results:
        for finding in result.findings:
            label = finding.metadata.get("label", "lainnya")
            labels[label] = labels.get(label, 0) + 1
    return {
        "files_scanned": sum(r.scanned_items for r in results),
        "total_exposures": sum(labels.values()),
        "by_label": labels,
        "note": "Hanya jumlah dan label yang disimpan; nilai data tidak diekstraksi.",
    }
