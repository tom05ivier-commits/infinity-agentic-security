# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Simulasi serangan serius pada hardware lokal (terbatas & aman).

Modul ini memberi beban nyata tetapi terukur pada CPU, memori, disk, dan
soket lokal agar kontrol pertahanan dapat diuji terhadap aktivitas mencurigakan.
Semua parameter dibatasi: tidak ada akses jaringan eksternal, tidak ada
penghapusan berkas, dan durasi maksimal 2 detik.
"""

from __future__ import annotations

import os
import socket
import time
from pathlib import Path

from ...common.models import Finding, FindingType, ScanResult, Severity

MAX_DURATION_SECONDS = 2.0
MAX_MEMORY_MB = 16
MAX_FILES = 20
MAX_SOCKETS = 30


def _cpu_burst(duration: float) -> float:
    """Beban CPU terkendali; mengembalikan durasi aktual."""
    start = time.monotonic()
    value = 0
    while time.monotonic() - start < duration:
        value = (value * 6364136223846793005 + 1) & ((1 << 64) - 1)
    return time.monotonic() - start


def _memory_burst(megabytes: int) -> int:
    """Alokasi memori sementara yang langsung dilepas."""
    chunks = []
    allocated = 0
    try:
        for _ in range(megabytes):
            chunks.append(bytearray(1024 * 1024))
            allocated += 1
    except MemoryError:
        pass
    finally:
        chunks.clear()
    return allocated


def _disk_burst(directory: Path, count: int) -> int:
    """Tulis berkas uji kecil ke direktori lab."""
    directory.mkdir(parents=True, exist_ok=True)
    written = 0
    for index in range(count):
        path = directory / f"stress_{index:02d}.tmp"
        try:
            path.write_bytes(os.urandom(512))
            written += 1
        except OSError:
            break
    return written


def _socket_burst(count: int) -> int:
    """Coba koneksi lokal cepat ke port tertutup (tanpa payload)."""
    attempts = 0
    for port in range(45000, 45000 + count):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.01)
        try:
            sock.connect(("127.0.0.1", port))
        except OSError:
            pass
        finally:
            sock.close()
            attempts += 1
    return attempts


def hardware_stress(
    lab_root: Path,
    duration: float = 0.3,
    memory_mb: int = 4,
    file_count: int = 10,
    socket_count: int = 10,
) -> ScanResult:
    """Jalankan beban hardware terkendali dan kembalikan temuannya."""
    duration = min(max(duration, 0.01), MAX_DURATION_SECONDS)
    memory_mb = min(max(memory_mb, 0), MAX_MEMORY_MB)
    file_count = min(max(file_count, 0), MAX_FILES)
    socket_count = min(max(socket_count, 0), MAX_SOCKETS)

    lab_root = Path(lab_root)
    result = ScanResult(target=f"hardware://{lab_root}")
    start = time.monotonic()

    cpu_time = _cpu_burst(duration)
    result.findings.append(
        Finding(
            finding_type=FindingType.SUSPICIOUS_ACTIVITY,
            severity=Severity.HIGH,
            description=f"Beban CPU buatan terdeteksi ({cpu_time:.2f}s)",
            location="cpu",
            metadata={"duration_seconds": round(cpu_time, 3)},
        )
    )

    allocated = _memory_burst(memory_mb)
    if allocated:
        result.findings.append(
            Finding(
                finding_type=FindingType.SUSPICIOUS_ACTIVITY,
                severity=Severity.MEDIUM,
                description=f"Alokasi memori tidak wajar ({allocated} MB)",
                location="memory",
                metadata={"megabytes": allocated},
            )
        )

    written = _disk_burst(lab_root / "stress", file_count)
    if written:
        result.findings.append(
            Finding(
                finding_type=FindingType.SUSPICIOUS_ACTIVITY,
                severity=Severity.MEDIUM,
                description=f"Penulisan berkas massal di lab ({written} berkas)",
                location=str(lab_root / "stress"),
                metadata={"files": written},
            )
        )

    attempts = _socket_burst(socket_count)
    result.findings.append(
        Finding(
            finding_type=FindingType.SUSPICIOUS_ACTIVITY,
            severity=Severity.LOW,
            description=f"Probe soket lokal berulang ({attempts} percobaan)",
            location="127.0.0.1",
            metadata={"attempts": attempts},
        )
    )

    result.scanned_items = 4
    result.metadata = {"elapsed_seconds": round(time.monotonic() - start, 3)}
    return result
