#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Menjalankan latihan keamanan lengkap: lindungi hardware → serang lab → respons.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[*] Diagnosis sistem..."
python3 "$ROOT/security/security_cli.py" debug || true

echo "[*] Inisialisasi laboratorium..."
python3 "$ROOT/security/security_cli.py" lab

echo "[*] Latihan penuh..."
python3 "$ROOT/security/security_cli.py" drill

echo "[*] Selesai. Laporan: $ROOT/security/reports/"
