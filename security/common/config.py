# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Konfigurasi pusat untuk Infinity Security Suite."""

from __future__ import annotations

import os
from pathlib import Path


def _workspace() -> Path:
    """Root proyek: environment override, atau direktori paket itu sendiri."""
    override = os.environ.get("AGENTY_WORKSPACE")
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[2]


WORKSPACE: Path = _workspace()
SECURITY_ROOT: Path = WORKSPACE / "security"
LAB_ROOT: Path = SECURITY_ROOT / "lab"
QUARANTINE_DIR: Path = SECURITY_ROOT / "quarantine"
LOG_DIR: Path = SECURITY_ROOT / "logs"
SIGNATURE_DIR: Path = SECURITY_ROOT / "blue" / "signatures"
REPORT_DIR: Path = SECURITY_ROOT / "reports"

# Nama variabel lingkungan yang memuat token otorisasi red-team (JSON).
AUTH_TOKEN_ENV: str = "AGENTY_RED_AUTH_TOKEN"

# Target yang diizinkan untuk pengujian ofensif.
ALLOWED_TARGETS: tuple[str, ...] = ("127.0.0.1", "localhost", "::1", "lab")
LAB_TARGET: str = "lab"

# String uji EICAR standar industri untuk memvalidasi mesin antivirus.
EICAR_SIGNATURE: bytes = (
    b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
)


def ensure_dirs() -> None:
    """Buat semua direktori kerja yang dibutuhkan."""
    for directory in (
        SECURITY_ROOT,
        LAB_ROOT,
        QUARANTINE_DIR,
        LOG_DIR,
        SIGNATURE_DIR,
        REPORT_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
