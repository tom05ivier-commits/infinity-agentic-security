# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Mesin antivirus berbasis tanda tangan, hash, dan heuristik ringan.

Tanda tangan yang dipakai adalah EICAR (standar uji industri) dan basis hash
SHA-256 lokal. Heuristik hanya menandai pola mencurigakan untuk ditinjau,
bukan menghapus berkas secara otomatis.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path
from typing import Iterable

from ..common.config import (
    EICAR_SIGNATURE,
    QUARANTINE_DIR,
    SIGNATURE_DIR,
    ensure_dirs,
)
from ..common.logging import audit, get_logger
from ..common.models import Finding, FindingType, ScanResult, Severity

logger = get_logger("blue.antivirus")

# Pola heuristik jinak untuk laboratorium (deteksi, bukan eksekusi).
SUSPICIOUS_PATTERNS: list[tuple[str, str]] = [
    (r"(?i)os\.system\s*\(", "pemanggilan os.system"),
    (r"(?i)subprocess\.(Popen|call|run)\s*\(", "eksekusi subprocess"),
    (r"(?i)base64\.b64decode\s*\(", "dekode base64"),
    (r"(?i)socket\.socket\s*\(", "pembukaan socket"),
    (r"(?i)/dev/tcp/", "reverse shell /dev/tcp"),
    (r"(?i)eval\s*\(", "penggunaan eval"),
]

_MAX_SCAN_BYTES = 32 * 1024 * 1024


class AntivirusAgent:
    """Memindai berkas dan direktori untuk mencari ancaman."""

    def __init__(self, hash_database: Path | None = None) -> None:
        ensure_dirs()
        self.hash_database = hash_database or SIGNATURE_DIR / "malware_hashes.txt"
        self.known_hashes = self._load_hashes()

    def _load_hashes(self) -> set[str]:
        hashes: set[str] = set()
        if not self.hash_database.exists():
            return hashes
        for line in self.hash_database.read_text(encoding="utf-8").splitlines():
            cleaned = line.strip().lower()
            if cleaned and not cleaned.startswith("#"):
                hashes.add(cleaned.split()[0])
        return hashes

    def scan_file(self, path: Path) -> ScanResult:
        """Pindai satu berkas."""
        result = ScanResult(target=str(path))
        try:
            if not path.is_file():
                result.errors.append("Bukan berkas reguler")
                return result
            size = path.stat().st_size
            if size > _MAX_SCAN_BYTES:
                result.errors.append("Berkas terlalu besar untuk dipindai")
                return result
            data = path.read_bytes()
        except OSError as exc:
            result.errors.append(str(exc))
            return result

        result.scanned_items = 1
        digest = hashlib.sha256(data).hexdigest()

        if EICAR_SIGNATURE in data:
            result.findings.append(
                Finding(
                    finding_type=FindingType.SIGNATURE,
                    severity=Severity.CRITICAL,
                    description="Tanda tangan EICAR terdeteksi (berkas uji antivirus)",
                    location=str(path),
                    evidence="EICAR-STANDARD-ANTIVIRUS-TEST-FILE",
                )
            )

        if digest in self.known_hashes:
            result.findings.append(
                Finding(
                    finding_type=FindingType.HASH,
                    severity=Severity.HIGH,
                    description="SHA-256 cocok dengan basis data ancaman lokal",
                    location=str(path),
                    evidence=digest,
                )
            )

        text = data.decode("utf-8", errors="ignore")
        for pattern, label in SUSPICIOUS_PATTERNS:
            match = re.search(pattern, text)
            if match:
                result.findings.append(
                    Finding(
                        finding_type=FindingType.HEURISTIC,
                        severity=Severity.MEDIUM,
                        description=f"Pola mencurigakan: {label}",
                        location=str(path),
                        evidence=match.group(0)[:120],
                    )
                )

        audit(
            logger,
            "av.file_scanned",
            path=str(path),
            findings=len(result.findings),
            sha256=digest[:16],
        )
        return result

    def scan_directory(
        self, root: Path, recursive: bool = True
    ) -> list[ScanResult]:
        """Pindai seluruh berkas dalam direktori."""
        if not root.exists():
            audit(logger, "av.dir_missing", path=str(root))
            return []
        iterator: Iterable[Path] = (
            root.rglob("*") if recursive else root.glob("*")
        )
        results = [
            self.scan_file(path) for path in iterator if path.is_file()
        ]
        audit(
            logger,
            "av.dir_scanned",
            path=str(root),
            files=len(results),
        )
        return results

    def quarantine(self, path: Path) -> Path | None:
        """Pindahkan berkas terinfeksi ke direktori karantina."""
        ensure_dirs()
        if not path.is_file():
            return None
        target = QUARANTINE_DIR / f"{path.stem}.quarantined{path.suffix}"
        counter = 1
        while target.exists():
            target = QUARANTINE_DIR / (
                f"{path.stem}.quarantined{counter}{path.suffix}"
            )
            counter += 1
        try:
            shutil.move(str(path), str(target))
        except OSError:
            # Daemon proteksi bisa memindahkan berkas lebih dulu (race).
            # Anggap berhasil bila sumber sudah tidak ada.
            if path.exists():
                return None
            audit(logger, "av.quarantine_race", source=str(path))
            return None
        audit(logger, "av.quarantined", source=str(path), target=str(target))
        return target
