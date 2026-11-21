# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pemindai port TCP jinak untuk pengujian pertahanan lokal.

Hanya melakukan koneksi TCP connect() standar dengan timeout pendek.
Tidak ada pengiriman payload eksploitasi, tidak ada scanning agresif.
"""

from __future__ import annotations

import socket
from pathlib import Path

from ...common.models import Finding, FindingType, ScanResult, Severity


def parse_ports(value: str) -> list[int]:
    """Parse daftar port seperti '22,80,443' atau rentang '1-100'."""
    ports: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            lo, hi = int(start), int(end)
            if lo > hi:
                lo, hi = hi, lo
            ports.update(range(max(1, lo), min(65535, hi) + 1))
        else:
            port = int(part)
            if 1 <= port <= 65535:
                ports.add(port)
    return sorted(ports)


def connect_scan(
    host: str, ports: list[int], timeout: float = 0.25
) -> ScanResult:
    """Lakukan TCP connect scan pada host (digunakan hanya untuk localhost)."""
    result = ScanResult(target=host)
    result.scanned_items = len(ports)
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
        except (OSError, socket.timeout):
            continue
        else:
            result.findings.append(
                Finding(
                    finding_type=FindingType.OPEN_PORT,
                    severity=Severity.LOW,
                    description=f"Port TCP {port} terbuka",
                    location=f"{host}:{port}",
                )
            )
        finally:
            sock.close()
    return result


def scan_lab_files(root: Path) -> ScanResult:
    """Menghasilkan inventaris berkas lab (bukan eksploitasi)."""
    result = ScanResult(target=str(root))
    if root.exists():
        files = [p for p in root.rglob("*") if p.is_file()]
        for path in files:
            result.findings.append(
                Finding(
                    finding_type=FindingType.SUSPICIOUS_ACTIVITY,
                    severity=Severity.INFO,
                    description=f"Berkas lab terlihat: {path.name}",
                    location=str(path),
                )
            )
        result.scanned_items = len(files)
    return result
